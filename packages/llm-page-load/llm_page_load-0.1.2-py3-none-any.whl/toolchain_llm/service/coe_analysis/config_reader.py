import configparser
from kms_sdk.kms import Kms
from kms_sdk.utils.exceptions import KmsResultNullException
import time
from src.toolchain_llm.utils import logger, appkey
coe_config = configparser.ConfigParser()
coe_config.read('config/coe_server.conf', encoding='utf-8')


def get_config(key: str, field_name: str = 'test'):
    return coe_config[field_name][key]


KMS_CACHE = {}


def get_kms(key):
    '''部分config文件中的内容放入kms中去了'''
    if key in KMS_CACHE:
        if time.time() - KMS_CACHE[key]['time'] > 300:
            value = Kms.get_by_name(appkey, key)
            KMS_CACHE[key] = {
                "value": value, 'time': time.time()
            }
        return KMS_CACHE[key]['value']
    try:
        value = Kms.get_by_name(appkey, key)
        KMS_CACHE[key] = {
            "value": value, 'time': time.time()
        }
        return value
    except KmsResultNullException as e:
        logger.exception('kms获取失败:'+e.msg)
    except Exception as e:
        logger.exception(e.args)


OPENAI_API_BASE = get_config('OPENAI_API_BASE', 'model')
OPENAI_API_KEY = get_kms('FRIDAY_APPID')


COE_ACCESS_TOKEN = get_kms('COE_ACCESS_TOKEN')   # 到店申请的token
# token = get_config('token')
# youxuan_token = get_config('youxuan_token')   # 优选申请的token
COE_ACCESS_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_0_0) " +\
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36"
COE_ACCESS_HEADER = {
    "Authorization": "Bearer %s" % COE_ACCESS_TOKEN,
    "User-Agent": COE_ACCESS_AGENT,
}
COE_API_HOST = get_config('COE_API_HOST')
DEFAULT_AGGR_COEID_PLACEHOLDER = "-2"


llmapp_s3_access_key = get_kms('llmapp_s3_access_key')
llmapp_s3_s_key = get_kms('llmapp_s3_s_key')

friday_client_id = get_kms('friday_client_id')
friday_client_secret = get_kms('friday_client_secret')
