import cv2
import numpy as np
import time
import os
from PIL import Image
from service.app_traversal.visionui_client import visionui_client
from service.app_traversal.image_utils import assemble_elems, get_bbox_center_pos, get_ocr_only_text_result
from service.app_traversal.llm_utils import get_node_description_by_llm, judging_rationality
from utils import logger


def interaction_check_claudeInstant(image1, image2, bbox_coords):
    # 将首张图像进行本地保存
    logger.info(f'[interaction_check_claudeInstant]: 图片本地保存')
    current_timestamp = str(int(time.time()*1000))
    app_traversal_dir = os.path.dirname(os.path.realpath(__file__))
    temp_dir = os.path.join(app_traversal_dir, 'temp')
    image1_local_temp_pth = os.path.join(temp_dir, f'{current_timestamp}_image1.png')
    cv2.imwrite(image1_local_temp_pth, image1)
    # 使用inspect获取到交互前页面的元素
    logger.info(f'[interaction_check_claudeInstant]: inspect获取到交互前页面的元素')
    current_img_h, current_img_w = image1.shape[:2]
    visionui_inspect = visionui_client.get_inspect(image1_local_temp_pth, 'inspect')
    # 删除本地图像
    os.remove(image1_local_temp_pth)
    if visionui_inspect.get('code', '') == 0:
        all_elements = visionui_inspect['data']['recognize_results']
        all_elements = assemble_elems(all_elements, int(current_img_w * 0.03))
        all_elements = sorted(all_elements, key=lambda r: (r['elem_det_regionIterator'][1], r['elem_det_regionIterator'][0]))
        interaction_elem_center_x, interaction_elem_center_y = get_bbox_center_pos(bbox_coords)
        before_page_info = []
        node_id = -1
        node_info = ''
        # 整理页面信息+匹配交互节点
        for node_i, element in enumerate(all_elements):
            before_page_info.append({
                'ID': node_i,
                'text': element.get('elem_detail_info', '')
            })
            x1, y1, x2, y2 = element['elem_det_regionIterator']
            if x1 <= interaction_elem_center_x <= x2 and y1 <= interaction_elem_center_y <= y2:
                node_id = node_i
                node_info = element.get('elem_detail_info', '')
        if node_id == -1:
            return 1, {'message': '根据坐标，未匹配到可交互节点!'}
        # 获取新页面文本信息
        new_page_text = visionui_client.get_long_page_ocr(image=image2, offset_y_w=0,
                                                    resize_w=1080, padding_right=0, always_split=False,
                                                    alpha=2.5, ocr_filter_score=0.6, business='traverse')['data']
        page_text_ = get_ocr_only_text_result(new_page_text)
        # llm预测节点功能
        node_description = get_node_description_by_llm(before_page_info, node_id, node_info)
        if node_description is not None:
            # llm推理交互是否符合预期
            rational_prediction = judging_rationality(node_description, page_text_)
            if rational_prediction is not None:
                if 'false' in rational_prediction or 'False' in rational_prediction:
                    return 0, {'result': False, 'reason': rational_prediction}
                elif 'true' in rational_prediction or 'True' in rational_prediction:
                    return 0, {'result': True, 'reason': rational_prediction}
            else:
                return 1, {'message': 'llm接口返回出错!'}
        else:
            return 1, {'message': 'llm接口返回出错!'}
    else:
        return 1, {'message': 'inspect接口出错!'}
    
    
