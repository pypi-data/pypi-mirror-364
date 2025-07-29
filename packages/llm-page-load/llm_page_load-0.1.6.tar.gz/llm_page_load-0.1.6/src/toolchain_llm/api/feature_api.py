import copy
import time

from flask import jsonify
from flask import request
from flask import Blueprint
import json
import threading
import requests
import re
from utils import logger
from service.GPT import llmcore_completion
from service.lang_chain_utils.lion_client import client_prod as lion

feature_api = Blueprint('feature_api', __name__)


ignore_keys = ['Id', 'Url', '@', 'token', 'Token', 'uuid', 'Text', 'Number', 'number', 'cn_pt',
               'abStrategy', 'language', 'price', 'Price', 'Desc', 'Note', 'Title', 'time',
               'Time', 'Name', 'version', 'response.body.code', 'response.body.suc',
               'pagesize', 'Tips', 'abtest', 'csecpkgname', '__', 'Reason', 'Version']


def generate_query(prompt, model='gpt-3.5-turbo-1106', t=1.0, response_format=None):
    prompt = [
        {"role": "system", "content": prompt}
    ]
    r = llmcore_completion(prompt, business='feature_api', response_format=response_format, model=model,
                           max_token=8192, temperature=t)
    return r


def flatten_json(json_obj, parent_key='', results=None):

    if results is None:
        results = {}

    if isinstance(json_obj, dict):
        for key, value in json_obj.items():
            key = '[key]' if key.isdigit() else key
            new_key = "{}.{}".format(parent_key, key) if parent_key else key
            flatten_json(value, new_key, results)
    elif isinstance(json_obj, list):
        for i, value in enumerate(json_obj):
            if 'java' in str(value):
                continue
            new_key = "{}{}".format(parent_key, '[*]') if parent_key else '[*]'
            flatten_json(value, new_key, results)
    else:
        results[parent_key] = json_obj

    return results


def process_key_with_rule(appKey, param_keys):
    # duo rule
    duo = False
    if appKey in json.loads(lion.config.get(f'{lion.app_name}.feature_api_duo_app_keys', '[]')):
        duo = True
    for param_key in param_keys:
        if 'bizReq.environmentParam.duoCommonParam' in param_key:
            duo = True
            break
    if duo:
        rule_param_keys = []
        for param_key in param_keys:
            if 'bizReq.' in param_key or 'bizRes.' in param_key:
                rule_param_keys.append(param_key)
        param_keys = rule_param_keys
    return param_keys


def get_param_feature(contract_id, top, url, swimlane=None, chain=None):
    param_keys = []
    step = 25
    result_list = []
    appKey = ''
    headers = {'Content-Type': 'application/json;charset=utf-8'}
    if swimlane:
        headers['swimlane'] = swimlane
    if isinstance(contract_id, dict):
        service_url = url + '/third/random/contactInfp/caseDetail'
        params = {'appKey': contract_id['appkey'], 'url': contract_id['url'], 'method': contract_id['method'], 'top': top}
    else:
        service_url = url + '/third/random/caseDetail'
        params = {'contract-id': contract_id, 'top': top}
    res = requests.request('GET', url=service_url, params=params, headers=headers)
    res_data_list = json.loads(res.text)['data']
    if res_data_list:
        params = {}
        for res_data in res_data_list:
            try:
                appKey = res_data['appKey']
                request_json = json.loads(res_data['requestJson'])
                response_json = json.loads(res_data['responseJson'])
                params['responseJson.body'] = json.loads(response_json['body'])
                if request_json.get('queryParams'):
                    params['requestJson.queryParams'] = request_json.get('queryParams')
                if request_json.get('bodyParams'):
                    params['requestJson.bodyParams'] = request_json.get('bodyParams')
                if request_json.get('values'):
                    params['requestJson.values'] = json.loads(request_json.get('values')[0])
            except Exception as e:
                print(res_data)
            leaf_nodes = flatten_json(params)
            for path, value in leaf_nodes.items():
                if not any(s in path for s in ignore_keys) and \
                        not re.search(r'.*(?:id|List|No|Day|ID|title|desc)$', path):
                    if path not in param_keys:
                        if 'request' in path:
                            path = path.replace('[*][*]', '[1][*]')
                            path = path.replace('[*][*][*]', '[1][*][1]')
                        if chain and len(str(value)) < 10:
                            param_keys.append(f"{path}:{value}")
                        else:
                            param_keys.append(path)
        param_keys = process_key_with_rule(appKey, param_keys)
        if chain:
            return param_keys
        for i in range(0, len(param_keys), step):
            path_s = '\n'.join(param_keys[i:i + step])
            prompt = f"""
                    请给以下字段列表补充说明
                    ===字段列表===
                    {path_s}
                    ===字段和说明===
                    """
            r = generate_query(prompt, model='gpt-4o-mini', t=0.1)
            prompt = f"""
                    请分析以下参数列表，按照分析规则判断参数是否可以作为接口参数的有效特征，输出有效特征
                    === 参数列表 ===
                    {r}
                    === 分析规则 ===
                    **有效特征**：
                      - 表示模式、状态码、是否开启某功能的参数
                      - 表示规则，分类和类型相关的参数
                    **无效特征**:
                     - 表示单纯的数量信息，如个人信息，售价，数量，经纬度，日期这些属于无效特征
                     - 表示和外观相关信息，如表示文案，标题这些是无效特征
                     === 输出结果 ===
                     参数名
                    """
            r = generate_query(prompt, model='gpt-4o-2024-08-06', t=0.1)
            prompt = f"""
            请给以下字段列表补充说明
            ===字段列表===
            {r}
            ===字段和说明===
            字段名 - 说明
            """
            r1 = generate_query(prompt, model='gpt-4o-mini', t=0.1)
            r1 = r1.split('\n')
            for param_k in r1:
                param_k = param_k.replace(':', "-")
                param_k = param_k.replace('：', "-")
                param_k = re.sub(r'^[^a-zA-Z]+', '', param_k)
                if len(param_k) > 1:
                    result_list.append(param_k)
    else:
        result_list.append(res.text)
    return result_list


def get_chain_feature_call_back(call_back_url, env, swimlane, task_id, contracts, chain_id):
    contracts_c = copy.deepcopy(contracts)
    feature_result = []
    for c in contracts_c:
        c['target'] = []
        feature_result.append(c)
    for i, contract in enumerate(contracts):
        if "target" in contract.keys() and len(contract['target']) > 0:
            targets = contract['target']
            input_feature = ''
            for target in targets:
                input_feature = input_feature + f"{target['field']}-{target['desc']}\n"
            contract_id_list = [contracts[i] for i in range(i, -1, -1)]
            r = get_contract_feature(contract_id_list, input_feature, 10,
                                  "https://we.sankuai.com" if env == "prod" else "https://we.dzu.test.sankuai.com",
                                  swimlane=swimlane)
            for k in r.keys():
                feature_result[k]['target'].append(r[k])

    # call back
    if task_id == 1000:
        print(json.dumps(feature_result, indent=4))
    else:
        headers = {'Content-Type': 'application/json'}
        if swimlane:
            headers['swimlane'] = swimlane
        payload = {'chainId': chain_id, 'taskId': task_id, 'contracts': feature_result}
        response = requests.post(call_back_url, data=json.dumps(payload), headers=headers, timeout=10)
        logger.info(f"[feature api][task id:{task_id}][payload:{payload}][call back:{response.text}]")


def get_contract_feature(contract_list, input_feature, top, url, swimlane=None):
    result = {}
    for contract_id in contract_list:
        contract_index = contract_id['index']
        api_key_list = get_param_feature(contract_id, top, url, swimlane, chain=True)
        prompt = f"""
        给你一个字段的列表，在列表中查找跟目标字段语义相同的字段,返回json
        ===字段列表===
        字段名:值
        {api_key_list}
        ===目标字段列表===
        目标字段名 - 目标描述
        {input_feature}
        ===查找规则===
        1.优先根据字段名查找,名称相同,查到1个可以停止
        2.然后根据字段值的语义查找，查到1个可以停止
        ===查找结果===
        searchResultList:[
        field - 从字段列表中找到的字段名，没有找到填'NULL'
        desc - 目标描述
        success - true-存在 / false-不存在
        reason - 说明]
        """
        r = generate_query(prompt, model='gpt-4.1', t=0.1, response_format={"type": "json_object"})
        query_result = []
        query_feature = []
        for i in json.loads(r)['searchResultList']:
            i['field'] = i['field'].split(':')[0]
            query_result.append(i)
            query_feature.append(f"{i['fieldName']}-{i['desc']}")
        result[contract_index] = query_result
        input_feature = query_feature
    return result


def get_feature_call_back(contract_ids, task_id, env, swimlane=None):
    ret = {}
    url = "https://we.sankuai.com" if env == "prod" else "https://we.dzu.test.sankuai.com"
    for contract_id in contract_ids:
        result = get_param_feature(contract_id, 2, url, swimlane)
        ret[contract_id] = result
    headers = {'Content-Type': 'application/json'}
    if swimlane:
        headers['swimlane'] = swimlane
    payload = {'task_id': task_id, 'data': ret}
    response = requests.post(url + "/open-api/LLM/feature-field", data=json.dumps(payload), headers=headers, timeout=10)
    logger.info(f"[feature api][task id:{task_id}][payload:{payload}][call back:{response.text}]")


@feature_api.route('', methods=['POST'])
def get_feature():
    contract_ids = request.json.get('contract_ids')
    env = request.json.get('env')
    swimlane = request.json.get('swimlane')
    task_id = str(time.time()).split(".")[1]
    thread = threading.Thread(target=get_feature_call_back, args=(contract_ids, task_id, env, swimlane))
    thread.start()
    logger.info(f"[feature api][task id:{task_id}][contrack id:{contract_ids}]")
    return jsonify({"task_id": task_id})


@feature_api.route('chain', methods=['POST'])
def get_chain_feature():
    contracts = request.json.get('contracts')
    env = request.json.get('env')
    swimlane = request.json.get('swimlane')
    chain_id = request.json.get('chainId')
    call_back_url = request.json.get('call_back_url')
    task_id = str(time.time()).split(".")[1]
    thread = threading.Thread(target=get_chain_feature_call_back, args=(call_back_url, env, swimlane, task_id,
                                                                        contracts, chain_id))
    thread.start()
    logger.info(f"[feature api][task id:{task_id}][request:{request.json}]")
    return jsonify({"task_id": task_id})


if __name__ == '__main__':
    # contract_id = '4935'
    # contract_id = '2752'
    contract_id = '3685'
    # r = get_param_feature(contract_id, 5, url="http://we.sankuai.com")
    contracts = [
        {'index': 0, 'appkey': 'com.sankuai.mptrade.hotel.apic', 'url': '/hotelorder/hotelordercreateorder.json', 'method': 'post', 'target': []},
        {'index': 1, 'appkey': 'com.sankuai.mptrade.hotel.generaltrade', 'url': 'com.sankuai.nibtp.trade.hotel.general.trade.client.service.GeneralTradeBuyService', 'method': 'createOrder', 'target': []},
        {'index': 2, 'appkey': 'com.sankuai.mptrade.hotel.aggregate', 'url': 'com.meituan.nibtp.trade.hotel.aggregate.client.service.IOpOrder4CService', 'method': 'createOrder', 'target': []},
        {'index': 3, 'appkey': 'com.sankuai.mptrade.buy.process', 'url': 'com.meituan.nibtp.trade.client.buy.service.CreateOrderService', 'method': 'createOrder', 'target': [{'field': 'request.environmentSDO.channel', 'desc': '客户端平台', 'success': None, 'reason': None}, {'field': 'request.environmentSDO.platform', 'desc': '渠道', 'success': None, 'reason': None}]}
    ]
    get_chain_feature_call_back('call_back_url', 'test', 'wanganqiang-brgnn', 1000, contracts, 123)
