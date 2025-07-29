import json

from flask import jsonify
from flask import request
from flask import Blueprint
from service.promot_base import PromptBase
from api.components.limiter import limiter
from service.GPT import llmcore_completion, create_conversation, mt_chat_inference
from utils import logger, GPT35NAME
import os
import requests
from llmcore_sdk.models.friday import DEEP_SEEK, GEMINI, LONGCATNAMES

CHEAP_MODELS = ['gpt-3.5-turbo-0613', 'gpt-3.5-turbo-1106', 'gpt-3.5-turbo', 'gpt-4o-mini']
CHEAP_MODELS += DEEP_SEEK + LONGCATNAMES[:7] + GEMINI  # 这些模型价位都在<¥5/百万token
CHEAP_MODELS += ['abab6.5t-chat', 'abab6.5g-chat']  # ¥5/百万token
CHEAP_MODELS += ['glm-4-air', 'glm-4-flash']


conversation = Blueprint('conversation', __name__)


@conversation.route('', methods=['POST'])
@limiter.limit('6/minute')
def get_conversation_result():
    logger.info(f'[conversation] input = {request.json}')
    payload = request.json
    model = payload.get('model', GPT35NAME)
    assert model in CHEAP_MODELS
    if "key" in payload.keys():
        if "message" in payload.keys():
            r = llmcore_completion(payload.get('message'), business='conversation_api', model=model,
                                   functions=payload.get('functions'))
            resp = {
                "choices": [{
                    "message": {
                        "content": r,
                        "role": "assistant"
                    }}
                ],
                "data": {
                    "result": r
                }
            }
            logger.info(f'[conversation] output = {resp}')
            return resp
        else:
            r = llmcore_completion([
                {"role": "system", "content": payload.get('system_content')},
                {"role": "user", "content": payload.get('user_content')}
            ], business='conversation_api', model=model, functions=payload.get('functions', None))
            resp = {
                "choices": [{
                    "message": {
                        "content": r,
                        "role": "assistant"
                    }}
                ],
                "data": {
                    "result": r
                }
            }
            logger.info(f'[conversation] output = {resp}')
            return resp
    else:
        logger.warn('[conversation] warn = please provide key')
        return jsonify({"code": 1, "message": "please provide key"})


@conversation.route('/meituanmodel/', methods=['POST'])
def get_meituan_inference_result():
    logger.info(f'[conversation] input = {request.json}')
    payload = request.json
    model = payload.get('model', 'Meituan-7B')
    assert model in ['Meituan-7B', 'Meituan-70B']
    resp = mt_chat_inference(payload.get('message'), model=model)
    logger.info(f'[conversation] output = {resp}')
    return resp



@conversation.route('/convert/json', methods=['POST'])
@limiter.limit('10/minute')
def convert_json():
    logger.info(f'[conversation/convert/json] input = {request.json}')
    payload = request.json
    if "key" in payload.keys():
        r = llmcore_completion(create_conversation(
            PromptBase.result_to_json, payload.get('content')), business='conversation_api')
        resp = {
            "choices": [{
                "message": {
                    "content": r,
                    "role": "assistant"
                }}
            ],
            "data": {
                "result": r
            }
        }
        logger.info(f'[conversation/convert/json] output = {resp}')
        return resp
    else:
        logger.warn('[conversation/convert/json] warn = please provide key')
        return jsonify({"code": 1, "message": "please provide key"})


@conversation.route('/chatglm', methods=['POST'])
@limiter.limit('10/minute')
def glm_call_in_prod():
    '''线上环境可以将请求转发到http://10.164.6.121:8414'''
    Env = os.getenv('Env', 'dev')
    if Env == 'test':
        raise NotImplementedError('线下环境不可访问chatglm')
    else:
        # 在线上环境中，将请求转发到指定的地址
        response = requests.post('http://10.164.6.121:8414', headers=request.headers, data=request.get_data())
        return response.text
