import requests
import time
import json
from llmcore_sdk.models.friday import Friday
from PIL import Image
import io
import base64
import openai
import cv2
from service.lang_chain_utils.lion_client import client_prod as lion


api_key = lion.config.get(f'{lion.app_name}.friday_appid', '0')
openai.api_key = api_key
openai.api_base = "https://aigc.sankuai.com/v1/openai/native"


def llmcore_completion(message, business, model='gpt-4o-mini', max_token=4096, temperature=0.1,
                       response_format=None, functions=None):
    friday = Friday(
        model=model,
        max_tokens=max_token,
        temperature=temperature,
        direction=business,
    )
    ret = friday.complex_chat(messages=message, response_format=response_format, functions=functions)
    return ret


def create_conversation(prompt, content, **kwargs):
    system_content = prompt['system'].replace('$CONTENT', str(content))
    for k in kwargs:
        system_content = system_content.replace('$' + k, str(kwargs[k]))
    user_content = prompt['user'].replace('$CONTENT', str(content))
    for k in kwargs:
        user_content = user_content.replace('$'+k, str(kwargs[k]))
    conversation = [
        {"role": "system", "content": system_content},
        {"role": "user", "content": user_content}
    ]
    return conversation


def mt_chat_inference(message, model="LongCat-7B-32K-Chat", temperature=0.01, max_tokens=300):
    url = "https://aigc.sankuai.com/v1/host-model/sankuai/inference"
    headers = {
        "Content-Type": "application/json;charset=UTF-8",
        "appId": lion.config.get(f'{lion.app_name}.friday_appid', '0')
    }
    data = {
        "messages": message,
        "model": model,
        "temperature": temperature,
        "max_tokens": max_tokens
    }
    result = {'status': 0}
    resp = ''
    friday = Friday(model, max_tokens=max_tokens, temperature=temperature)
    timing = time.time()
    for _ in range(2):
        try:
            resp = requests.post(url, headers=headers, data=json.dumps(data))
            result = json.loads(resp.text)
            if not result['data']:
                result['data'] = {'result': result['message']}
            break
        except Exception as e:
            print(f"Model interface:{resp.text}")
            result['status'] = 1
            result['message'] = repr(e)
    friday._calculate_cost_(model, result, timing=timing)  # 上报计费
    return result


def encode_image(pil_image):
    if pil_image.mode == "RGBA":
        pil_image = pil_image.convert("RGB")
    buffer = io.BytesIO()
    pil_image.save(buffer, format="JPEG")
    return base64.b64encode(buffer.getvalue()).decode('utf-8')


def gpt_v(image_cv, prompt, model="gpt-4.1", business='local_test', temperature=0.2):
    rgb_image = cv2.cvtColor(image_cv, cv2.COLOR_BGR2RGB)
    pil_image = Image.fromarray(rgb_image)
    base64_image = encode_image(pil_image)
    friday = Friday(model=model, direction=business)
    start_time = time.time()
    result = openai.ChatCompletion.create(
        model=model,
        messages=[{"role": "user", "content": [
            {"type": "text",
             "text": prompt},
            {"type": "image_url",
             "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}},
            ],
        }],
        temperature=temperature
    )
    friday._calculate_cost_('gpt-4o-2024-08-06', result, start_time)
    content = result.choices[0].message.content
    return content


if __name__ == '__main__':
    pass
