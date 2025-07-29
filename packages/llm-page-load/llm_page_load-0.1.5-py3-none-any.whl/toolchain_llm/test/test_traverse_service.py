import requests
import base64
import cv2
import numpy as np

def test_page_classification():
    url = 'http://127.0.0.1:8002/app_traversal_service/page_classification'

    test_img = cv2.imread('./data/test7-02.png')
    # 转为base64
    img_str = cv2.imencode('.png', test_img)[1].tobytes()
    img_str = base64.b64encode(img_str).decode()

    data = {
        'page': img_str,
        'type': 'test',
        'business': 'testtest'
    }

    response = requests.post(url, json=data)
    result = response.json()
    print(result)

def test_image_similarity():
    url = 'http://127.0.0.1:8002/app_traversal_service/image_similarity'

    test_img1 = cv2.imread('./data/test7-02.png')
    test_img2 = cv2.imread('./data/test7-03.png')
    # 转为base64
    img_str1 = cv2.imencode('.png', test_img1)[1].tobytes()
    img_str1 = base64.b64encode(img_str1).decode()
    img_str2 = cv2.imencode('.png', test_img2)[1].tobytes()
    img_str2 = base64.b64encode(img_str2).decode()

    data = {
        'image1': img_str1,
        'image2': img_str2,
        'business': 'testtest'
    }

    response = requests.post(url, json=data)
    result = response.json()
    print(result)
    
def test_interaction_check():
    # [250, 648, 419, 738]
    url = 'http://127.0.0.1:8002/app_traversal_service/interaction_check'
    before_img = cv2.imread('./data/before_0.png')
    after_img = cv2.imread('./data/after_0.png')
    # 转为base64
    img_str1 = cv2.imencode('.png', before_img)[1].tobytes()
    img_str1 = base64.b64encode(img_str1).decode()
    img_str2 = cv2.imencode('.png', after_img)[1].tobytes()
    img_str2 = base64.b64encode(img_str2).decode()

    data = {
        'image1': img_str1,
        'image2': img_str2,
        'bbox_coords': [250, 648, 419, 738],
        'business': 'testtest'
    }
    response = requests.post(url, json=data)
    result = response.json()
    print(result)
    
def test_page_inspect():
    url = 'http://127.0.0.1:8002/app_traversal_service/page_inspect'

    test_img = cv2.imread('./data/test7-02.png')
    # 转为base64
    img_str = cv2.imencode('.png', test_img)[1].tobytes()
    img_str = base64.b64encode(img_str).decode()

    data = {
        'page': img_str,
        'type': 'test',
        'business': 'testtest'
    }

    response = requests.post(url, json=data)
    result = response.json()
    print(result)
    
def test_image_diff():
    url = 'http://127.0.0.1:8002/ui_detection/image_diff'

    test_img1 = cv2.imread('./data/image_diff_test_01.png')
    # 转为base64
    img_str1 = cv2.imencode('.png', test_img1)[1].tobytes()
    img_str1 = base64.b64encode(img_str1).decode()
    
    test_img2 = cv2.imread('./data/image_diff_test_02.png')
    # 转为base64
    img_str2 = cv2.imencode('.png', test_img2)[1].tobytes()
    img_str2 = base64.b64encode(img_str2).decode()

    data = {
        'img1': img_str1,
        'img2': img_str2,
        'business': 'testtest'
    }

    response = requests.post(url, json=data)
    result = response.json()
    print(result)
    
if __name__ == "__main__":
    # test_page_classification()
    # test_image_similarity()
    # test_interaction_check()
    test_image_diff()