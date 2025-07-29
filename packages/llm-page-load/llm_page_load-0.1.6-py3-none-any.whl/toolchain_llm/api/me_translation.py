from flask import jsonify
from flask import request
from flask import Blueprint
from service.GPT import llmcore_completion
from tools.dx import send_dx_message_to_person
import json
import re
import threading
import time
import requests

me_translation = Blueprint('me_translation', __name__)


def get_text_key_list(name_space_id, i18n_cookie):
    header = {
        'Content-Type': 'application/json',
        'Cookie': i18n_cookie
    }
    url = "https://i18n.mykeeta.sankuai.com/api/i18n_admin/v1/namespace/queryNamespaceDetail"
    payload = {"namespaceId": name_space_id}
    resp = requests.request('POST', url=url, data=json.dumps(payload), headers=header)
    project_id = json.loads(resp.text)['data']['projectId']
    name_space_key = json.loads(resp.text)['data']['namespaceKey']
    url = "https://i18n.mykeeta.sankuai.com/api/i18n_admin/v1/text/queryTextList"
    payload = {
        "projectId": project_id,
        "locale": "zh-CN",
        "namespaceId": name_space_id,
        "pageNum": 1,
        "pageSize": 10000,
        "keyText": None
    }
    resp = requests.request('POST', url=url, data=json.dumps(payload), headers=header)
    text_list = [i['targetText'] for i in json.loads(resp.text)['data']['resultList']]
    return text_list, name_space_key


def generate_query(prompt, model='gpt-3.5-turbo-1106', t=0.1):
    prompt = [
        {"role": "system", "content": prompt}
    ]
    r = llmcore_completion(prompt, business='me_translation', model=model, temperature=t)
    return r


def get_translation(text_key, name_space_id, locate):
    ret = ''
    for _ in range(3):
        try:
            url = f"http://client.hotel.test.sankuai.com/me/getText?key={text_key}&nameSpaceId={name_space_id}&locate={locate}"
            res = requests.request('GET', url=url, timeout=15)
            ret = res.text
            break
        except Exception as e:
            time.sleep(2)
    return ret


def val_text_key(text_key, name_space_id, selected_language):
    text = get_translation(text_key, name_space_id, 'zh-CN')
    a = json.loads(text)['text']
    b = ""
    for language in selected_language:
        k = language.split(":")[0]
        v = language.split(":")[1]
        text = get_translation(text_key, name_space_id, v)
        b = b+f"{k}-{json.loads(text)['text']}\n"
    prompt = f"""
    你作为专业翻译人员，以下是原文和目标语言的翻译结果，指出翻译结果有明显错误的地方，按回答方式生成结果
    === 原文 ===
    {a}
    === 翻译结果 ===
    目标语言 - 翻译结果
    {b}
    === 回答方式 ===
    总体结果 - 对/错
    原因 - 如有错误简单解释
    """
    res = generate_query(prompt, model='gpt-4o-2024-08-06')
    result = f"""
    ===  原文  ===
    {a}
    ===  翻译  ===
    {b}
    ===  分析结果  ===
    {res}
    """
    return result


def split_text_into_paragraphs(text):
    # 使用正则表达式匹配带下划线的英文作为分段标志
    paragraph_pattern = re.compile(r'([a-zA-Z]+(?:_[a-zA-Z_]*[a-zA-Z]))')
    # 找到所有匹配的位置
    matches = list(paragraph_pattern.finditer(text))
    paragraphs = []

    # 根据匹配的位置分割文本
    for i in range(len(matches)):
        start = matches[i].start()
        # 如果不是最后一个匹配，结束位置是下一个匹配的开始位置
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        paragraphs.append(text[start:end].strip())
    return paragraphs


def text_process(text, task_id, group_text):
    paragraphs = split_text_into_paragraphs(text)
    k = 0
    result = ''
    for i, paragraph in enumerate(paragraphs):
        if "结果 - 对" not in paragraph:
            k = k + 1
            result = result + f"\n\n{k}."
            result = result + paragraph + '\n'
    if len(result) > 5:
        result = f"【ME多语言翻译】分析结果，TaskId {task_id}，分组 {group_text}，以下翻译可能是有问题的："+result
    else:
        result = f"【ME多语言翻译】分析结果，TaskId {task_id}，分组 {group_text}，所有翻译结果没有明显错误。"
    return result


def val_translate(project_name, text_key_list, selected_language, task_id, mis_name):
    try:
        text_key_list_group = [text_key_list[i:i + 15] for i in range(0, len(text_key_list), 15)]
        for group_i, text_key_group in enumerate(text_key_list_group):
            result = ''
            for i, text_key in enumerate(text_key_group):
                try:
                    result = result + text_key
                    val_text = val_text_key(text_key, project_name, selected_language)
                    val_text = re.sub(r'\n(?=\n)', '', val_text)
                    val_text = re.sub(r'\n +', '\n', val_text)
                    result = result + val_text + '\n\n'
                    if i % 10 == 0:
                        time.sleep(5)
                except Exception as e:
                    result = result + "没有发布\n\n"
            text = text_process(result, task_id, f"{group_i+1}/{len(text_key_list_group)}")
            send_dx_message_to_person(mis_name, text)
    except Exception as e:
        send_dx_message_to_person('jinhailiang', f"[ME多语言] {repr(e)}")


@me_translation.route('val_translation', methods=['POST'])
def translation_check():
    project_name = request.json.get('nameSpaceKey')
    text_key_list = request.json.get('textKeyList')
    selected_language = request.json.get('selectedLanguage')
    mis_name = request.json.get('misName')
    task_id = str(time.time()).split(".")[1]
    thread = threading.Thread(target=val_translate, args=(project_name, text_key_list, selected_language, task_id, mis_name))
    thread.start()
    send_dx_message_to_person(mis_name, f"【ME多语言翻译】提交成功，TaskId {task_id}，总计{len(text_key_list)}个TextKey，"
                                        f"预计时间{6*len(text_key_list)}s，请等待")
    response = jsonify({"code": 0})
    response.headers['Content-Type'] = 'application/json; charset=utf-8'
    return response


@me_translation.route('getTextKeyList', methods=['POST'])
def get_feature():
    nameSpaceId = request.json.get('nameSpaceId')
    i18n_cookie = request.json.get('i18nCookie')
    text_key_list, name_space_key = get_text_key_list(nameSpaceId, i18n_cookie)
    response = jsonify({
        "code": 0,
        "data": {"textKeyList": text_key_list, "nameSpaceKey": name_space_key}
    })
    response.headers['Content-Type'] = 'application/json; charset=utf-8'
    return response
