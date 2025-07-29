import json
import re
import time
from copy import deepcopy
from datetime import datetime

import requests
import subprocess
import threading
from llmcore_sdk import utils
# from utils import logger


class LyrebirdClient:
    """Lyrebird API 客户端，提供与 Lyrebird 服务交互的接口"""
    
    # 常量定义
    GROUP_INFO_KEYS = {'id', 'name', 'parent_id', 'operator_id', 'children', 'scene_id', 'update_time'}
    SELECTED_FILTERS = {"Simple", "Testability", "All"}
    
    # Debug Link 相关模板
    DEBUG_LINK_RESPONSE_DATA_TEMPLATE = [
        {
            "type": "mock",
            "info": {
                "value": "http://{{ip}}:{{config.get('extra.mock.port')}}/"
            },
            "desc": "mock:The ip of mock serve"
        },
        {
            "type": "reportresult",
            "info": {
                "value": 1
            },
            "desc": "是否通过bable上报结果:1--上报结果 0--不上报结果"
        },
        {
            "type": "scheme",
            "info": {
                "value": "imeituan://www.meituan.com/gc/poi/detail?id=123456&shopId=123456"
            },
            "desc": "The scheme of target page"
        },
        {
            "type": "signin",
            "info": {
                "account": "17344473050",
                "countryCode": "86",
                "password": "jiulv888",
                "signin": 1
            },
            "desc": "请保证此项的countryCode,account和password正确且不为空. 登录,signin:登录标志(默认是true),countryCode:登录区号,account:登录账号,password:登录密码"
        }
    ]
    
    DEBUG_LINK_TEMPLATE = {
        "name": "debug-link",
        "rule": {
            "request.url": "(?=.*debug-link$)|(?=.*debug-link\\?)"
        },
        "request": {
            "url": "debug-link",
            "headers": {},
            "method": "GET"
        },
        "response": {
            "code": 200,
            "headers": {
                "Connection": "keep-alive",
                "Content-Type": "application/json;charset=utf-8"
            },
            "data": {}
        },
        "lyrebirdInternalFlow": "agent"
    }

    def __init__(self, url=None, default_node=None):
        """
        初始化 Lyrebird 客户端
        
        参数:
            url: str, 可选, Lyrebird 服务的 URL 地址
            default_node: str, 可选, 默认创建数据组的节点 ID
        """
        self.url = ''
        self.default_node_id = ''
        self.apis = {}
        self.config = {}
        
        if url and default_node:
            self.init(url, default_node)
    
    def init(self, url, default_node):
        """
        初始化 Lyrebird 客户端配置
        
        参数:
            url: str, Lyrebird 服务的 URL 地址
            default_node: str, 默认创建数据组的节点 ID
        """
        self.url = url
        self.default_node_id = default_node
        self.apis = {
            'mock_group': f'{self.url}/api/group',
            'mock_data': f'{self.url}/api/data',
            'flow': f'{self.url}/api/flow',
            'flow_list': f'{self.url}/api/flow/search',
            'save_flow': f'{self.url}/api/flow/save',
            'event_channel': f'{self.url}/api/event/channel',
            'activate_mock_group': f'{self.url}/api/mock',
            'deactivate_mock_group': f'{self.url}/api/mock/group/deactivate',
            'cut_group': f'{self.url}/api/cut',
            'paste_group': f'{self.url}/api/paste',
            'get_lyrebird_config': f'{self.url}/api/conf',
        }
        
        config_response = self._get_lyrebird_config()
        if not config_response['status']:
            raise Exception(config_response['message'])
        else:
            self.config = config_response['message']
    
    def _http_connection(self, method, url, json_data=None, params=None):
        """
        通用 HTTP 请求方法
        
        参数:
            method: str, 请求方法 (GET, POST, PUT, DELETE)
            url: str, 请求 URL
            json_data: dict, 可选, JSON 请求体
            params: dict, 可选, URL 参数
            
        返回值:
            dict: 包含以下字段的字典
                status: bool, 请求是否成功
                message: 成功时为响应数据，失败时为错误信息
        """
        try:
            if method.upper() == 'GET':
                res = requests.get(url, params=params)
            elif method.upper() == 'POST':
                if json_data:
                    res = requests.post(url, json=json_data)
                else:
                    res = requests.post(url)
            elif method.upper() == 'PUT':
                if json_data:
                    res = requests.put(url, json=json_data)
                else:
                    res = requests.put(url)
            elif method.upper() == 'DELETE':
                res = requests.delete(url)
            else:
                return {'status': False, 'message': f'不支持的HTTP方法: {method}'}
            
            if res.status_code == 200:
                return {'status': True, 'message': res.json()}
            else:
                return {'status': False, 'message': str(res.json())}
        except Exception as e:
            return {'status': False, 'message': str(e)}
    
    def _get_lyrebird_config(self):
        """获取 Lyrebird 配置信息"""
        response = self._http_connection('GET', self.apis['get_lyrebird_config'])
        if response['status']:
            return {'status': True, 'message': response['message']}
        return response
    
    def _add_mock_group(self, name, parent_id):
        """
        添加 mock 数据组
        
        参数:
            name: str, 数据组名称
            parent_id: str, 父节点 ID
        """
        if not name:
            return {'status': False, 'message': 'name is required'}
        if not parent_id:
            return {'status': False, 'message': 'parent_id is required'}

        response = self._http_connection('POST', self.apis['mock_group'], json_data={'name': name, 'parent_id': parent_id})
        if response.get('message', {}).get('code') != 1000:
            return {'status': False, 'message': response.get('message')}
        if response['status']:
            group_id = response['message']['data']['group_id']
            return {'status': True, 'message': {'group_id': group_id}}
        return response
    
    def _add_mock_data(self, name, parent_id, data=None):
        """
        添加 mock 数据
        
        参数:
            name: str, 数据名称
            parent_id: str, 父节点 ID
            data: dict, 可选, 数据内容
        """
        if not name:
            return {'status': False, 'message': 'name is required'}
        if not parent_id:
            return {'status': False, 'message': 'parent_id is required'}

        if not data:
            data = {
                'parent_id': parent_id, 
                'data': {
                    'name': name,
                    'type': 'data'
                }
            }
        
        response = self._http_connection('POST', self.apis['mock_data'], json_data=data)
        if response.get('message', {}).get('code') != 1000:
            return {'status': False, 'message': response.get('message')}
        if response['status']:
            data_id = response['message']['data_id']
            return {'status': True, 'message': {'data_id': data_id}}
        return response
    
    def _update_mock_data(self, data_id, data):
        """
        更新 mock 数据
        
        参数:
            data_id: str, 数据 ID
            data: dict, 更新数据
        """
        if not data_id:
            return {'status': False, 'message': 'data_id is required'}
        if not data:
            return {'status': False, 'message': 'data is required'}

        response = self._http_connection('PUT', self.apis['mock_data'], json_data=data)
        if response.get('message', {}).get('code') != 1000:
            return {'status': False, 'message': response.get('message')}
        if response['status']:
            return {'status': True, 'message': 'success'}
        return response
    
    def _get_mock_group_info(self, group_id):
        """
        获取 mock 数据组信息
        
        参数:
            group_id: str, 数据组 ID
        """
        if not group_id:
            return {'status': False, 'message': 'group_id is required'}

        response = self._http_connection('GET', f'{self.apis["mock_group"]}/{group_id}')
        if response.get('message', {}).get('code') != 1000:
            return {'status': False, 'message': response.get('message')}
        if response['status']:
            data = response['message']['data']
            group_info = {}
            for key, value in data.items():
                if key in self.GROUP_INFO_KEYS:
                    group_info[key] = value
                elif 'debug_link' in key:
                    group_info[key] = value
                elif 'urlscheme' in key:
                    group_info[key] = value
            return {'status': True, 'message': group_info}
        return response
    
    def _get_mock_data_info(self, data_id):
        """
        获取 mock 数据信息
        
        参数:
            data_id: str, 数据 ID
        """
        if not data_id:
            return {'status': False, 'message': 'data_id is required'}
        
        response = self._http_connection('GET', f'{self.apis["mock_data"]}/{data_id}')
        if response.get('message', {}).get('code') != 1000:
            return {'status': False, 'message': response.get('message')}
        if response['status']:
            return {'status': True, 'message': response['message']['data']}
        return response
    
    def _get_flow_list(self, flow_type='Simple'):
        """
        获取 flow 列表
        
        参数:
            flow_type: str, 过滤类型
        """
        if flow_type not in self.SELECTED_FILTERS:
            return {'status': False, 'message': 'flow_type is invalid'}

        if flow_type == 'All':
            flow_type = ''
        
        response = self._http_connection('POST', self.apis['flow_list'], json_data={"selectedFilter": flow_type})
        if response['status']:
            return {'status': True, 'message': response['message']}
        return response
    
    def _get_flow_detail(self, flow_id):
        """
        获取 flow 详情
        
        参数:
            flow_id: str, 请求 ID
        """
        if not flow_id:
            return {'status': False, 'message': 'flow_id is required'}

        response = self._http_connection('GET', f'{self.apis["flow"]}/{flow_id}')
        if response.get('message', {}).get('code') != 1000:
            return {'status': False, 'message': response.get('message')}
        if response['status']:
            return {'status': True, 'message': response['message']['data']}
        return response
    
    def _save_by_flow_ids(self, group_id, flow_ids):
        """
        通过 flow ID 保存 mock 数据
        
        参数:
            group_id: str, 数据组 ID
            flow_ids: list, 请求 ID 列表
        """
        if not group_id:
            return {'status': False, 'message': 'group_id is required'}
        if not flow_ids:
            return {'status': False, 'message': 'flow_ids is required'}

        response = self._http_connection('POST', self.apis['save_flow'], json_data={"ids": flow_ids})
        if response.get('message', {}).get('code') != 1000:
            return {'status': False, 'message': response.get('message')}
        if response['status']:
            return {'status': True, 'message': response['message']}
        return response
    
    def _activate_group(self, group_id):
        """
        激活 mock 数据组
        
        参数:
            group_id: str, 数据组 ID
        """
        if not group_id:
            return {'status': False, 'message': 'group_id is required'}

        response = self._http_connection('PUT', f'{self.apis["activate_mock_group"]}/{group_id}/activate')
        if response.get('message', {}).get('code') != 1000:
            return {'status': False, 'message': response.get('message')}
        if response['status']:
            return {'status': True, 'message': 'success'}
        return response
    
    def _deactivate_group(self):
        """停用 mock 数据组"""
        response = self._http_connection('PUT', f'{self.apis["deactivate_mock_group"]}')
        if response.get('message', {}).get('code') != 1000:
            return {'status': False, 'message': response.get('message')}
        if response['status']:
            return {'status': True, 'message': 'success'}
        return response
    
    def _delete_mock_group(self, group_id):
        """
        删除 mock 数据组
        
        参数:
            group_id: str, 数据组 ID
        """
        if not group_id:
            return {'status': False, 'message': 'group_id is required'}
        
        response = self._http_connection('DELETE', f'{self.apis["mock_group"]}/{group_id}')
        if response.get('message', {}).get('code') != 1000:
            return {'status': False, 'message': response.get('message')}
        if response['status']:
            return {'status': True, 'message': 'success'}
        return response
    
    def _cut_mock_group(self, group_id):
        """
        剪切 mock 数据组
        
        参数:
            group_id: str, 数据组 ID
        """
        if not group_id:
            return {'status': False, 'message': 'group_id is required'}
        
        response = self._http_connection('PUT', f'{self.apis["cut_group"]}/{group_id}')
        if response.get('message', {}).get('code') != 1000:
            return {'status': False, 'message': response.get('message')}
        if response['status']:
            return {'status': True, 'message': 'success'}
        return response
    
    def _paste_mock_group(self, group_id):
        """
        粘贴 mock 数据组
        
        参数:
            group_id: str, 数据组 ID
        """
        if not group_id:
            return {'status': False, 'message': 'group_id is required'}
        
        response = self._http_connection('PUT', f'{self.apis["paste_group"]}/{group_id}')
        if response.get('message', {}).get('code') != 1000:
            return {'status': False, 'message': response.get('message')}
        if response['status']:
            return {'status': True, 'message': 'success'}
        return response
    
    # 以下是公开的 API 方法
    
    def create_group(self, name=None, parent_id=None, debug_link=None):
        """
        创建一个 mock 数据组
        
        参数:
            name: str, 可选, mock 组名称, 默认以当前时间命名
            parent_id: str, 可选, 父节点 ID, 默认 init 全局配置的节点
            debug_link: list, 可选, debuglink 配置, 默认为空
            
        返回值:
            dict: 包含以下字段的字典
                status: bool, 操作是否成功
                message: dict, 包含以下字段:
                    group_id: str, 创建的 mock 组 ID
                    scene_id: str, 场景 ID
                    group_name: str, mock 组名称
        """
        if not name:
            name = datetime.now().strftime('%Y%m%d-%H-%M-%S')
        if parent_id is None:
            parent_id = self.default_node_id
        if debug_link is None:
            debug_link = {}

        add_group_res = self._add_mock_group(name, parent_id)
        if not add_group_res['status']:
            return add_group_res
        group_id = add_group_res['message']['group_id']
        
        add_data_res = self._add_mock_data('debug-link', group_id)
        if not add_data_res['status']:
            return add_data_res
        data_id = add_data_res['message']['data_id']

        debug_link_info = deepcopy(self.DEBUG_LINK_TEMPLATE)
        debug_link_info['id'] = data_id
        debug_link_info['response']['data'] = json.dumps(debug_link, ensure_ascii=False)
        update_data_res = self._update_mock_data(data_id, debug_link_info)
        if not update_data_res['status']:
            return update_data_res
        time.sleep(2)
        
        group_info = self._get_mock_group_info(group_id)
        if not group_info['status']:
            return group_info
        scene_id = group_info['message']['scene_id']
        group_name = group_info['message']['name']

        return {'status': True, 'message': {'group_id': group_id, 'scene_id': scene_id, 'group_name': group_name}}
    
    def get_flow_list(self, flow_type='Simple', black_hosts=None, black_filters=None, show_detail=False):
        """
        获取 flow 列表
        
        参数:
            flow_type: str, 过滤类型, 默认 Simple 即主要业务接口
            black_hosts: set, 可选, 要过滤的主机名集合
            black_filters: list, 可选, 要过滤的 URL 正则表达式列表
            show_detail: bool, 是否显示请求详细信息, 默认不显示（开启增加耗时和负载）

        返回值:
            dict: 包含以下字段的字典
                status: bool, 操作是否成功
                message: dict, 包含以下字段:
                    flows: dict, 当前代理到的请求列表
        """
        if black_hosts is None:
            black_hosts = set()
        if black_filters is None:
            black_filters = []
        else:
            black_filters = '|'.join(black_filters)

        flow_api_res = self._get_flow_list(flow_type)
        if not flow_api_res['status']:
            return flow_api_res
        flow_list = flow_api_res['message']
        filtered_flow_map = {}
        for flow in flow_list:
            url = flow['request']['url']

            if flow['request']['host'] in black_hosts:
                continue
            if re.search(black_filters, url):
                continue

            if url not in filtered_flow_map:
                filtered_flow_map[url] = []
            flow_data = {
                'id': flow['id'],
                'method': flow['request']['method'],
                'code': flow['response']['code'],
                'url': url
            }

            if show_detail:
                detail = self.get_flow_detail(flow['id'])['message']
                flow_data['request'] = detail['request']
                flow_data['response'] = detail['response']

            filtered_flow_map[url].append(flow_data) 

        return {'status': True, 'message': {'flows': filtered_flow_map}}
    
    def get_flow_detail(self, flow_id):
        """
        获取流量详情
        
        参数:
            flow_id: str, 请求 ID
            
        返回值:
            dict: 包含以下字段的字典
                status: bool, 操作是否成功
                message: dict, 包含以下字段:
                    id: str, 请求 ID
                    request: dict, 请求信息
                    response: dict, 响应信息
        """
        if not flow_id:
            return {'status': False, 'message': 'flow_id is required'}

        flow_detail_res = self._get_flow_detail(flow_id)
        if not flow_detail_res['status']:
            return flow_detail_res
        
        flow = {}
        flow['id'] = flow_detail_res['message']['id']
        flow['request'] = flow_detail_res['message']['request']
        flow['response'] = flow_detail_res['message']['response']

        return {'status': True, 'message': flow}
    
    def get_group_children(self, group_id):
        """
        获取数据组下子节点信息
        
        参数:
            group_id: str, 请求 ID
            
        返回值:
            dict: 包含以下字段的字典
                status: bool, 操作是否成功
                message: dict, 包含以下字段:
                    data_list: list, mock 数据列表
                    group_list: list, 子数据组列表
        """
        if not group_id:
            return {'status': False, 'message': 'group_id is required'}
        
        group_info_res = self._get_mock_group_info(group_id)
        if not group_info_res['status']:
            return group_info_res
        
        children = group_info_res['message']['children']
        data_list = []
        group_list = []
        for child in children:
            if child['type'] == 'data':
                data_list.append({'id': child['id'], 'name': child['name']})
            elif child['type'] == 'group':
                group_list.append({'id': child['id'], 'name': child['name']})
        
        return {'status': True, 'message': {'data_list': data_list, 'group_list': group_list}}
    
    def get_group_detail(self, group_id):
        """
        获取数据组的详细信息
        
        参数:
            group_id: str, 请求 ID
            
        返回值:
            dict: 包含以下字段的字典
                status: bool, 操作是否成功
                message: dict, 包含以下字段:
                    group_info: dict, 数据组信息
        """
        if not group_id:
            return {'status': False, 'message': 'group_id is required'}
        
        group_info_res = self._get_mock_group_info(group_id)
        if not group_info_res['status']:
            return group_info_res
        
        group_info = group_info_res['message']

        return {'status': True, 'message': {'group_info': group_info}}
    
    def get_mock_data_detail(self, data_id):
        """
        获取 mock 数据详情
        
        参数:
            data_id: str, 请求 ID
            
        返回值:
            dict: 包含以下字段的字典
                status: bool, 操作是否成功
                message: dict, mock 数据详情
        """
        if not data_id:
            return {'status': False, 'message': 'data_id is required'}
        
        data_info_res = self._get_mock_data_info(data_id)
        if not data_info_res['status']:
            return data_info_res
        
        data_info = data_info_res['message']

        return {'status': True, 'message': data_info}
    
    def save_mock_data_by_ids(self, group_id, flow_ids):
        """
        将指定 id 的请求保存成 mock 数据
        
        参数:
            group_id: str, 数据组 ID
            flow_ids: list, 请求 ID 列表
            
        返回值:
            dict: 包含以下字段的字典
                status: bool, 操作是否成功
                message: str, 成功或失败信息
        """
        if not group_id:
            return {'status': False, 'message': 'group_id is required'}
        if not flow_ids:
            return {'status': False, 'message': 'flow_ids is required'}
        
        activate_group_res = self._activate_group(group_id)
        if not activate_group_res['status']:
            return activate_group_res
        
        save_flow_res = self._save_by_flow_ids(group_id, flow_ids)
        if not save_flow_res['status']:
            return save_flow_res
        
        deactivate_group_res = self._deactivate_group()
        if not deactivate_group_res['status']:
            return deactivate_group_res

        return {'status': True, 'message': 'success'}
    
    def delete_mock_group(self, target_id, security_limit=True):
        """
        删除指定的 mock 数据组/mock 数据
        注意: 此处 mock 数据 id 和数据组 id 均可
        
        参数:
            target_id: str, 要删除的 mock 组 ID/mock 数据 ID
            security_limit: bool, 是否限制删除非叶子节点, 默认限制
            
        返回值:
            dict: 包含以下字段的字典
                status: bool, 操作是否成功
                message: str, 成功或失败信息
        """
        if not target_id:
            return {'status': False, 'message': 'target_id is required'}

        undeletable_ids = self.config['mock.data.tree.undeletableId']
        if target_id in undeletable_ids:
            return {'status': False, 'message': f'{target_id} is not deletable'}
        
        if security_limit:
            children_res = self.get_group_children(target_id)
            if not children_res['status']:
                return children_res
            if children_res['message']['group_list']:
                return {'status': False, 'message': f'{target_id} is not leaf node, please make sure it is secure'}

        delete_res = self._delete_mock_group(target_id)
        if not delete_res['status']:
            return delete_res
        
        return {'status': True, 'message': 'success'}
    
    def cut_mock_group(self, source_id, target_id):
        """
        剪切并粘贴 mock 数据组
        
        参数:
            source_id: str, 待移动的数据组
            target_id: str, 要粘贴到该数据组下
            
        返回值:
            dict: 包含以下字段的字典
                status: bool, 操作是否成功
                message: str, 成功或失败信息
        """
        if not source_id:
            return {'status': False, 'message': 'source_id is required'}
        if not target_id:
            return {'status': False, 'message': 'target_id is required'}
        
        cut_group_res = self._cut_mock_group(source_id)
        if not cut_group_res['status']:
            return cut_group_res
        
        time.sleep(2)
        
        paste_group_res = self._paste_mock_group(target_id)
        if not paste_group_res['status']:
            return paste_group_res
        
        return {'status': True, 'message': 'success'}
    
    def update_mock_data(self, data_id, data):
        """
        更新 mock 数据
        
        参数:
            data_id: str, 数据 ID
            data: dict, 更新数据
            
        返回值:
            dict: 包含以下字段的字典
                status: bool, 操作是否成功
                message: str, 成功或失败信息
        """
        REQUIRED_KEYS = {'id', 'name', 'type', 'rule', 'response', 'request'}
        if not data_id:
            return {'status': False, 'message': 'data_id is required'}
        if not data:
            return {'status': False, 'message': 'data is required'}
        if not REQUIRED_KEYS.issubset(data.keys()):
            return {'status': False, 'message': f'missing required keys: {REQUIRED_KEYS - set(data.keys())}'}
        if data['type'] != 'data':
            return {'status': False, 'message': 'data type must be data'}

        update_res = self._update_mock_data(data_id, data)
        if not update_res['status']:
            return update_res

        return {'status': True, 'message': 'success'}
    
    def extract_debug_link_id(self, group_detail_data):
        """
        从 get_group_detail 返回的数据中提取 name 为 debug-link 的 id 值，用于下一步修改 scheme
        
        参数:
            group_detail_data: dict, get_group_detail 方法的返回值
            
        返回值:
            str: debug-link 的 id 值，如果未找到则返回 None
        """
        try:
            # 获取 children 列表
            children = group_detail_data['message']['group_info']['children']
            
            # 遍历 children 查找 name 为 debug-link 的项
            for child in children:
                if child['name'] == 'debug-link':
                    return child['id']
                    
            return None
        except (KeyError, TypeError):
            return None
    
    def analyze_flow_list(self, flow_list_result):
        """
        分析 flow_list 的结果，统计数据总数，打印所有 URL 及其对应的 ID，并找出重复的 URL
        
        参数:
            flow_list_result: dict, get_flow_list 的返回结果
            
        返回值:
            dict: 包含以下字段的字典
                total_count: int, 总数据条数
                unique_urls: list, 所有唯一的 URL
                duplicate_urls: dict, 重复的 URL 及其出现次数
                url_info: dict, URL 详细信息
        """
        if not flow_list_result['status']:
            print(f"获取数据失败: {flow_list_result['message']}")
            return None
            
        flows = flow_list_result['message']['flows']
        
        # 统计总数据条数
        total_count = sum(len(flow_list) for flow_list in flows.values())
        print(f"\n总数据条数: {total_count}")
        
        # 统计 URL 出现次数和收集 ID
        url_info = {}  # {base_url: {'count': count, 'ids': [id1, id2, ...]}}
        for url, flow_list in flows.items():
            # 提取问号前的部分
            base_url = url.split('?')[0]
            if base_url not in url_info:
                url_info[base_url] = {'count': 0, 'ids': []}
            url_info[base_url]['count'] += len(flow_list)
            url_info[base_url]['ids'].extend([flow['id'] for flow in flow_list])
        
        # 打印所有 URL 及其对应的 ID
        print("\n所有 URL 及其对应的 ID:")
        for url in sorted(url_info.keys()):
            print(f"\nURL: {url}")
            print(f"出现次数: {url_info[url]['count']}")
            print("ID列表:")
            for id in url_info[url]['ids']:
                print(f"- {id}")
        
        # 找出重复的 URL（出现次数大于 1 的）
        duplicate_urls = {url: info['count'] for url, info in url_info.items() if info['count'] > 1}
        if duplicate_urls:
            print("\n重复的 URL:")
            for url, count in duplicate_urls.items():
                print(f"- {url} (出现 {count} 次)")
        else:
            print("\n没有重复的 URL")
        
        return {
            'total_count': total_count,
            'unique_urls': list(url_info.keys()),
            'duplicate_urls': duplicate_urls,
            'url_info': url_info
        }
    
    def collect_flow_ids(self, flow_list_result):
        """
        收集所有 flow 的 ID
        
        参数:
            flow_list_result: dict, get_flow_list 的返回结果
            
        返回值:
            list: 包含所有 flow ID 的列表
        """
        if not flow_list_result['status']:
            print(f"获取数据失败: {flow_list_result['message']}")
            return []
            
        flows = flow_list_result['message']['flows']
        
        # 收集所有 ID
        all_ids = []
        for flow_list in flows.values():
            for flow in flow_list:
                all_ids.append(flow['id'])
        
        print(f"\n总共收集到 {len(all_ids)} 个 ID:")
        print(all_ids)
        
        return all_ids
    
    @staticmethod
    def start_background_service(direction='playground', mock_port=None, proxy_port=None, extra_mock_port=None, websocket_port=None):
        try:
            print(f"正在启动后台服务 {direction}...")
            # 构建命令参数列表
            cmd = ['venv/bin/lb', 'start', direction, '-y']
            # 添加可选的端口参数
            if mock_port:
                cmd.extend(['--mock', str(mock_port)])
            if proxy_port:
                cmd.extend(['--proxy', str(proxy_port)])
            if extra_mock_port:
                cmd.extend(['--extra-mock', str(extra_mock_port)])
            if websocket_port:
                cmd.extend(['--websocket', str(websocket_port)])          
            
            process = subprocess.Popen(cmd,
                          stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE,
                          universal_newlines=True)
            # process = subprocess.Popen(cmd,
            #                stdout=None,
            #                stderr=None,
            #                universal_newlines=True)
            # 注册退出处理函数，确保主进程退出时终止子进程
            import atexit
            atexit.register(lambda p: p.terminate() if p.poll() is None else None, process)
            print("后台服务启动成功，保持连接中...")
            return process;
            
        except Exception as e:
            print(f"启动后台服务失败: {e}")
            return None

    @staticmethod
    def clear_lyrebird_orphan_process() -> bool:
        # 清理Lyrebird的孤儿进程
        # try:
        #     import psutil
        # except ImportError:
        #     logger.error("无法进行Lyrebird孤儿进程清理")
        #     return False

        # print("开始进行Lyrebird孤儿进程清理：所有父进程id为1且命令行中包含关键字lyrebird的进程将会被清理")
        # lyrebird_process_count = 0
        # for pid in psutil.pids():
        try:
            process = subprocess.Popen(['lb', 'kill'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except Exception as e:
            print(f"清理lb进程失败: {e}")
        return True


if __name__ == '__main__':
    # service_thread = threading.Thread(
    #         target=LyrebirdClient.start_background_service,
    #         args=('dzu',)
    #     )
    # service_thread.daemon = True  # 设置为守护线程，这样主进程结束时会自动终止
    # service_thread.start()
    # while(True):
    #     time.sleep(1)
    process = LyrebirdClient.start_background_service()
    max_retries = 30  # 最多等待30次
    retry_interval = 2  # 每次等待2秒
    lyrebird_url = 'http://127.0.0.1:9090'
    print('正在启动lyrebird，需要大约20s启动')
    for i in range(max_retries):
        try:
            # 尝试连接 Lyrebird 服务的配置 API
            response = requests.get(f"{lyrebird_url}/api/conf", timeout=3)
            if response.status_code == 200:
                print(f"Lyrebird 服务已启动，用时 {i * retry_interval} 秒")
                break
        except requests.exceptions.RequestException:
            pass
            
        print(f"等待 Lyrebird 服务启动，已尝试 {i+1}/{max_retries} 次")
        time.sleep(retry_interval)
    else:
        # for 循环正常结束（没有 break）表示达到最大重试次数
        raise Exception("Lyrebird 服务启动超时")
    if process:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
        print("服务已手动终止")

    # 初始化客户端
    # client = LyrebirdClient('http://127.0.0.1:9090', 'cd003fc7-3d69-4853-8cbb-5a30a088332d')
    
    # 设置 scheme
    # scheme = 'imeituan://www.meituan.com/gc/poi/detail?id=1031353116&shopId=10313531'
    # debug_link_template = deepcopy(client.DEBUG_LINK_RESPONSE_DATA_TEMPLATE)
    # debug_link_template[2]['info']['value'] = scheme

    # # 创建 mock 数据组
    # group = client.create_group(
    #     name='正式test33', 
    #     parent_id='cd003fc7-3d69-4853-8cbb-5a30a088332d', 
    #     debug_link=debug_link_template
    # )
    # print('创建的mock数据组:', group)

    # # 获取 flow 列表
    # black_hosts = {
    #     'mtmessage.meituan.com', 'mop.meituan.com', 'awp-assets.sankuai.com', 
    #     'appsec-mobile.meituan.com', 'aop.meituan.com', 's3plus.sankuai.com', 
    #     'ar2.test.meituan.com', 'apimeishi.meituan.com', 'dynamicf.sankuai.com', 
    #     'apimobile.meituan.com', 'dd.meituan.com', 'gaea.meituan.com', 
    #     'pubmsg.meituan.com', 'mars.meituan.com', 'ddapi.fe.test.sankuai.com'
    # }
    # flow_list = client.get_flow_list(
    #     black_hosts=black_hosts, 
    #     black_filters=['/mapi/dzu/live/querylivepartdetailbyliveid.bin']
    # )

    # # 分析结果
    # client.analyze_flow_list(flow_list)
    
    # # 收集所有接口的 mock ID
    # all_ids = client.collect_flow_ids(flow_list)
    
    # # 保存 mock 数据
    # save_result = client.save_mock_data_by_ids(group['message']['group_id'], all_ids)
    # print('mock数据保存结果：', save_result)