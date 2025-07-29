from llmcore_sdk.data_connection.es_client import LLMElasticsearchClient
import os
from service.file_config_reader import read_lion_file_config
ES_ENV = os.getenv('ES_ENV', 'default')
config = read_lion_file_config('es_client.conf')

accesskey = config[ES_ENV]['accesskey']
appkey = config[ES_ENV]['appkey']
is_online_env = config[ES_ENV]['isOnlineEnv'] == 'true'
es_client = LLMElasticsearchClient(
    accesskey=accesskey, appkey=appkey, is_online_env=is_online_env)

client = es_client.client
headers = es_client.headers
ActivityRuleIndex = 'campaign_rule'
TreeNodeIndex = 'campaign_test_case_tree_node'
TaskIndex = 'campaign_test_case_generation_task'
EntityIndex = 'campaign_activity_entity'
