from src.toolchain_llm.service.ui_detection.img_diff import ImageDiff
from src.toolchain_llm.service.ui_detection.horus_ocr import ClientHorus
from src.toolchain_llm.service.ui_detection.image_utils import TaskThread
#from src.toolchain_llm.service.app_traversal.mss_client import s3_client
import time
import cv2
import os
import base64
import io
from PIL import Image
import numpy as np

def get_ocr_result(image1, image2, offset_y_w=0.1, resize_w=1080, padding_right=80, always_split=False,
                    alpha=2.5, ocr_filter_score=0.6, business=''):
    try:
        client_ocr = ClientHorus()
        h1, w1, _ = image1.shape
        h2, w2, _ = image2.shape
        image2_task = TaskThread(
            func=client_ocr.get_long_page_ocr,
            args=(image2, offset_y_w, resize_w, padding_right, always_split, alpha, ocr_filter_score, business))
        image2_task.start()
        image1_result = client_ocr.get_long_page_ocr(image1, offset_y_w, resize_w, padding_right, always_split,
                                                        alpha, ocr_filter_score, business)['data']
        image2_task.join(timeout=15)
        image2_result = image2_task.get_result()['data']
        result = dict()
        result['image1_ocr_result'] = image1_result
        result['image2_ocr_result'] = image2_result
        result['scale'] = image1_result['scale']
    except Exception:
        result = None
    return result

def line_feature_diff(image1, image2, business):
    try:
        # 如果是PIL.Image，先convert再转np；如果已经是np.ndarray则跳过
        if hasattr(image1, 'convert'):
            image1 = image1.convert('RGB')
            image1 = np.array(image1)
            image1 = cv2.cvtColor(image1, cv2.COLOR_RGB2BGR)
        elif isinstance(image1, np.ndarray):
            if image1.shape[-1] == 3:
                pass  # 已经是BGR或RGB
            else:
                raise ValueError('image1 shape not supported')
        if hasattr(image2, 'convert'):
            image2 = image2.convert('RGB')
            image2 = np.array(image2)
            image2 = cv2.cvtColor(image2, cv2.COLOR_RGB2BGR)
        elif isinstance(image2, np.ndarray):
            if image2.shape[-1] == 3:
                pass
            else:
                raise ValueError('image2 shape not supported')
        ocr_result = get_ocr_result(image1, image2, business=business)
        image_diff_obj = ImageDiff(image1, image2, ocr_result, 0.98, 0.8, False)
        struct_score, score = image_diff_obj.get_similar_score_info([])
        print("fkscore",score)
        diff_result = image_diff_obj.image_diff([])
        (diff_pic_img, points_count) = diff_result
        result_cls = {
            'cls': 0,
            'cls_name': 'SAME',
            'score': score
        }
        if score < 0.99:
            if score < 0.5:
                result_cls['cls'] = 2
                result_cls['cls_name'] = 'NOT_SAME_PAGE'
            else:
                result_cls['cls'] = 1
                result_cls['cls_name'] = 'NOT_SIMILAR'
        return result_cls, diff_pic_img
    except Exception as e:
        print("fkfkfkf",e)
        result_cls = {
            'cls': -1,
            'cls_name': e,
            'score': -1
        }
        return result_cls, None