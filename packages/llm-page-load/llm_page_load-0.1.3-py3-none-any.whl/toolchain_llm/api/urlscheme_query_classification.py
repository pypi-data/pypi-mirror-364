from flask import jsonify
from flask import request
from flask import Blueprint
from utils import logger
from service.urlscheme_query_cls.query_classification import query_cls


urlscheme_query_classification_service = Blueprint('urlscheme_query_classification', __name__)

@urlscheme_query_classification_service.route('/cls', methods=['POST'])
def urlscheme_query_classification():
    logger.info(f'[urlscheme_query_classification] input: {request.json}')
    payload = request.json
    query_labeled = payload.get('query_labeled', {})
    query_need_infer = payload.get('query_need_infer', {})
    # 获取推理结果
    try:
        query_cls_result = query_cls(query_labeled, query_need_infer)
        _result = {
            'code': 0,
            'error_info': '',
            'result': query_cls_result
        }
    except Exception as e:
        logger.exception('[urlscheme_query_classification] 失败', e.args)
        _result = {
            'code': 1,
            'error_info': e,
            'result': {}
        }
    logger.info(f'[urlscheme_query_classification] output: {_result}')
    return jsonify(_result)
    