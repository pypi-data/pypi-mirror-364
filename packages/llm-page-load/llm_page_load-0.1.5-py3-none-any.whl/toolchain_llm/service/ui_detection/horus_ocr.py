import copy
import traceback

import numpy as np
import requests
import json
import numpy
from src.toolchain_llm.service.ui_detection.image_utils import get_center_pos
#from src.toolchain_llm.tools.s3 import MssHHelper
import base64
import cv2
import time

"""
# 视觉平台ocr服务，经过CQP后台转换提供HTTP接口
"""


class ClientHorus(object):
    def __init__(self):
        self.ocr_host = 'http://client.hotel.test.sankuai.com/horus/recognize/ocr'
        self.host_online = 'http://qa.sankuai.com/clientdata/horus/recognize/'
        # vision-ui服务，plus 不支持ubuntu，手动用vm mac部署
        self.vision_ui_infer_url = 'https://visionui.sankuai.com/vision/ui-infer'
        self.vision_ui_semantic_url = 'https://visionui.sankuai.com/vision/semantic-search'


    def get_ui_infer(self, image: numpy.ndarray = None, image_path: str = None, offset_y: int = 0,
                     cls_thresh: float = 0.5):
        result = {'code': 0, 'data': {'recognize_results': []}}
        header = {'Content-Type': 'application/json;charset=utf-8'}

        if image is not None:
            image_b = base64.b64encode(cv2.imencode('.png', image)[1].tobytes())
            image_source = bytes.decode(image_b)
            payload = {'image': image_source, 'type': 'base64', 'cls_thresh': cls_thresh}
        elif image_path:
            self.client_s3 = MssHHelper()
            ts = str(time.time()).split('.')[1]
            image_name = image_path.split('/')[-1]
            s3_path_name = f'resource/{ts}-{image_name}'
            image_url = self.client_s3.save_to_mss(image_path, s3_path_name)
            payload = {'url': image_url, 'cls_thresh': cls_thresh}

        # retry for qps limitation
        max_try = 3
        resp = type('Resp', (object,), dict(text=''))()
        for i in range(max_try):
            resp = requests.post(url=self.vision_ui_infer_url, json=payload, headers=header, timeout=30.0)
            if resp.status_code == 200:
                resp_obj = json.loads(resp.text)
                if resp_obj.get('code') == 0:
                    # 转换
                    result['data']['recognize_results'] = resp_obj['data']
                    for recognize in result['data']['recognize_results']:
                        recognize['elem_det_region'][1] += offset_y
                        recognize['elem_det_region'][3] += offset_y
                    break
            # sleep for qps limitation
            time.sleep(1)
        else:
            result['code'] = 1
            result['data'] = resp.text
        return result

    def get_inspect(self, image_source: str, func_type: str):
        self.client_s3 = MssHHelper()
        result = {'code': 0, 'data': {'recognize_results': [], 'img_shape': []}}
        header = {'Content-Type': 'application/json;charset=utf-8'}
        ts = str(time.time()).split('.')[1]
        image_name = image_source.split('/')[-1]
        s3_path_name = f'resource/{ts}-{image_name}'
        image_url = self.client_s3.save_to_mss(image_source, s3_path_name)
        host = self.host_online + func_type
        if func_type == 'inspect':
            resp_r_key = 'result_info'
        elif func_type == 'uiCompat':
            resp_r_key = 'result_str'
        else:
            resp_r_key = 'result_info'
        payload = {'url': image_url}
        # retry for qps limitation
        max_try = 3
        resp = type('Resp', (object,), dict(text=''))()
        for i in range(max_try):
            resp = requests.request('POST', url=host, data=json.dumps(payload), headers=header, timeout=30.0)
            if resp.status_code == 200:
                resp_obj = json.loads(resp.text)
                if resp_obj.get('code') == 0:
                    result['data']['img_url'] = image_url
                    result['data']['img_shape'] = cv2.imread(image_source).shape
                    result['data']['recognize_results'] = resp_obj[resp_r_key]['result_info_listIterator']
                    break
            # sleep for qps limitation
            time.sleep(1)
        else:
            result['code'] = 1
            result['data'] = resp.text
        return result


    def find_split_point_for_ui_infer(self, result, img, offset_y=0):
        h, w, _ = img.shape
        r = numpy.zeros(h, dtype=numpy.dtype('int8'))
        for recognize in result['data']['recognize_results']:
            y1 = int(recognize['elem_det_region'][1] - offset_y)
            y2 = int(recognize['elem_det_region'][3] - offset_y)
            r[y1:y2 + 1] = 1
        y_ranges = []
        y_range = []
        for i, p in enumerate(r):
            if p == 0 and len(y_range) == 0:
                y_range.append(i)
            if p == 1 and len(y_range) == 1:
                y_range.append(i - 1)
            if len(y_range) == 2:
                y_ranges.append(y_range)
                y_range = []
        if len(y_ranges) > 0:
            next_y = int((y_ranges[-1][0]+y_ranges[-1][1])/2)
        else:
            next_y = h
        if next_y < int(h/3):
            next_y = h
        next_y += offset_y
        filtered_result = []
        for recognize in result['data']['recognize_results']:
            y2 = int(recognize['elem_det_region'][3])
            if y2 < next_y:
                filtered_result.append(recognize)
        result['data']['recognize_results'] = filtered_result
        return next_y

    def get_long_page_ui_infer(self, pic_path, cls_thresh):
        alpha = 2.5
        padding = 80
        image = cv2.imread(pic_path)
        result = {'code': 0, 'data': {'recognize_results:': [], 'img_shape': []}}
        image = cv2.GaussianBlur(image, (3, 3), 1.0)
        h_origin, w_origin, _ = image.shape
        scale = 1080/w_origin if w_origin > 1080 else 1.0
        image = cv2.resize(image, (0, 0), fx=scale, fy=scale)
        h, w, _ = image.shape
        top = int(w*0.1)
        if h/w < alpha:
            result = self.get_ui_infer(image=image[top:, :, :], offset_y=top, cls_thresh=cls_thresh)
        else:
            image = image[:, :w-padding, :]
            start = top
            end = start + int(alpha*w)
            while start < h:
                if start > top:
                    time.sleep(0.15)
                    ret = self.get_ui_infer(image=image[start:end, :, :], offset_y=start, cls_thresh=cls_thresh)
                    next_y = self.find_split_point_for_ui_infer(ret, image[start:end, :, :], start)
                    result['data']['recognize_results'].extend(ret['data']['recognize_results'])
                else:
                    result = self.get_ui_infer(image=image[start:end, :, :], offset_y=start, cls_thresh=cls_thresh)
                    next_y = self.find_split_point_for_ui_infer(result, image[start:end, :, :], start)

                start = next_y
                end = start + int(alpha*w)

        # scale 转换
        for recognize in result['data']['recognize_results']:
            recognize['elem_det_region'] = numpy.asfarray(recognize['elem_det_region']) / scale
        result['data']['img_shape'] = [h, w, 1]
        result['data']['scale'] = scale
        return result

    def get_ocr_from_horus(self, image_source, business=''):
        host = self.ocr_host
        header = {'Content-Type': 'application/json;charset=utf-8'}
        key = 'url'
        h_w = 0
        if isinstance(image_source, numpy.ndarray):
            key = 'img'
            h_w = image_source.shape
            host = self.host_online + 'ocrProxy'
            image_b = base64.b64encode(cv2.imencode('.jpg', image_source)[1])
            image_source = bytes.decode(image_b)
        payload = {key: image_source, 'model_type': '2'}
        success = False
        exception_msg = ''
        end_time = 0
        resp_obj = None
        cause = None
        start_time = time.time()
        try:
            resp = requests.request('POST', url=host, data=json.dumps(payload), headers=header, timeout=15.0)
            end_time = time.time()
            resp_obj = json.loads(resp.text)
            _origin_resp_obj = copy.deepcopy(resp_obj)
            if 'responseData' in resp_obj.keys() and len(resp_obj['responseData']) > 0:
                resp_obj = json.loads(_origin_resp_obj['responseData']['result'])
            resp_obj['code'] = _origin_resp_obj['code']
            resp_obj['shape_info'] = h_w
            success = resp_obj.get('code') == 0
            if not success:
                cause = "API返回异常"
                exception_msg = resp_obj.message
        except Exception:
            end_time = time.time()
            exception_msg = traceback.format_exc()
            cause = "发送API请求失败"
        finally:
            time_used_millis = (end_time - start_time) * 1000
        return success, resp_obj

    def get_ocr(self, image_source, offset_y=0, ocr_filter_score=0.6, business=''):
        result = {'code': 0, 'data': {'roi_text': [], 'img_shape': []}}

        success = False
        resp_obj = None
        # 最多重试2次
        for _ in range(2):
            success, resp_obj = self.get_ocr_from_horus(image_source, business)
            if success:
                break
            time.sleep(2)
        # process
        if success:
            result['data']['trace_id'] = resp_obj['trace_id'] if 'trace_id' in resp_obj else 0
            shape_info = resp_obj['shape_info']
            if shape_info[0] > shape_info[1]:
                img_h, img_w = shape_info[0], shape_info[1]
            else:
                img_h, img_w = shape_info[1], shape_info[0]
            result['data']['img_shape'] = [img_h, img_w, 1]
            for i in range(len(resp_obj.get('results_str', []))):
                if isinstance(resp_obj['prob_string'][i], list):
                    score = numpy.mean(resp_obj['prob_string'][i])
                else:
                    score = float(resp_obj['prob_string'][i])
                text = resp_obj['results_str'][i]
                if isinstance(resp_obj['location'][i], list):
                    points = [int(point) for point in resp_obj['location'][i]]
                else:
                    points = [int(point) for point in resp_obj['location'][i].replace('[', '').replace(']', '').split(' ') if len(point) > 0]
                rect = numpy.array([[points[0], points[1]+offset_y], [points[2], points[3]+offset_y],
                                    [points[4], points[5]+offset_y], [points[6], points[7]+offset_y]])
                result['data']['roi_text'].append({'rect': rect, 'pos': get_center_pos(rect), 'text': text, 'score': score}) if score > ocr_filter_score else 0
        else:
            result['code'] = 1
            result['data']['roi_text'].append({'rect': [], 'pos': (0, 0), 'text': json.dumps(resp_obj), 'score': 1.0})
        return result

    def filter_result(self, result, img, offset_y=0):
        h, w, _ = img.shape
        r = numpy.zeros(h, dtype=numpy.dtype('int8'))
        for recognize in result['data']['roi_text']:
            y1 = recognize['rect'][0][1] - offset_y
            y2 = recognize['rect'][2][1] - offset_y
            r[y1:y2 + 1] = 1
        y_ranges = []
        y_range = []
        for i, p in enumerate(r):
            if p == 0 and len(y_range) == 0:
                y_range.append(i)
            if p == 1 and len(y_range) == 1:
                y_range.append(i - 1)
            if len(y_range) == 2:
                y_ranges.append(y_range)
                y_range = []
        if len(y_ranges) > 0:
            next_y = int((y_ranges[-1][0]+y_ranges[-1][1])/2)
        else:
            next_y = h
        if next_y < int(h/2):
            next_y = h
        next_y += offset_y
        filtered_result = []
        for recognize in result['data']['roi_text']:
            y2 = recognize['rect'][2][1]
            if y2 < next_y:
                filtered_result.append(recognize)
        result['data']['roi_text'] = filtered_result
        return next_y

    def get_long_page_ocr(self, image, offset_y_w=0.1, resize_w=1080, padding_right=80, always_split=False, alpha=2.5,
                          ocr_filter_score=0.6, business=''):
        image = cv2.imread(image) if isinstance(image, str) else image
        result = {'code': 0, 'data': {'roi_text:': [], 'img_shape': []}}
        h_origin, w_origin, _ = image.shape
        scale = resize_w / w_origin if resize_w != 0 else 1
        if scale != 1:
            image = cv2.resize(image, (0, 0), fx=scale, fy=scale)
        image = cv2.GaussianBlur(image, (3, 3), 1.0)
        h, w, _ = image.shape
        top = int(offset_y_w * w)
        if h/w < alpha and always_split is False:
            result = self.get_ocr(image[top:, :, :], offset_y=top, ocr_filter_score=ocr_filter_score, business=business)
        else:
            image = image[:, :w-padding_right, :]
            start = top
            end = start + int(alpha*w)
            while start < h:
                if start > top:
                    time.sleep(0.15)
                    ret = self.get_ocr(image[start:end, :, :], offset_y=start, ocr_filter_score=ocr_filter_score,
                                       business=business)
                    next_y = self.filter_result(ret, image[start:end, :, :], start)
                    result['data']['roi_text'].extend(ret['data']['roi_text'])
                else:
                    result = self.get_ocr(image[start:end, :, :], offset_y=start, business=business,
                                          ocr_filter_score=ocr_filter_score)
                    next_y = self.filter_result(result, image[start:end, :, :], start)
                start = next_y
                end = start + int(alpha*w)

        # scale换算
        for roi_text in result['data']['roi_text']:
            roi_text['pos'] = (int(roi_text['pos'][0] / scale), int(roi_text['pos'][1] / scale))
            for value in roi_text['rect']:
                value[0] = value[0] / scale
                value[1] = value[1] / scale
        result['data']['img_shape'] = [h_origin, w_origin, 1]
        # 外面就不需要再通过scale再换算了
        result['data']['scale'] = 1
        return result

    @staticmethod
    def fix_text_rect(text_rect, ocr_img_scale):
        """
        因为使用ClientHorus().get_long_page_ocr()获取文本信息时，对图片进行缩放，导致返回的文本位置信息是相对缩放后的坐标，所以需要对返回坐标进行转换。
        @param text_rect：文本区域的四点坐标，例如：[[x1, y1], [x2, y2], [x3, y3], [x4, y4]]
        @param ocr_img_scale：图片缩放率
        @return 修正后后的四点坐标
        """
        if ocr_img_scale == 1:
            return text_rect

        fix_text_rect = []
        for index in range(len(text_rect)):
            x = text_rect[index][0] / ocr_img_scale
            y = text_rect[index][1] / ocr_img_scale
            fix_text_rect.append([x, y])

        return fix_text_rect

    def find_elem_by_image_semantic(self, target_img_path, source_img_path, desc, top_k, confidence_score,
                                    proposal_provider, logger):
        try:
            source_img = cv2.imread(source_img_path)
            if target_img_path:
                target_img = cv2.imread(target_img_path)
                if target_img.shape[1] >= source_img.shape[1]:
                    # 需要缩放一下
                    scale_percent = (source_img.shape[1] - 1) / target_img.shape[1]  # 缩放比例
                    w = int(target_img.shape[1] * scale_percent)
                    h = int(target_img.shape[0] * scale_percent)
                    target_img = cv2.resize(target_img, (w, h))
                image_b_t = base64.b64encode(cv2.imencode('.png', target_img)[1])
                target_img_source = bytes.decode(image_b_t)
                image_alpha = 1.0
            else:
                target_img = np.zeros([100, 100, 3], dtype=np.uint8) + 255
                image_b_t = base64.b64encode(cv2.imencode('.jpg', target_img)[1])
                target_img_source = bytes.decode(image_b_t)
                image_alpha = 0.0

            image_b_s = base64.b64encode(cv2.imencode('.png', source_img)[1])
            source_img_source = bytes.decode(image_b_s)

            text_alpha = 0.0
            if desc != "":
                text_alpha = 0.5

            payload = {
                'type': 'base64',
                'target_image': target_img_source,
                'source_image': source_img_source,
                'target_desc': desc,
                'image_alpha': image_alpha,
                'text_alpha': text_alpha,
                'top_k': top_k,
                'proposal_provider': proposal_provider if proposal_provider else 'ui-infer'
            }
            ret = self.semantic_search(payload)
            logger.info(f"image semantic top{top_k}: {ret}")
            target_pos_list = []
            target_area_list = []
            if ret['code'] == 0:
                for _target in ret['data']['search_result']:
                    if ret['data']['max_confidence'] * _target['score'] >= confidence_score:
                        x1, y1, x2, y2 = _target['boxes']
                        target_pos_list.append((int((x1 + x2) / 2), int((y1 + y2) / 2)))
                        target_area_list.append(_target['boxes'])
                if len(target_pos_list) > 1:
                    # point (x, y), Sort by y, then by x
                    sort_data = [[p[0], p[1]] for p in target_pos_list]
                    sort_data_np = np.array(sort_data)
                    idx_sorts = np.lexsort((tuple(sort_data_np[:, 0]), tuple(sort_data_np[:, 1])))
                    sorted_pos_list = []
                    sorted_area_list = []
                    for idx in idx_sorts:
                        sorted_pos_list.append(target_pos_list[idx])
                        sorted_area_list.append(target_area_list[idx])
                    target_pos_list = sorted_pos_list
                    target_area_list = sorted_area_list
            return target_pos_list, target_area_list
        except Exception as e:
            logger.info(f"find elem by image semantic error:{repr(e)}")
            return []

