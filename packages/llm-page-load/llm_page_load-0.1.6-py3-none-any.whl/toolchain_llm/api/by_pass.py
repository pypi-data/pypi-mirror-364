from flask import request, jsonify
from flask import Blueprint
from utils import logger
import os
import requests
from service.lang_chain_utils.lion_client import client as lion
import json

bypass = Blueprint('bypass', __name__)


@bypass.route('/embedding/<path:path>', methods=['POST'])
def bypass_to_embedding(path):
    '''线上环境可以将请求转发到 10.164.6.121，embedding的端口是8416'''
    Env = os.getenv('Env', 'dev')
    if Env == 'test':
        raise NotImplementedError('线下环境不可访问A100机器')
    else:
        # 在线上环境中，将请求转发到指定的地址
        lion.fetch_config()
        valid_path = json.loads(lion.config.get(f'{lion.app_name}.bypass.embedding_valid'))
        assert path in valid_path, '没有对应的url'
        path = valid_path[path]
        response = requests.post('http://10.164.6.121:8416/'+path, headers=request.headers, data=request.get_data())
        object = response.json()
        return jsonify(object)


@bypass.route('/uitestagent/<path:path>', methods=['POST'])
def bypass_to_uitestagent(path):
    '''线上环境可以将请求转发到 10.164.6.121，动态端口'''
    Env = os.getenv('Env', 'dev')
    if Env == 'test':
        raise NotImplementedError('线下环境不可访问A100机器')
    else:
        # 在线上环境中，将请求转发到指定的地址
        lion.fetch_config()
        valid_path = json.loads(lion.config.get(f'{lion.app_name}.bypass.uitestagent'))
        assert path in valid_path, '没有对应的url'
        path = valid_path[path]['path']
        port = valid_path[path]['host']
        response = requests.post(f'http://10.164.6.121:{port}/'+path, headers=request.headers, data=request.get_data())
        object = response.json()
        return jsonify(object)


@bypass.route('/image_analysis/<path:path>', methods=['POST'])
def bypass_to_image_analysis(path):
    Env = os.getenv('Env', 'dev')
    if Env == 'test':
        logger.info('[bypass_to_image_analysis]: 线下环境不可访问A100机器')
        raise NotImplementedError('线下环境不可访问A100机器')
    else:
        # 请求转发A100
        lion.fetch_config()
        valid_path = json.loads(lion.config.get(f'{lion.app_name}.bypass.embedding_valid'))
        logger.info(f'[bypass_to_image_analysis]: 请求{path}')
        assert path in valid_path, '没有对应的url'
        path = valid_path[path]
        response = requests.post('http://10.164.6.121:8418/'+path, headers=request.headers, data=request.get_data())
        object = response.json()
        return jsonify(object)
