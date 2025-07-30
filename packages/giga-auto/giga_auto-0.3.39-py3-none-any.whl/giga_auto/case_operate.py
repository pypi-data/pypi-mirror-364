import os.path
from collections import defaultdict

import requests
from giga_auto.conf.settings import settings
from giga_auto.constants import CAL_API_FILE
from giga_auto.yaml_utils import YamlUtils



class CaseOperator():

    def __init__(self):
        self.send_wechat = False
        self.failed_tests = defaultdict(set)
        self.successful_tests = set()
        self.failed_models = defaultdict(set)
        self.package_stats = defaultdict(lambda: {'total': 0, 'passed': 0, 'failed': 0, 'skipped': 0})


    @staticmethod
    def get_marker(item, mark_name):
        """
        获取测试用例的标签
        """
        for marker in item.parent.own_markers:
            if mark_name in marker.name:
                return marker.args[0]
        return None

    def send_failure_notification(self):
        def _send(owner, fail_case):
            message = {
                "msgtype": "text",
                "text": {
                    "content": f"{owner},你有{len(fail_case)}条测试用例失败\n失败用例模块:{list(self.failed_models[owner])}",
                    "mentioned_list": [owner]  # @相关负责人
                }
            }
            requests.post(settings.admin_config['webhook_url'], json=message)

        if self.send_wechat:
            for owner, fail_case in self.failed_tests.items():
                if fail_case:
                    _send(owner, fail_case)


    def cal_fail_case(self,item, report):
        case_name = f"{report.when}_{item.name}"
        # 如果用例已经标记为失败，且最终成功，则移除失败记录
        owner = self.get_marker(item, 'owner')
        # 检查是否是失败的测试用例
        if 'test_' in item.name and report.failed:
            if self.send_wechat:
                if owner:
                    feature = self.get_marker(item, 'feature')
                    self.failed_tests[owner].add(case_name)
                    self.failed_models[owner].add(feature)

        # 检查用例是否最终成功（避免重复统计）
        if 'test_' in item.name and report.passed:
            if self.failed_tests.get(owner) and case_name in self.failed_tests.get(owner):
                self.failed_tests[owner].remove(case_name)
                # 如果该owner下没有其他失败用例，则从failed_models中移除
                if len(self.failed_tests[owner]) == 0:
                    del self.failed_tests[owner]
                # 移除成功的用例，避免再次统计
                self.successful_tests.add(case_name)


    def cal_case_num(self,item, call,service=None):
        """
        统计测试用例数量
        """
        # 只有在调用阶段（测试用例执行时）才需要收集结果
        if call.when == 'call':
            # 获取包名或模块路径
            package_name = item.nodeid.split('testcases/')[1].split('/')[0] if not service else service
            # 统计每个包的测试用例数量
            self.package_stats[package_name]['total'] += 1

            # 根据执行结果进行分类统计
            if call.excinfo is None:  # 如果没有异常，则表示通过
                self.package_stats[package_name]['passed'] += 1
            elif call.excinfo and 'skipped' in str(call.excinfo):  # 如果是跳过
                self.package_stats[package_name]['skipped'] += 1
            else:  # 否则，视为失败
                self.package_stats[package_name]['failed'] += 1


    def write_case_num(self):
        """
        输出测试用例数量
        """
        package_stats_dict = {
            package: {
                "case_num":stats
            }
            for package, stats in self.package_stats.items()
        }
        YamlUtils(os.path.join(settings.Constants.BASE_DIR, CAL_API_FILE), False).update(**package_stats_dict)


case_operator = CaseOperator()