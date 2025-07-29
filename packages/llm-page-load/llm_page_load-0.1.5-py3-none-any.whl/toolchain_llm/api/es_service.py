from flask import jsonify
from flask import request
from flask import Blueprint
from utils import logger, appkey
from llmcore_sdk.data_connection.es_client import LLMElasticsearchClient
from service.file_config_reader import read_lion_file_config
import os

# 初始化ES
ES_ENV = os.getenv('ES_ENV', 'default')
config = read_lion_file_config('es_client.conf')
accesskey = config[ES_ENV]['accesskey']
appkey = config[ES_ENV]['appkey']
is_online_env = config[ES_ENV]['isOnlineEnv'] == 'true'
api_accesskey = config[ES_ENV]['api_accesskey']
es_util = LLMElasticsearchClient(accesskey=accesskey, appkey=appkey, is_online_env=is_online_env)


es_service = Blueprint('es_service', __name__)

@es_service.route('/search', methods=['POST'])
def search_from_es():
    logger.info(f'[es search] input = {request.json}')
    payload = request.json
    index = payload.get('index', None)
    query = payload.get('query', None)
    if index and query:
        search_result = es_util.client.search(index=index, body=query, headers=es_util.headers)
        logger.info(f'[es search] return = {search_result}')
        return jsonify(search_result)
    else:
        logger.warn('[es search] warn = please provide index and query')
        return jsonify({"code": 1, "message": "please provide index and query"})

@es_service.route('/update', methods=['POST'])
def update_from_es():
    logger.info(f'[es update] input = {request.json}')
    payload = request.json
    index = payload.get('index', None)
    id = payload.get('id', None)
    body = payload.get('body', None)
    if index and id and body:
        update_result = es_util.update(index, id, body)
        logger.info(f'[es update] return = {update_result}')
        return jsonify(update_result)
    else:
        logger.warn('[es update] warn = please provide index / id / query')
        return jsonify({"code": 1, "message": "please provide index / id / query"})

@es_service.route('/delete', methods=['POST'])
def delete_from_es():
    logger.info(f'[es delete] input = {request.json}')
    payload = request.json
    index = payload.get('index', None)
    id = payload.get('id', None)
    if index and id:
        delete_result = es_util.delete(index, id)
        logger.info(f'[es delete] return = {delete_result}')
        return jsonify(delete_result)
    else:
        logger.warn('[es delete] warn = please provide index / id')
        return jsonify({"code": 1, "message": "please provide index / id"})

@es_service.route('/index', methods=['POST'])
def add_to_es():
    logger.info(f'[es index] input = {request.json}')

    # 验证 API 密钥
    api_key = request.headers.get('X-APPKEY')
    if api_key != appkey:
        logger.warn('[es index] warn = unauthorized access')
        return jsonify({"code": 403, "message": "unauthorized access"}), 403

    payload = request.json
    index = payload.get('index', None)
    body = payload.get('body', None)
    if index and body:
        add_result = es_util.client.index(index=index, body=body, headers=es_util.headers)
        logger.info(f'[es index] return = {add_result}')
        return jsonify(add_result)
    else:
        logger.warn('[es index] warn = please provide index and body')
        return jsonify({"code": 1, "message": "please provide index and body"})
