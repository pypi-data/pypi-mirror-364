import json

from tools.s3 import MssHHelper
from service.ui_detection.image_utils import draw_contours, image_preprocess
from service.ui_detection.horus_ocr import ClientHorus
from service.GPT import llmcore_completion
from service.lang_chain_utils.lion_client import client_prod as lion
import openai
import cv2


api_key = lion.config.get(f'{lion.app_name}.friday_appid', '0')
openai.api_key = api_key
openai.api_base = "https://aigc.sankuai.com/v1/openai/native"


def get_infer(img_path, long_page=True):
    result = []
    client_horus = ClientHorus()
    if long_page:
        ui_infer_result = client_horus.get_long_page_ui_infer(img_path, 0.5)
    else:
        ui_infer_result = client_horus.get_ui_infer(cv2.imread(img_path), cls_thresh=0.5)
    for infer in ui_infer_result['data']['recognize_results']:
        region = infer['elem_det_region']
        infer['rect'] = [round(i) for i in [region[0], region[1], region[2] - region[0], region[3] - region[1]]]
        result.append({'rect': infer['rect'], 'type': infer['elem_det_type']})
    return result


def upload_image(local_path, image_name):
    s3_client = MssHHelper()
    s3_client.bucket = s3_client.conn.get_bucket('vision-image')
    image_url = s3_client.save_to_mss(local_path, image_name)
    return image_url


def inspect_preview_image(local_path):
    img = cv2.imread(local_path)
    ret = get_infer(local_path)
    rects = [i['rect'] for i in ret if i['type'] == 'image' and i['rect'][2]/i['rect'][3] < 1.5]
    draw_contours(img, rects, type='w_h')
    img = cv2.resize(img, (0, 0), fx=0.5, fy=0.5)
    cv2.imwrite(local_path, img)


def gpt_vision(url):
    result = openai.ChatCompletion.create(
        model="gpt-4o-2024-08-06",
        temperature=0.1,
        messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "分析页面上所有蓝色框圈选的部分是否存在变形，展示不完全的情况"
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "detail": "high",
                        "url": url
                    }
                }
            ]
        }
    ]
    )
    return result['choices'][0]['message']['content']


def preview_image_detection(image_url):
    local_path, image_name = image_preprocess(image_url)
    inspect_preview_image(local_path)
    upload_image(local_path, image_name)
    r = gpt_vision(f"https://s3plus.meituan.com/vision-image/{image_name}")
    return generate_json_response(r, '形变，展示不完全的情况')


def generate_json_response(response, judgement=''):
    prompt = f"""
    判断以下描述表达的意是否存在{judgement}，以json形式返回
    === 描述 ===
    {response}
    === 结果 ===
    {{
     "status": 0-不存在/1-存在,
    }}
    """
    try:
        res = generate_query(prompt, model='gpt-4o-2024-08-06', response_format={"type": "json_object"})
        res = json.loads(res)
        res['message'] = response
    except Exception as e:
        res = {'status': 2}
    return res


def generate_query(prompt, model='gpt-3.5-turbo-1106', t=0.1, response_format=None):
    prompt = [
        {"role": "system", "content": prompt}
    ]
    r = llmcore_completion(prompt, business='sg_ui_detect', model=model, temperature=t, response_format=response_format)
    return r


def text_detection(image_url):
    local_path, image_name = image_preprocess(image_url)
    ocr_client = ClientHorus()
    r = ocr_client.get_ocr(cv2.imread(local_path))
    text_list = []
    for roi_text in r['data']['roi_text']:
        text_list.append(roi_text['text'])
    prompt = f"""
    提取以下文本列表中的所有表示价格的文本
    === 文本列表 ===
    {text_list}
    === 分析结果 ===
    """
    price_text = generate_query(prompt, model='gpt-4o-2024-08-06')
    prompt = f"""
    判断以下文本列表是否存在因展示不全打点结尾的情况
    === 文本列表 ===
    {price_text}
    === 结果 ===
    """
    res = generate_query(prompt, model='gpt-4o-2024-08-06')
    return generate_json_response(res, '文本因展示不全打点的情况')


if __name__ == '__main__':
    pass
