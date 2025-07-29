from PIL import Image
from service.app_traversal.visionui_client import visionui_client
from service.app_traversal.image_utils import get_ocr_only_text_result
import cv2
import numpy as np

def check_error_situations(page):
    """对当前页面结果进行分类

    Args:
        page (opencv image): 传入一个opencv打开的image

    Returns:
        result: False不存在问题 True存在问题
        type: 存在问题的描述
    """
    
    # 识别page的ocr信息
    page_text_ = visionui_client.get_long_page_ocr(image=page, offset_y_w=0,
                                                    resize_w=1080, padding_right=0, always_split=False,
                                                    alpha=2.5, ocr_filter_score=0.6, business='traverse')['data']
    page_text_ = get_ocr_only_text_result(page_text_)
    result, type = check_error(page, page_text_)
    return result, type

def check_error(page_img, page_text):
    if is_debuglink_page(page_text):
        return True, '停留扫码配置页'
    elif is_js_error(page_text):
        return True, 'JSError'
    elif is_load_failed(page_text):
        return True, '加载失败'
    elif check_white_page(page_img):
        return True, '白屏'
    elif check_black_page(page_img, page_text):
        return True, '黑屏'
    elif is_login_page(page_text):
        return True, '停留登录页'
    else:
        return False, ''


def check_white_page(page_img):
    # 将图片转换为单通道灰度图
    gray_img = cv2.cvtColor(page_img, cv2.COLOR_BGR2GRAY)
    # 获取灰度图矩阵的行数和列数
    r, c = gray_img.shape[:2]
    # 整个弧度图的像素个数为r*c
    piexs_sum = r * c
    # 获取偏暗的像素(表示236~255的灰度值为白 此处阈值可以修改
    white_points = (gray_img > 235)
    target_array = gray_img[white_points]
    wtite_sum = target_array.size
    # 判断灰度值为白的百分比
    white_prop = wtite_sum / (piexs_sum)
    # 计算std，取中间部分
    h = gray_img.shape[0]
    std = np.std(gray_img[150:h - 150, ])
    # 纯色std小于0.1，少量内容的页面std大于10，区分明显
    if white_prop > 0.9 and std < 1:
        return True
    return False

def check_black_page(page_img, page_txt):
    # 黑屏时，页面不应该存在文字
    if page_txt.strip():
        return False
    
    # 将图片转换为单通道灰度图
    gray_img = cv2.cvtColor(page_img, cv2.COLOR_BGR2GRAY)
    # 获取灰度图矩阵的行数和列数
    r, c = gray_img.shape[:2]
    # 整个弧度图的像素个数为r*c
    piexs_sum = r * c
    # 获取偏暗的像素(表示0~19的灰度值为暗) 此处阈值可以修改
    dark_points = (gray_img < 20)
    target_array = gray_img[dark_points]
    dark_sum = target_array.size
    # 判断灰度值为暗的百分比
    dark_prop = dark_sum / (piexs_sum)
    if dark_prop >= 0.85:
        return True
    else:
        return False

def is_app_home(texts):
    category_keyword_map = {
        '微信': ['微信团队'],
        '美团': ['外卖', '消息', '我的'],
        '点评': ['美食', '收藏', '我的'],
    }
    for app_key in category_keyword_map:
        find_all = True
        for text in category_keyword_map[app_key]:
            if text not in texts:
                find_all = False
                break
        if find_all:
            return True

def is_debuglink_page(texts):
    text_list = ['扫码配置']
    if text_list[0] in texts:
        return True
    else:
        return False

def is_login_page(texts):
    text_list = ['欢迎登录', '密码登录']
    if text_list[0] in texts:
        return True
    else:
        return False

def is_load_failed(texts):
    text_list = ['无法连接到网络', '努力加载中', '请求失败', '加载失败', '页面出错了', '重新加载', '检查网络']
    for text in text_list:
        if text in texts:
            return True
    return False

def is_js_error(texts):
    mrn_jserror = True
    text_list = ['Dismiss', 'Reload', 'Copy']
    for text in text_list:
        if text not in texts:
            mrn_jserror = False
    if mrn_jserror:
        return True
    mmp_jserror = True
    text_list = ['JS错误名称', 'JS错误堆栈']
    for text in text_list:
        if text not in texts:
            mmp_jserror = False
    if mmp_jserror:
        return True
    return False