from flask import jsonify
from flask import request
from flask import Blueprint
from service.promot_base import PromptBase
from service.GPT import create_conversation, llmcore_completion
from tools.oceanus_auth import get_oceanus_auth_header
import threading
import json
import requests
import os
from utils import GPT35NAME, logger, appkey
import traceback
from token_count.tokenizer import count_token
from service.lang_chain_utils.lion_client import client_prod as lion

MACHINE_ENV = os.environ.get('Env')

impact_analysis = Blueprint('impact-analysis', __name__)


@impact_analysis.route('', methods=['POST'])
def get_conversation_result():
    logger.info(f'[impact_analysis] input = {request.json}')
    resp = {
        "code": 0, "msg": "",
        "data": {"success": True, "url": "", "returnImmediately": False, "decisionName": "", "decisionMsg": ""}
    }
    payload = request.json
    execute_id = payload.get('executeId', '')
    context = payload.get('context', '')
    set_param = context.get('requestParameters', {}).get('SET')
    if set_param and 'ptest' in set_param:
        decision = 'access'
        result = '在ptest环境发布的配置变更，用于线下验证，不再进行LLM风险预检'
        mcm_call(decision, result, execute_id)
        return jsonify(resp)

    business_app_key = context.get('eventSourceAppkey', '')
    value_new = context.get('requestParameters', {})\
        .get('new', {}).get('value', '')
    key_new = context.get('requestParameters', {})\
        .get('new', {}).get('key', '')
    key_type_new = context.get('requestParameters', {})\
        .get('new', {}).get('type', '')
    value_old = context.get('requestParameters', {})\
        .get('old', {}).get('value', '')
    key_type_old = context.get('requestParameters', {})\
        .get('old', {}).get('type', '')
    key_old = context.get('requestParameters', {})\
        .get('old', {}).get('key', '')
    desc = context.get('requestParameters', {})\
        .get('new', {}).get('config', {}).get('desc', '')
    desc = desc.split("\n【关联需求】")[0].strip() if desc != '' else ''
    affectAppkeyNum = max(context.get('requestParameters', {}).get('affectAppkeyNum', 1), 1)

    if key_new and key_old:
        action = 'modify'
        content = f"""{{
            key:{key_old},
            type: {key_type_new}
            value_before:{value_old},
            value_after: {value_new},
            affectModuleNum:{affectAppkeyNum},
            desc:{desc}
        }}"""
    elif key_new:
        action = 'add'
        content = f"""{{
            key:{key_new},
            type: {key_type_new}
            value: {value_new},
            affectModuleNum:{affectAppkeyNum},
            desc:{desc}
        }}"""
    else:
        action = 'delete'
        content = f"""{{
            key:{key_old},
            type: {key_type_old}
            value: {value_old},
            affectModuleNum:{affectAppkeyNum},
            desc:{desc}
        }}"""
    
    thread = threading.Thread(target=get_completion_result, args=(content, action, execute_id, business_app_key))
    thread.start()
    return jsonify(resp)


def get_completion_result(msg, action, execute_id, business_app_key):
    token_len = 0
    try:
        token_len = count_token(msg)
        if is_appkey_in_blacklist(business_app_key):
            decision = 'access'
            result = '该appkey下的lion配置变更视为低风险，不再进行LLM风险预检'
        elif token_len > 10000:
            decision = 'access'
            result = '风险等级：低，原因：识别到超长文本，此类较大规模的配置变更一般与业务逻辑无关，不会影响代码的功能和行为。'
        else:
            model = GPT35NAME
            content = msg
            completion_result = llmcore_completion(create_conversation(PromptBase.impact_analysis, content, ACTION=action),
                                                   business='impact_analysis', model=model)
            result = completion_result
            result_list = [l for l in result.split('\n') if len(l) > 1]
            decision = 'access' if 'low' in result_list[0].lower() else 'warning'
            completion_result = llmcore_completion(create_conversation(PromptBase.translate_cn, result),
                                                   business='impact_analysis', model=model)
            result = completion_result
            result = result.replace("\n", "，").replace("，，", "，").replace("：，", "：")
    except Exception as e:
        decision = 'access'
        result = '服务跳过'
        logger.info(traceback.format_exc())

    logger.info(f'[impact_analysis] execute_id = {execute_id}, decision= {decision}, result = {result}, length of token = {token_len}')
    mcm_call(decision, result, execute_id)

def mcm_call(decision, result, execute_id):
    url = 'https://mcm.vip.sankuai.com/api/v2/cf/callback/thirdparty' if MACHINE_ENV == 'prod' \
        else 'http://mcm.tbd.test.sankuai.com/api/v2/cf/callback/thirdparty'
    auth = get_oceanus_auth_header("com.sankuai.cf.rule.server", appkey)
    headers = {'Content-Type': 'application/json'}
    headers.update(auth)
    result = result + "如有问题请联系 baihan,yangfan100"
    payload = {
        'executeId': execute_id,
        'decisionName': decision,
        'decisionMsg': result,
        'errMsg': '',
        'url': ''
    }
    response = requests.post(url, data=json.dumps(payload), headers=headers)
    logger.info(f'[impact_analysis] result = {response.text}')


def is_appkey_in_blacklist(business_app_key):
    lion.fetch_config()
    appkey_blacklist = json.loads(lion.config.get(f'{lion.app_name}.impact_analysis.appkey_blacklist', '[]'))
    return business_app_key in appkey_blacklist
