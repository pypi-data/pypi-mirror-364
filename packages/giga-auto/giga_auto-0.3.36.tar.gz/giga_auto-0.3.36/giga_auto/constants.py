import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_DIR = os.path.join(BASE_DIR, "giga_auto", "config")

class DBType:
    oracle = 'oracle'
    mysql = 'mysql'
    sqlserver = 'sqlserver'
    mongodb = 'mongodb'
    redis = 'redis'


class CaseTypeEnum:
    """
    - 'emptyFilter' 空筛选项查询
    - 'exactMatch' 精确查询
    - 'fuzzySearch' 模糊查询
    - 'defaultQuery' 默认查询
    - 'emptyResult' 空结果查询
    - 'timeRange' 查询创建时间范围
    """
    emptyFilter = 'emptyFilter'
    exactMatch = 'exactMatch'
    fuzzySearch = 'fuzzySearch'
    defaultQuery = 'defaultQuery'
    emptyResult = 'emptyResult'
    timeRange = 'timeRange'
    multiSelect = 'multiSelect'  # 多选查询

# 未认证状态
UNAUTHORIZED = 401
# 从api以及business拿到的service可能是公共service，如wms_common_web对应wms_uk_web、wms_jp_web、wms_de_web，
# 需要给common service对应的实际service分配对应api及business
SERVICE_MAP='SERVICE_MAP'