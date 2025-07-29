import base64
from PIL import Image
import io
import cv2
import numpy as np
import time
import os
from flask import jsonify
from flask import request
from flask import Blueprint
from utils import logger
from service.case_generation.service import case_generation

auto_case_generate = Blueprint('auto_case_generate', __name__)


@auto_case_generate.route('/case_generation', methods=['POST'])
def case_generate():
    """生成case

    Returns:
        code(int): 0成功 1错误
        cases(dict): 生成的case
    """
    data = request.get_json()
    page = data.get('page', None)
    checklist = data.get('checklist', "")
    result = {}
    try:
        cases = case_generation(page, checklist)
        result = {
            'code': 0,
            'cases': cases
        }
    except Exception as e:
        logger.error(f'[case_generate] error = {str(e)}')
        result = {'code': 1, 'message': f'error = {str(e)}'}
    finally:
        logger.info(f'[case_generate] return = {result}')

    return jsonify(result)
    
