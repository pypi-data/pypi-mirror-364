
import logging

import allure

from giga_auto.assert_class.date_assert import AssertDete
from giga_auto.utils import to_date

from giga_auto.expect_utils import ExpectUtils

from giga_auto.constants import CaseTypeEnum

from giga_auto.assert_class.common_assert import AssertCommon
from giga_auto.assert_class.container_assert import AssertContainer


from giga_auto.assert_class.excel_assert import AssertExcel
from giga_auto.assert_class.string_assert import AssertString

from giga_auto.base_class import SingletonMeta
from giga_auto.expect_utils import ExpectUtils



logger = logging.getLogger('giga')

class ListQueryValidator:

    @staticmethod
    def validate(scene_type, response, expect=None, payload=None,
                 data=None, records=None, total=None):
        """
        通用列表查询验证入口
        :param scene_type: 场景类型
            - 'emptyFilter' 空筛选项查询
            - 'exactMatch' 精确查询
            - 'fuzzySearch' 模糊查询
            - 'emptyResult' 空结果查询
            - 'timeRange' 查询创建时间范围
        :param response: 接口响应字典
        :param expect: 预期值配置
                value: 需要验证的值/字段
                total: 预期总数
                startTime: 开始时间（仅对查询创建时间有效）
                endTime: 结束时间（仅对查询创建时间有效）
        :param payload: 请求参数（模糊查询需传递）
        :param payload: 判断是否为时间范围查询
        :param data: 响应数据字典，默认为response中的data
        :param records: 响应记录列表，默认为response中的records
        :param total: 响应总数，默认为response中的total
        """
        data = data or response.get('data', {})
        records = records or data.get('records', []) or data.get('data', [])
        total = total or data.get('total', 0)
        strategies = {
            CaseTypeEnum.emptyFilter: lambda: ListQueryValidator._validate_empty_filter(records, total, expect),
            CaseTypeEnum.exactMatch: lambda: ListQueryValidator._validate_exact_match(records, total, expect, payload),
            CaseTypeEnum.fuzzySearch: lambda: ListQueryValidator._validate_fuzzy_search(records, expect, payload),
            CaseTypeEnum.emptyResult: lambda: ListQueryValidator._validate_empty_result(records, total),
            CaseTypeEnum.timeRange: lambda: ListQueryValidator._validate_time_range(records, expect, payload),
            CaseTypeEnum.multiSelect: lambda: ListQueryValidator._assert_multi_select(records, expect, payload),
        }
        if scene_type not in strategies:
            raise ValueError(f"未知的场景类型: {scene_type}")
        return strategies[scene_type]()

    @staticmethod
    def _expected_fields(expect, payload, key='checkValueField'):
        """
        获取checkValueField字段
        :return:
        yaml配置示:
        expect:
            checkValueField:  #检查值不为空字段key
                - text
                - value
        当checkValueField字段值为'&payload'时，表示使用payload中的字段:示例如下：
        expect:
            checkValueField: &payload
        """
        check_value_field = expect.get(key, {})
        # 兼容精确匹配时入参和返回值字段完全一致的场景,无需额外定义一遍checkValueField
        if check_value_field == '&payload':
            check_value_field = payload
        return check_value_field

    @staticmethod
    def _validate_empty_filter(records, total, expect):
        """空筛选项验证
        yaml配置示例:
        expect:
            checkValueField:  #检查值不为空字段key
                - text
                - value
            checkField: #检查key存在,value允许为空
                - remark
                - relationOrder
        """
        assert records, "空筛选项查询结果不能为空"
        AssertCommon.assert_true(total > 0, "空筛选项查询结果应大于0")
        check_value_field = expect.get('checkValueField', [])  # 需要检查值不为空字段key
        check_field = expect.get('checkField', [])
        assert check_value_field or check_field, "空筛选项查询需配置至少一个检查字段"
        if check_value_field:
            ExpectUtils.assert_fields(records[0], check_value_field, check_value=True, subset=True,
                                      msg=f"空筛选项查询结果字段不符")
        if check_field:
            ExpectUtils.assert_fields(records[0], check_field, check_value=False, subset=True,
                                      msg=f"空筛选项查询结果字段不符")

    @staticmethod
    def _validate_exact_match(records, total, expect, payload=None):
        """精确匹配验证(输入参数的查询)
        """
        expected_total = expect.get('total', 1)
        # 校验总数,如果预期总数为-1表示不定长，则不进行校验
        if int(expected_total) != -1:
            AssertCommon.assert_equal(total, expected_total, "精确查询总数不符")
            AssertCommon.assert_equal(len(records), expected_total, "返回记录数不符")
        else:
            AssertCommon.assert_greater(total, 0, "精确查询结果不能为空")
            AssertCommon.assert_greater(len(records), 0, "返回记录数不符")
        # 获取期待值
        expected_equal_fields = ListQueryValidator._expected_fields(expect, payload)
        expected_grater_fields = ListQueryValidator._expected_fields(expect, payload, key='checkGraterField')
        expected_less_fields = ListQueryValidator._expected_fields(expect, payload, key='checkLessField')
        assert expected_equal_fields or expected_grater_fields or expected_less_fields, "精确查询需配置至少一个检查字段"
        for record in records:
            for field, expected_value in expected_equal_fields.items():
                AssertCommon.assert_equal(record.get(field), expected_value, f"字段 {field} 值不匹配")

            for field, expected_value in expected_grater_fields.items():
                AssertCommon.assert_greater(record.get(field), expected_value, f"字段 {field} 值不匹配")

            for field, expected_value in expected_less_fields.items():
                AssertCommon.assert_less(record.get(field), expected_value, f"字段 {field} 值不匹配")

    @staticmethod
    def _validate_fuzzy_search(records, expect, payload=None):
        """模糊查询验证"""
        # 获取期待值
        expected_fields = ListQueryValidator._expected_fields(expect, payload)
        # 校验总数
        AssertCommon.assert_greater(len(records), 0, "模糊查询结果不能为空")
        # 遍历所有记录进行校验
        for record in records:
            for field, value in expected_fields.items():
                actual_value = str(record.get(field, ''))
                AssertCommon.assert_in(str(value), actual_value, f"模糊匹配失败,字段: {field} ")

    @staticmethod
    def _validate_empty_result(records, total):
        """空结果验证"""
        assert total in [0, None], f"空结果总数应等于0或者null, 当前值: {total}"
        assert records in [[], None], f"记录列表应为空，或者为null, 当前值: {records}"

    @staticmethod
    def _validate_time_range(records, expect, payload):
        """创建时间范围验证
        time_key: 时间范围字段名列表，默认['startTime', 'endTime']
        为了支持时间独立查询或者组合查询，yaml中expect断言时间单独配置checkDateTime。
        如checkDateTime和payload一直,则直接使用payload中的时间字段进行断言。
        yaml配置示例:
        expect:
            checkDateTime:
                startTime: 2023-10-01 00:00:00  #如果使用payload中的时间字段，
                endTime: 2023-10-31 23:59:59
            timeField: createTime
        #支持直接校验payload中的时间字段
         expect:
            checkDateTime: $payload
            timeField: createTime
        """

        check_date_fields = ListQueryValidator._expected_fields(expect, payload, 'checkDateTime')
        time_range = check_date_fields.values()
        time_field = expect.get('timeField')
        assert time_range, "时间范围字段不能为空"
        assert time_field, "需要校验的时间字段不能为空"

        # 将时间字符串转换为 datetime 对象，为了确认时间大小
        datetime_range = [to_date(time_value) for time_value in time_range]

        # 判断datetime_range中的两个时间大小,分别赋值为start_time 和end_time
        if datetime_range[0] > datetime_range[1]:
            datetime_range[0], datetime_range[1] = datetime_range[1], datetime_range[0]

        start_time, end_time = datetime_range

        # 3. 遍历记录并验证时间范围
        for record in records:
            # 获取记录中的时间字段值
            time_field_str = record.get(time_field)
            if not time_field_str:
                raise ValueError(f"接口返回缺少字段 '{time_field}'")
            # 将记录时间转为 datetime 对象
            record_time = to_date(time_field_str)
            # 4. 调用断言方法（传递 datetime 对象）
            AssertDete.assert_time_range(start_time, end_time, record_time, '时间范围不符')

    @staticmethod
    def _assert_multi_select(records, expect, payload):
        """
        多选断言
        expect:
            checkValueField:
              adjustSource: ['1','2','3'] #接口返回的字段值，value是需要断言的值，
              buyerInfo: ['LssApp自动化账号他人禁用(83635502)', '上门取货-自动化003(87478099)']
        """
        check_value_field = ListQueryValidator._expected_fields(expect, payload)
        for field, expected_values in check_value_field.items():
            actual_values = [str(r[field]) for r in records]
            AssertUtils.assert_in(actual_values, expected_values, msg={field: actual_values})

    @staticmethod
    def _assert_init_api(resp_data, expect, key_exist_list=None):
        """
        通用初始化接口响应校验
        :param resp_data: 接口返回结果
        :param expect: 预期值字典，包含 checkList、keyExistList、自定义key
        :param key_exist_list: 需要断言存在的key 列表
        """

        key_exist_list = ['value', 'text'] if key_exist_list is None else key_exist_list

        # 校验字段存在性（不校验值）
        check_list = expect.get('checkList', [])
        # 校验字段值是否完全一致
        check_value_list = expect.get('checkValueList', {})
        assert any([check_value_list,check_value_list]), "至少需要配置checkList或checkValueList"
        for field in check_list:
            ExpectUtils.assert_fields(resp_data[field][0], key_exist_list, subset=True, check_value=True)

        for key in check_value_list.keys():
            expect_list = check_value_list[key]
            actual_list_origin = resp_data.get(key)
            actual_list = [
                {k: obj.get(k) for k in key_exist_list} for obj in actual_list_origin
            ]
            AssertUtils.assert_equal(actual_list, expect_list)


class AssertUtils(AssertExcel,AssertCommon,AssertContainer,AssertDete,AssertString,ExpectUtils,ListQueryValidator,metaclass=SingletonMeta):
    compare_map = {
        'eq': 'assert_equal', 'gt': 'assert_greater', 'ge': 'assert_greater_equal',
        'lt': 'assert_less', 'le': 'assert_less_equal', 'ne': 'assert_not_equal',
        'in': 'assert_in', 'not_in': 'assert_not_in', 'length': 'assert_length',
        'iter': 'assert_iter', 'ac': 'assert_contains','ac_ig': 'assert_contains_ignore_case',
    }

    @staticmethod
    def assert_iter(actual: list, expected, assert_method='assert_equal',key=None):
        """
        :params : 遍历列表数据，默认断言是否与期望相等，可以传in、ne等
        """
        for item in actual:
            if key:
                assert_method(item[key], expected)
            else:
                assert_method(item, expected)

    def get_assert_method(self, key):
        """
        如果是映射关键字，去compare_map里获取方法名，获取不到则证明本身就是方法名
        :params key: eq,assert_equal等
        """
        method_key = self.compare_map.get(key, key)
        logger.info(f'获取断言方法，断言关键字:{key},断言方法:{method_key}')
        return getattr(self, method_key)

    def map_assert_method(self, key: str):
        """
        判断是否组合断言，
        """

        if '__' in key:
            compare, value = key.split('__')
            logger.info(f'获取方法:{compare},{value}')
            compare, value = self.get_assert_method(compare), self.get_assert_method(value)
            return compare, value
        return self.get_assert_method(key)

    def _validate(self, validates):
        for val in validates:
            for k, v in val.items():
                actual, expected, *others = v
                methods = self.map_assert_method(k)
                logger.info(f'断言关键字:{k}获取断言方法成功,actual:{actual},expected:{expected}')
                allure.attach(f'断言关键字:{k}获取断言方法成功,actual:{actual},expected:{expected}', '开始断言')
                if isinstance(methods, tuple):
                    methods[1](actual, expected, methods[0], *others)
                else:
                    methods(actual, expected, *others)
                    
    def condition(self,validates):
        try:
            self._validate(validates)
            return True
        except:
            return False
    


