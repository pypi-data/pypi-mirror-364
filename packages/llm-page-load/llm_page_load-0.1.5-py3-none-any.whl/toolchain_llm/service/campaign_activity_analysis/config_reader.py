import configparser
from langchain import PromptTemplate
from service.lang_chain_utils.lion_client import client as lion
import re
from typing import List, Union, Dict
from flask_socketio import emit
from kms_sdk.kms import KmsResultNullException, Kms
from utils import logger, appkey
campaign_config = configparser.ConfigParser()
campaign_config.read('config/campaign_activity_analysis.conf', encoding='utf-8')


def get_config(key: str, field_name: str = 'test'):
    return campaign_config[field_name][key]


def get_kms(key):
    '''部分config文件中的内容放入kms中去了'''
    try:
        return Kms.get_by_name(appkey, key)
    except KmsResultNullException as e:
        logger.exception('kms获取失败:'+e.msg)
    except Exception as e:
        logger.exception(e.args)


CAMPAIGN_PREFIX = 'campaign_activity'
OPENAI_API_BASE = get_config('OPENAI_API_BASE', 'model')
# OPENAI_API_KEY = get_config('OPENAI_API_KEY', 'model')
OPENAI_API_KEY = get_kms('FRIDAY_APPID')

NameSpace = '/campaign/activity'


def on_emit(event: str, message: Union[List, Dict, str]):
    '''
    向前端发送请求，这里指定向当前namespace发送请求
    emit函数会通过 flask.request.sid / flask.session.get('session_id')来确定长链接，此处不会发生广播
    '''
    try:
        emit(event, message, namespace=NameSpace)
    except Exception as e:
        logger.exception(e.args)


def get_prompt(type, template) -> PromptTemplate:
    lion.fetch_config()
    pattern = r'\{([a-zA-Z_0-9\-]+)\}'
    text = lion.config[f'{lion.app_name}.{CAMPAIGN_PREFIX}.{type}.{template}']
    variables = re.findall(pattern, text)
    return PromptTemplate(template=text, input_variables=variables)


def get_lion_config(path):
    lion.fetch_config()
    return lion.config[f'{lion.app_name}.{CAMPAIGN_PREFIX}.{path}']


def get_model_config():
    lion.fetch_config()
    output_dict = {}
    a = ''
    a.split()
    for key, value in lion.config.items():
        if key.startswith(f'{lion.app_name}.{CAMPAIGN_PREFIX}.model.'):
            param = key.split('.')[-1]
            output_dict[param] = value
    return output_dict


if __name__ == '__main__':
    print(get_prompt('stacking', 'system'))
