import cv2
import time
import os
from service.app_traversal.visionui_client import visionui_client
from utils import logger

def get_page_inspect(page):
    """基于Image对当前页面进行元素检测，返回识别到的元素

    Args:
        page (opencv image): 传入一个opencv打开的image

    Returns:
        result: inspect识别结果
    """
    # 将图像进行本地保存
    logger.info(f'[page_inspect]: 图片本地保存')
    current_timestamp = str(int(time.time()*1000))
    app_traversal_dir = os.path.dirname(os.path.realpath(__file__))
    temp_dir = os.path.join(app_traversal_dir, 'temp')
    image1_local_temp_pth = os.path.join(temp_dir, f'{current_timestamp}_image1.png')
    cv2.imwrite(image1_local_temp_pth, page)
    # 进行元素识别
    logger.info(f'[page_inspect]: 元素识别')
    visionui_inspect = visionui_client.get_inspect(image1_local_temp_pth, 'inspect')
    # 删除本地图像
    os.remove(image1_local_temp_pth)
    # 返回结果
    return visionui_inspect

    