import base64
from PIL import Image
import io
import cv2
import numpy as np
from flask import jsonify
from flask import request
from flask import Blueprint
from utils import logger
from service.app_traversal.result_label_service import label_node
from service.app_traversal.page_classification_service import check_error_situations
from service.app_traversal.image_similarity_service import cal_image_similarity
from service.app_traversal.interaction_check_service import interaction_check_claudeInstant
from service.app_traversal.ui_inspect_service import get_page_inspect

app_traversal_service = Blueprint('app_traversal', __name__)

@app_traversal_service.route('/label_node', methods=['POST'])
def search_from_es():
    logger.info(f'[label_node] input = {request.json}')
    payload = request.json
    taskid = payload.get('taskid', None)
    index = payload.get('index', None)
    labeled_result = payload.get('labeled_result', '')
    labeled_reason = payload.get('labeled_reason', '')
    if taskid and index:
        update_result = label_node(task_id=taskid, index=index, labeled_result=labeled_result, labeled_reason=labeled_reason)
        logger.info(f'[label_node] return = {update_result}')
        return jsonify(update_result)
    else:
        logger.warn('[label_node] warn = please provide taskid and index')
        return jsonify({"code": 1, "message": "please provide taskid and index"})


@app_traversal_service.route('/page_classification', methods=['POST'])
def page_classification():
    """页面分类，传入截图，返回是否存在异常

    Returns:
        code(int): 0推理成功 1发生错误
        error_flag(bool): False不存在问题 True存在问题
        error_type(str): 存在问题的描述
    """
    logger.info(f'[page_classification] input')
    data = request.get_json()
    page = data.get('page', None)
    business_id = data.get('business', None)
    if page is None or business_id is None:
        logger.info(f'[page classification] return = 未正确传入page / business')
        return jsonify({"code": 1, "message": "请正确传入 page / business"})
    else:
        logger.info(f'[page_classification] business:{business_id}')
        request_img = base64.b64decode(page)
        image = Image.open(io.BytesIO(request_img))
        image = image.convert('RGB')
        image = np.array(image)
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        result = {}
        try:
            error_flag, error_situation = check_error_situations(image)
            result = {
                'code': 0,
                'error_flag': error_flag,
                'error_type': error_situation
            }
        except Exception as e:
            logger.error(f'[page_classification] error = {str(e)}')
            result = {'code': 1, 'message': f'error = {str(e)}'}
        finally:
            logger.info(f'[page classification] return = {result}')
        return jsonify(result)
    

@app_traversal_service.route('/image_similarity', methods=['POST'])
def image_similarity():
    """计算图像结构相似度及颜色相似度，传入截图1/2，返回相似度指标

    Returns:
        code(int): 0推理成功 1发生错误
        structure_similarity(float): 0-1 越接近1则越相似
        color_similarity(float): 0-1 越接近1则越相似
    """
    logger.info(f'[image_similarity] input')
    data = request.get_json()
    page1 = data.get('image1', None)
    page2 = data.get('image2', None)
    business_id = data.get('business', None)
    if business_id is None:
        logger.info(f'[image_similarity] return = 未正确传入business')
        return jsonify({"code": 1, "message": "请正确传入business"})
    if page1 is None or page2 is None:
        logger.info(f'[image_similarity] return = 未正确传入page')
        return jsonify({"code": 1, "message": "请正确传入image"})
    else:
        logger.info(f'[image_similarity] business:{business_id}')
        request_img = base64.b64decode(page1)
        image1 = Image.open(io.BytesIO(request_img))
        image1 = image1.convert('RGB')
        image1 = np.array(image1)
        image1 = cv2.cvtColor(image1, cv2.COLOR_RGB2BGR)
        request_img = base64.b64decode(page2)
        image2 = Image.open(io.BytesIO(request_img))
        image2 = image2.convert('RGB')
        image2 = np.array(image2)
        image2 = cv2.cvtColor(image2, cv2.COLOR_RGB2BGR)
        result = {}
        try:
            structure_similarity, color_similarity = cal_image_similarity(image1, image2)
            result = {
                'code': 0,
                'structure_similarity': structure_similarity,
                'color_similarity': color_similarity
            }
        except Exception as e:
            logger.error(f'[image_similarity] error = {str(e)}')
            result = {'code': 1, 'message': f'error = {str(e)}'}
        finally:
            logger.info(f'[image_similarity] return = {result}')
        return jsonify(result)


@app_traversal_service.route('/interaction_check', methods=['POST'])
def interaction_check():
    """计算单次交互是否符合预期，输入交互前截图，交互节点box坐标(x1, y1, x2, y2)，交互后截图，返回是否符合预期及判断原因
    
    Returns:
        code(int): 0推理成功 1发生错误
        result(bool): True交互结果符合预期 False交互结果不符合预期
        reason(string): 是否符合预期的判断原因
    """
    logger.info(f'[interaction_check] input')
    data = request.get_json()
    page1 = data.get('image1', None)
    page2 = data.get('image2', None)
    bbox_coords = data.get('bbox_coords', None)
    business_id = data.get('business', None)
    if business_id is None:
        logger.info(f'[interaction_check] return = 未正确传入business')
        return jsonify({"code": 1, "message": "请正确传入business"})
    if page1 is None or page2 is None:
        logger.info(f'[interaction_check] return = 未正确传入page')
        return jsonify({"code": 1, "message": "请正确传入图像! image1 image2 "})
    elif bbox_coords is None:
        logger.info(f'[interaction_check] return = 未正确传入交互节点坐标bbox_coords')
        return jsonify({"code": 1, "message": "请传入交互节点坐标! bbox_coords: [x1, y1, x2, y2]"})
    else:
        logger.info(f'[interaction_check] business:{business_id}')
        request_img = base64.b64decode(page1)
        image1 = Image.open(io.BytesIO(request_img))
        image1 = image1.convert('RGB')
        image1 = np.array(image1)
        image1 = cv2.cvtColor(image1, cv2.COLOR_RGB2BGR)
        request_img = base64.b64decode(page2)
        image2 = Image.open(io.BytesIO(request_img))
        image2 = image2.convert('RGB')
        image2 = np.array(image2)
        image2 = cv2.cvtColor(image2, cv2.COLOR_RGB2BGR)
        result = {}
        try:
            code, result = interaction_check_claudeInstant(image1, image2, bbox_coords)
            logger.info(f'[interaction_check] return = code:{code} result:{result}')
            if code == 0:
                result = {
                    'code': 0,
                    'result': result.get('result', False),
                    'reason': result.get('reason', '')
                }
            else:
                result = {
                    'code': 1,
                    'message': result.get('message', '')
                }
        except Exception as e:
            logger.error(f'[interaction_check] error = {str(e)}')
            result = {'code': 1, 'message': f'error = {str(e)}'}
        finally:
            logger.info(f'[interaction_check] return = {result}')
        return jsonify(result)


@app_traversal_service.route('/page_inspect', methods=['POST'])
def page_inspect():
    """页面元素识别，传入截图，返回所有识别到的元素

    Returns:
        code(int): 0推理成功 1发生错误
        data(dict): 元素识别结果
    """
    logger.info(f'[page_inspect] input')
    data = request.get_json()
    page = data.get('page', None)
    business_id = data.get('business', None)
    if page is None or business_id is None:
        logger.info(f'[page classification] return = 未正确传入page / business')
        return jsonify({"code": 1, "message": "请正确传入 page / business"})
    else:
        logger.info(f'[page_inspect] business:{business_id}')
        request_img = base64.b64decode(page)
        image = Image.open(io.BytesIO(request_img))
        image = image.convert('RGB')
        image = np.array(image)
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        result = {}
        try:
            visionui_inspect = get_page_inspect(image)
            result = visionui_inspect
        except Exception as e:
            logger.error(f'[page_inspect] error = {str(e)}')
            result = {'code': 1, 'message': f'error = {str(e)}'}
        finally:
            logger.info(f'[page_inspect] return = {result}')
        return jsonify(result)