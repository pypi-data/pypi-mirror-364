import re
import random
import utils

keywords = utils.read_json('scenetivity/keywords.json')
name_list = utils.read_json('scenetivity/name_list.json')
biz_replacer = utils.read_json('scenetivity/biz_name_replacer.json')
measure_words = utils.read_json('scenetivity/measure_words.json')
coe_level = utils.read_json('scenetivity/coe_level.json')
porsche = utils.read_json('scenetivity/prosche.json')


def shuffle_cut(string, length=0):
    """
    打乱字符串
    """
    if length == 0:
        length = len(string)//3*2 if len(string)//3*2 > 0 else 1
    lst = list(string)
    # 打乱列表
    random.shuffle(lst)
    # 将列表转换为字符串
    return ''.join(lst[:length])


def find_name(text):
    for key in name_list:
        text = re.sub(key, shuffle_cut(key), text)

    return text


def find_coe_level(text):
    for k, v in coe_level.items():
        text = re.sub(k, v, text)
    return text


def find_version(text):
    pattern = r"\d+\.\d+\.\d+"
    text = re.sub(pattern, '**.**.**', text)
    return text


def find_card_number(text):
    """
    判断是否为合法的银行卡号
    """
    pattern = r'^\d{16}|\d{19}$'
    find_list = re.findall(pattern, text)
    for find in find_list:
        text = re.sub(find, shuffle_cut(find), text)
    return text


def find_appid_floatnumber(text):
    '''
    找 app ID 和 浮点数
    '''
    pattern = r"([a-zA-Z0-9]+\.)+[a-zA-Z0-9]+"
    text = re.sub(pattern, '**.***.*****', text)
    return text


def find_city(text):
    city_list = utils.read_json('scenetivity/city_list.json')
    for city in city_list:
        text = re.sub(city, '某城市', text)
    return text


def find_phone_number(text):
    """
    判断是否为合法的中国手机号
    如果有一些连续的一串数字，也会被替换
    """
    pattern = r'^1[3-9]\d{9}\$'
    find_list = re.findall(pattern, text)
    for find in find_list:
        text = re.sub(find, shuffle_cut(find), text)
    pattern = r'\d{11}'
    find_list = re.findall(pattern, text)
    for find in find_list:
        text = re.sub(find, find[0]+'***'+find[-1], text)
    return text


def find_email(text):
    pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z0-9]+"
    text = re.sub(pattern, '(某邮箱)', text)
    return text


def find_url(text):
    pattern = r"(https?://[a-zA-Z0-9./]+(\?[a-zA-Z0-9._\-%+-=&]*)?(#[a-zA-Z0-9._\-%+-=&]*)?)"
    text = re.sub(pattern, "(某链接)", text)
    return text


def find_measure_words(text):
    for key in measure_words:
        # 数字在前
        pattern = r"(\d+)(.{0,15})?"+key
        find_list = re.findall(pattern, text)
        for number, measure in find_list:
            text = re.sub(re.escape(f"{number}{measure}{key}"), number[0]+'*'+f"{measure}{key}", text)
        # 数字在后
        pattern = key+r"(\D{0,15})?(\d+)"
        find_list = re.findall(pattern, text)
        for measure, number in find_list:
            text = re.sub(re.escape(f"{key}{measure}{number}"), f"{key}{measure}"+number[0]+'*', text)
    return text


def find_key_words(text):
    '''
    替换剩下的关键字
    '''
    for key in keywords:
        text = re.sub(key, shuffle_cut(key), text)
    return text


def find_biz_name(text):
    for key, value in biz_replacer.items():
        text = re.sub(key, value, text)
    return text


def find_porsche(text):
    for key, value in porsche.items():
        text = re.sub(key, value, text)
    return text


def replace(text, level=1):
    if text is None:
        return text
    function_level_map = map()
    for function_level in function_level_map:
        if (function_level['level'] > level):
            continue
        for function in function_level['functions']:
            text = eval(function)(text)
    return text


def map():
    return [
        {
            'level': 1,
            'desc': "必须优先替换",
            'functions': [
                'find_email',
                'find_url',
                'find_measure_words',
                'find_phone_number',
                'find_card_number',
                'find_coe_level',
                'find_porsche'
            ]
        },
        {
            'level': 2,
            'desc': '不是特别必要替换，有些依赖于替换列表，在1替换完以后再替换',
            'functions': [
                'find_appid_floatnumber',
                'find_biz_name',
                'find_key_words',
                'find_name',
                'find_version',
            ]
        },
        {
            'level': 3,
            'desc': '可以不替换',
            'functions': ['find_city']
        }
    ]
