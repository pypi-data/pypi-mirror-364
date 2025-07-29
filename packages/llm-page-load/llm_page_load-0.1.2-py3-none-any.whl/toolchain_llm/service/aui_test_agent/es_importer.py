from llmcore_sdk.data_connection.es_client import LLMElasticsearchClient
import os
from service.file_config_reader import read_lion_file_config
ES_ENV = os.getenv('ES_ENV', 'default')
config = read_lion_file_config('es_client.conf')

accesskey = config[ES_ENV]['accesskey']
appkey = config[ES_ENV]['appkey']
is_online_env = config[ES_ENV]['isOnlineEnv'] == 'true'
es_util = LLMElasticsearchClient(accesskey=accesskey, appkey=appkey, is_online_env=is_online_env)

RECORDED_INSTRUCTION_WEB_INDEX = 'recorded_instruction_web'
SOCKET_STORAGET_INDEX = 'socket_storaget_index_1'
