from flask import jsonify
from flask import request
from flask import Blueprint
from api.components.limiter import limiter
from service.ui_detection.ui_detection import preview_image_detection, text_detection
from service.ui_detection.video_performance import video_load_duration
from service.ui_detection.video_perf import video_perf
from service.ui_detection.line_feature_diff import line_feature_diff
from utils import logger
from PIL import Image
import numpy as np
import threading
import time
import base64
import cv2
import io


ui_detection = Blueprint('ui_detection', __name__)


@limiter.limit('1/minute')
@ui_detection.route('preview_image_detection', methods=['POST'])
def get_preview_image_detection():
    image_url = request.json.get('image_url')
    r = preview_image_detection(image_url)
    return jsonify({'code': 0, "data": r})


@limiter.limit('3/minute')
@ui_detection.route('text_detection', methods=['POST'])
def get_text_detection():
    image_url = request.json.get('image_url')
    r = text_detection(image_url)
    return jsonify({'code': 0, "data": r})


@limiter.limit('10/minute')
@ui_detection.route('video_perf', methods=['POST'])
def get_video_perf():
    video_url = request.json.get('video_url')
    action_list = request.json.get('action_list')
    cut = request.json.get('cut', 0)
    call_back_url = request.json.get('callBackURL')
    task_id = str(time.time()).split(".")[1]
    thread = threading.Thread(target=video_perf, args=(video_url, action_list, cut, task_id, call_back_url))
    thread.start()
    return jsonify({'code': 0, "data": {'taskId': task_id}})


@limiter.limit('5/minute')
@ui_detection.route('video_load_duration', methods=['POST'])
def get_load_duration():
    video_url = request.json.get('videoURL')
    start_time = request.json.get('start')
    callback_URL = request.json.get('callBackURL')
    ignore_list = request.json.get('ignore_list', [])
    similar_thresh = request.json.get('similar_thresh', 0)
    task_id = str(time.time()).split(".")[1]
    thread = threading.Thread(target=video_load_duration, args=(video_url, start_time, task_id, callback_URL,
                                                                ignore_list, similar_thresh))
    thread.start()
    logger.info(f"[video performance][task id:{task_id}]")
    return jsonify({'code': 0, "data": {'taskId': task_id}})

@limiter.limit('1/minute')
@ui_detection.route('image_diff', methods=['POST'])
def get_image_diff():
    logger.info('[image_diff] input')
    data = request.get_json()
    img1 = data.get('img1', None)
    img2 = data.get('img2', None)
    business_id = data.get('business', None)
    if img1 is None or img2 is None or business_id is None:
        logger.info('[image_diff] return = 未正确传入page / business')
        return jsonify({"code": 1, "message": "请正确传入 page / business"})
    else:
        logger.info(f'[image_diff] business:{business_id}')
        request_img1 = base64.b64decode(img1)
        image1 = Image.open(io.BytesIO(request_img1))
        image1 = image1.convert('RGB')
        image1 = np.array(image1)
        image1 = cv2.cvtColor(image1, cv2.COLOR_RGB2BGR)
        request_img2 = base64.b64decode(img2)
        image2 = Image.open(io.BytesIO(request_img2))
        image2 = image2.convert('RGB')
        image2 = np.array(image2)
        image2 = cv2.cvtColor(image2, cv2.COLOR_RGB2BGR)
        result = {}
        try:
            diff_result, diff_image = line_feature_diff(image1, image2, business=business_id)
            if diff_image is None:
                result = {
                    'code': 1,
                    'result': diff_result,
                    'diff_image': ''
                }
            else:
                result = {
                    'code': 0,
                    'result': diff_result,
                    'diff_image': diff_image
                }
        except Exception as e:
            logger.error(f'[image_diff] error = {str(e)}')
            result = {'code': 1, 'result': f'error = {str(e)}'}
        finally:
            logger.info(f'[image_diff] return = {result}')
        return jsonify(result)