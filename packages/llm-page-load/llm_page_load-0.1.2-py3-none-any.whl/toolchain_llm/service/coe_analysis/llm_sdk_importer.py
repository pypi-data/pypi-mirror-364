import json

from llmcore_sdk.data_connection.es_client import LLMElasticsearchClient
import os
from service.file_config_reader import read_lion_file_config
from service.lang_chain_utils.lion_client import client as lion
ES_ENV = os.getenv('ES_ENV', 'default')
config = read_lion_file_config('es_client.conf')

accesskey = config[ES_ENV]['accesskey']
appkey = config[ES_ENV]['appkey']
is_online_env = config[ES_ENV]['isOnlineEnv'] == 'true'
es_util = LLMElasticsearchClient(accesskey=accesskey, appkey=appkey, is_online_env=is_online_env)

COE_CRAWLER_DATA = 'coe_crawler_data'
COE_ANALYSIS_EXPERIENCE = 'coe_analysis_experience'
COE_ANALYSIS_TASK = 'coe_analysis_task'
COE_ANALYSIS_DETAIL = 'coe_analysis_detail'
COE_SYNC_DATA = 'coe_sync_data'

lion.fetch_config()
agent_name_mapping = lion.config.get(f'{lion.app_name}.agent_name_mapping')
agent_name_mapping_dict = json.loads(agent_name_mapping)

TASK_TYPES = [{"title": title, "type": key} for key, title in agent_name_mapping_dict.items()]

# 以下内容配置化，作为副本保留
# TASK_TYPES = [
#     {"title": '问题原因标签分析', "type": 'cause_analysis'},
#     {"title": "技术债务标签分析", 'type': 'debt_label'},
#     {"title": "TODO智能分析", 'type': 'todo_analysis'},
#     {"title": "线上监控未发现原因分析", 'type': 'monitor_online_analysis'},
#     # {"title": '要测试', 'type': 'to_test'},
#     # {"title": '要周知', 'type': 'to_claim'},
#     # {"title": '要审核', 'type': 'to_check'},
#     # {"title": '要灰度', 'type': 'to_grey'},
#     # {"title": '要观测', 'type': 'to_inspect'},
#     # {"title": '要可回滚', 'type': 'to_rollback'},
#     # {"title": '不要延报故障', 'type': 'not_to_delay'},
#     # {"title": '不要违规变更数据', 'type': 'not_to_illagle_change_data'},
#     # {"title": '字段异常', 'type': 'null_check'},
#     # {"title": '资金计算准确问题', 'type': 'fund_acc'},
#     # {"title": '优惠价格问题', 'type': 'fund_activity_save'},
#     # {"title": '规则安全问题', 'type': 'rule_safety'},
#     # {"title": '线上问题触发条件', 'type': 'trigger_condition'},
#     # {"title": '是否资金安全', 'type': 'fund_judgement'},
#     {"title": "风险助手分析", 'type': 'risk_assistant_analysis'},
#     {"title": "测试是否可发现分析", 'type': 'qa_test_analysis'},
#     {"title": "聚合分析", "type": "aggr_simple"},
#     {"title": '资金问题分类', 'type': 'fund_aggr_classify'},
#     {"title": "自定义判断", 'type': 'determinate_search'},
#     {"title": 'COE原因分类', "type": 'cause'},
#     {"title": '测试调式', 'type': 'new_analysis'}
# ]


def is_type_regietered(type):
    for t in TASK_TYPES:
        if type == t['type']:
            return True
    return False


RESULT_FILTER_WHITE_LIST = [
    {
        'types': ['cause'],
        'match': ['需求问题', '技术设计', '代码逻辑', '配置问题', '数据存储', '服务上下游协同问题', '上线流程', '线上环境操作不当',
                  '性能问题', '基础架构', '基础设施', '外部依赖', '第三方问题', '安全问题']
    },
    {
        'types': ['to_test', 'to_claim', 'to_check', 'to_grey', 'to_inspect', 'to_rollback', 'not_to_delay',
                  'not_to_illagle_change_data'],
        'match': ['违反', '无法确定', '是', '涉及']
    }
]

NameSpace = '/coe'
