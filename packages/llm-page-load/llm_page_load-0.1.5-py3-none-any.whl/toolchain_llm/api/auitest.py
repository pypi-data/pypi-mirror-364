import imagehash
import ast
from flask import jsonify
from flask import request
from flask import Blueprint
from utils import logger
from service.aui_test_agent.single_step_service import trigger_agent, init_record, explain_record, search_record


auitest = Blueprint("auitest", __name__)


@auitest.route("/match_widget", methods=["POST"])
def urlscheme_query_classification():
    logger.info(f"[image_hash_sim] input: {request.json}")
    payload = request.json
    widget_need_match = payload.get("widget_need_match", {})
    widgets_list = payload.get("widgets_list", {})
    # 获取推理结果
    try:
        for current_widget_id, current_widget_info in widgets_list.items():
            current_hash = imagehash.hex_to_hash(widget_need_match["hash_value"])
            knowledge_hash = imagehash.hex_to_hash(current_widget_info["hash_value"])
            current_node_path = ast.literal_eval(widget_need_match["path"][0])
            knowledge_node_path = ast.literal_eval(current_widget_info["path"][0])
            # knowledge_node_path = knowledge_node_path_str.strip("[]").replace("'", "").split(', ') if knowledge_node_path_str.strip("[]") else []
            if len(knowledge_node_path) and len(current_node_path): # 如果都存在xml结构
                if get_path_similarity(current_node_path, knowledge_node_path) < 0.8:
                    if knowledge_hash - current_hash < 10:
                        _result = {
                            "code": 0,
                            "if_match": True,
                            "widget_id": current_widget_id,
                        }
                        logger.info(f"[match_widget] output: {_result}")
                        return jsonify(_result)
            else: # 不存在xml结构，直接匹配图像哈希
                if (knowledge_hash - current_hash) < 10:
                    _result = {
                        "code": 0,
                        "if_match": True,
                        "widget_id": current_widget_id,
                    }
                    logger.info(f"[match_widget] output: {_result}")
                    return jsonify(_result)
        # 没匹配上
        _result = {"code": 0, "if_match": False, "widget_id": ''} 
        return jsonify(_result)
    except Exception as e:
        logger.exception("[match_widget] 失败", e.args)
        _result = {"code": 1, "if_match": False, "widget_id": ''}
        logger.info(f"[urlscheme_query_classification] output: {_result}")
        return jsonify(_result)


def get_path_similarity(old_path, new_path):
    """
    计算路径相似度
    """
    if old_path == new_path:
        return 1

    # 如果当前节点的类型都不一样，默认当成不一样的节点
    if old_path[0] != new_path[0]:
        return 0

    old_length = len(old_path)
    new_length = len(new_path)

    merge_length = max(old_length, new_length)
    overlap_length = min(old_length, new_length)

    same_path_length = 0
    for index in range(overlap_length):
        if old_path[index] == new_path[index]:
            same_path_length += 1

    return same_path_length / merge_length


@auitest.route('/agent_trigger', methods=['POST'])
def _agent_trigger():
    method_name = request.json.get('method_name')
    driver_args = request.json.get('driver_args', {})
    agent_args = request.json.get('agent_args', {})
    message = trigger_agent(driver_args, method_name, **agent_args)
    return jsonify({
        'success': 'ok',
        'message': message
    })


@auitest.route('/web_recorder/explain', methods=['POST'])
def _web_recorder_explain():
    try:
        record_data = request.json.get('record_data')
        record_task_id = request.json.get('record_task_id')
        record_id = request.json.get('record_id')
        explain_record(init_record(record_data, record_task_id, record_id))
        return jsonify({'success': 'ok', 'code': 0})
    except Exception as e:
        logger.error('失败', e)
        raise e


@auitest.route('/web_recorder/list', methods=['GET'])
def _web_recorder_list():
    record_task_id = request.args.get('record_task_id')
    return jsonify({'success': 'ok', 'data': search_record(record_task_id)})
