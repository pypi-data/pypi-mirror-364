from flask import jsonify
from flask import request
from flask import Blueprint
from utils import logger
from service.stabex_trace_diff.trace_diff import compare_trace, set_trace_as_ground_truth
from service.stabex_trace_diff.trace_page_match import page_match


trace_compare_service = Blueprint('trace_compare', __name__)

@trace_compare_service.route('/compare_trace', methods=['POST'])
def compare_trace_api():
    logger.info(f'[compare_trace] input: {request.json}')
    payload = request.json
    task_id = payload.get('task_id', "")
    case_name = payload.get('case_name', "")
    mode = payload.get('mode', "soft")
    # 获取推理结果
    try:
        is_compare, reason, confidence = compare_trace(task_id, case_name, mode)
        _result = {
            'code': 0,
            'error_info': '',
            'result': {'is_compare': is_compare, 'reason': reason, 'confidence': confidence}
        }
    except Exception as e:
        logger.exception('[compare_trace] 失败', e.args)
        _result = {
            'code': 1,
            'error_info': str(e),
            'result': {}
        }
    logger.info(f'[compare_trace] output: {_result}')
    return jsonify(_result)
    
@trace_compare_service.route('/set_trace_as_ground_truth', methods=['POST'])
def set_trace_as_ground_truth_api():
    logger.info(f'[set_trace_as_ground_truth] input: {request.json}')
    payload = request.json
    task_id = payload.get('task_id', "")
    case_name = payload.get('case_name', "")
    # 获取推理结果
    try:
        success, reason = set_trace_as_ground_truth(task_id, case_name)
        _result = {
            'code': 0,
            'error_info': '',
            'result': {'success': success, 'reason': reason}
        }
    except Exception as e:
        logger.exception('[set_trace_as_ground_truth] 失败', e.args)
        _result = {
            'code': 1,
            'error_info': e,
            'result': {}
        }
    logger.info(f'[set_trace_as_ground_truth] output: {_result}')
    return jsonify(_result)


@trace_compare_service.route('/page_match', methods=['POST'])
def page_match_api():
    logger.info(f'[page_match] input: {request.json}')
    payload = request.json
    task_id = payload.get('task_id', "")
    case_name = payload.get('case_name', "")
    action_index = payload.get('action_index', 1)
    # 获取推理结果
    try:
        result = page_match(task_id, case_name, action_index)
        if result.get('success', False):
            _result = {
                'code': 0,
                'error_info': '',
                'result': result
            }
        else:
            _result = {
                'code': 1,
                'error_info': result.get('error', 'Unknown error'),
                'result': result
            }
    except Exception as e:
        logger.exception('[page_match] 失败', e.args)
        _result = {
            'code': 1,
            'error_info': str(e),
            'result': {}
        }
    logger.info(f'[page_match] output: {_result}')
    return jsonify(_result)