import json
import os
from queue import Queue
import uuid
import requests
from flask_socketio import SocketIO
from service.aui_test_agent.hyperjump_copilot.es_storaget import (ChatMessage, MetaAgentAction,
                                                                  SocketEvent, SocketStorage)
from service.aui_test_agent.hyperjump_copilot.chat_prompt import UI_CASE_PROMPT, UI_CASE_TOOLS
from service.aui_test_agent.hyperjump_copilot.friday_bot import FridayBot
from service.aui_test_agent.hyperjump_copilot.remote_driver import RemoteDriver
from service.aui_test_agent.hyperjump_copilot.robot_context import UITestRobotContextManager
from utils import logger
from llmcore_sdk.models.friday import Friday
from AUITestAgent.utils.utils import BLUE, END, find_json  # noqa
from service.aui_test_agent.hyperjump_copilot.print_inc import PrintInterceptorV2
from functools import partial
import threading
import threading
import time
from copy import deepcopy
from service.aui_test_agent.hyperjump_copilot.utils.mmcd_api import *
from service.aui_test_agent.hyperjump_copilot.utils.ui_case_api import LyrebirdClient
from concurrent.futures import ThreadPoolExecutor
from service.aui_test_agent.hyperjump_copilot.agent.base_agent import BaseAgent
from service.aui_test_agent.hyperjump_copilot.chat_prompt import *
from service.aui_test_agent.hyperjump_copilot.agent import *


# 定义线程局部变量
thread_local = threading.local()


# 用户会话管理
ui_user_sessions = {}
# 添加全局映射表存储CaseGenerateResponseManager实例
response_manager_map = {}

CHAT_NAMESPACE = '/hyperjump/copilot/case_generate'
DRIVER_NAMESPACE = '/hyperjump/copilot/driver'
DIRECTIONS = ['Device2Server', 'Server2Device', 'Frontend2Server', 'Server2Frontend']
DIRECTION_MAPPING = {
    'dzu': {
        'nodeid': 'cd003fc7-3d69-4853-8cbb-5a30a088332d',
        'pageid': 5522,
        'lyrebird_url': 'http://127.0.0.1:9090'
    },
    'dzviewscene': {
        'nodeid': '2d38140b-2546-4283-a518-f5fbae11938d',
        'pageid': 5542,
        'lyrebird_url': 'http://127.0.0.1:9091'
    },
    'dzuactivity': {
        'nodeid': '656552d6-fe31-480f-9a17-301a755c1c84',
        'pageid': 5541,
        'lyrebird_url': 'http://127.0.0.1:9092'
    },
    'dzupoimodule': {
        'nodeid': '32151276-906e-4d83-8da3-c30add88ddfe',
        'pageid': 5524,
        'lyrebird_url': 'http://127.0.0.1:9093'
    },
    'dzutrade': {
        'nodeid': '2a2baabf-51d8-4bcc-9167-318a22d57a8b',
        'pageid': 5543,
        'lyrebird_url': 'http://127.0.0.1:9094'
    },
    'playground': {
        'nodeid': 'd71cde5b-9001-49fe-a2a5-91a133237f60',
        'pageid': 5548,
        'lyrebird_url': 'http://127.0.0.1:9095'
    }
}
notification_executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="notification_worker")
shared_data = {
    'lyrebird_group_id': None
}

def get_available_compatibility_phones():
    """
    封装 curl 请求为 Python 函数，用于获取 Copilot 兼容性手机信息。
    """
    url = 'https://client.hotel.test.sankuai.com/compatibilityPhone/available'
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-CN,zh;q=0.9,ja;q=0.8,en;q=0.7',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Origin': 'https://qa.sankuai.com',
        'Pragma': 'no-cache',
        'Referer': 'https://qa.sankuai.com/',
        'SSOID': 'eAGFkjtv01AAheVOpRPiF2RggEhFvi_fe5nwTZ2H87LrJnayWH5c22mCQ-o0bq0uCKTuHTuh_ggWNiSEhARiQh3K0oE_wIxEOzCzH33n09HZVh5effmwVbt9--bPNYQ7hKJQBrGM8fMaxSqONRlwVYswUEkQQFhPYggJjlQJgfimPHrqytCJZC7PCDCozjkQUKdEQ5QZdznCmxowwB7RYO37r8uPN_CJAv8LZvdKLx60v_54__oaWr_Pzz9_AhfK9r-uS-UZjUCoyYQmCeCSBDEIIdUiQmmAoExw4gOqQsgZRCpE-Ep5XMrwTA04SmgYoxAyjAjlWsJlEsRazKgWo3hakxyThCAZaHWGA4k4iMKIRSoOOQsTGFU_t6RugMoBw1Q1bH2gF3bouAaw02WnV1RDOqS9GcTOoGOkjkP7u_2jLnxlx2NvvJnYLVGaHacllnraqGwX6yIdMstsZbhAMdrXlr6raeOe17ADOWN6g5ByGQlcnji2J_RhZLKeuesnx8xeW20D4911Zs5QtjK8ciW85qqdcJ3hlc1PmSWodULkpu3Hau5tQDEouFW03UMfbvLqKBPmwQjqvDkaLvbnwfIlEU2nF6ebwnDGh0wc3mHhZt0lfO6KSGqzyURNi2nXdIcbrw8MyxduMbIber1-N0iznBiiNHRD9BpjJqrWMs78rBHkpzlw9rKSWXNt6vWNdd4_kLwD6WIyWo7weMVn3XKULDrUjkr_ZG9-odRK15o6g_ViX3VNNvUG_RFomaDp8HmjGqBVfqnsVFmQp6fHEKF3yu3N_Uf-Ak4G4qo**eAEFwYEBwCAIA7CXmFAt50jB_09Ysg-W-W4a0Hj8gtIaB10sIzyzLWusPO464p3tQwWypPgBEPwRBg**E8kGwCBPb1pw7y4bZNN_DBZUWA7L-SVQt298tKuw3h12W_utv-HnlHPWLldoytK3FCpDsooIIbBVyLyy8xqLzQ**NTE3MDQ2Nix6aGFuZ3l1MjMzLOW8oOmbqCx6aGFuZ3l1MjMzQG1laXR1YW4uY29tLDEsMDMxOTU3ODEsMTc0MTg3MTQzMjI5MA',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-site',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'isOnline': 'true',
        'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
    }
    params = {
        'business': 'clienttool',
        'jobType': 'Copilot',
        'platform': 'Android',
        'sourceType': 'Microscope',
        'category': '美团',
        'filterRule': 'ALL',
        'usePublic': 'true',
    }

    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        response.raise_for_status()


def trigger_compatibility_job(socket_id):
    """
    封装 curl 请求为 Python 函数，用于触发 Copilot 测试任务。
    """
    url = 'https://compatibility.hotel.test.sankuai.com/trigJob'
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-CN,zh;q=0.9,ja;q=0.8,en;q=0.7',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Content-Type': 'application/json;charset=UTF-8',
        'Origin': 'https://qa.sankuai.com',
        'Pragma': 'no-cache',
        'Referer': 'https://qa.sankuai.com/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'SSOID': 'eAGFkjtv01AAheVOpRPiF2RggEhFvi_fe5nwTZ2H87LrJnayWH5c22mCQ-o0bq0uCKTuHTuh_ggWNiSEhARiQh3K0oE_wIxEOzCzH33n09HZVh5effmwVbt9--bPNYQ7hKJQBrGM8fMaxSqONRlwVYswUEkQQFhPYggJjlQJgfimPHrqytCJZC7PCDCozjkQUKdEQ5QZdznCmxowwB7RYO37r8uPN_CJAv8LZvdKLx60v_54__oaWr_Pzz9_AhfK9r-uS-UZjUCoyYQmCeCSBDEIIdUiQmmAoExw4gOqQsgZRCpE-Ep5XMrwTA04SmgYoxAyjAjlWsJlEsRazKgWo3hakxyThCAZaHWGA4k4iMKIRSoOOQsTGFU_t6RugMoBw1Q1bH2gF3bouAaw02WnV1RDOqS9GcTOoGOkjkP7u_2jLnxlx2NvvJnYLVGaHacllnraqGwX6yIdMstsZbhAMdrXlr6raeOe17ADOWN6g5ByGQlcnji2J_RhZLKeuesnx8xeW20D4911Zs5QtjK8ciW85qqdcJ3hlc1PmSWodULkpu3Hau5tQDEouFW03UMfbvLqKBPmwQjqvDkaLvbnwfIlEU2nF6ebwnDGh0wc3mHhZt0lfO6KSGqzyURNi2nXdIcbrw8MyxduMbIber1-N0iznBiiNHRD9BpjJqrWMs78rBHkpzlw9rKSWXNt6vWNdd4_kLwD6WIyWo7weMVn3XKULDrUjkr_ZG9-odRK15o6g_ViX3VNNvUG_RFomaDp8HmjGqBVfqnsVFmQp6fHEKF3yu3N_Uf-Ak4G4qo**eAEFwYEBwCAIA7CXmFAt50jB_09Ysg-W-W4a0Hj8gtIaB10sIzyzLWusPO464p3tQwWypPgBEPwRBg**E8kGwCBPb1pw7y4bZNN_DBZUWA7L-SVQt298tKuw3h12W_utv-HnlHPWLldoytK3FCpDsooIIbBVyLyy8xqLzQ**NTE3MDQ2Nix6aGFuZ3l1MjMzLOW8oOmbqCx6aGFuZ3l1MjMzQG1laXR1YW4uY29tLDEsMDMxOTU3ODEsMTc0MTg3MTQzMjI5MA',
        'Sec-Fetch-Site': 'same-site',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'isOnline': 'true',
        'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
    }
    payload = {
        "plat": "Android",
        "app_plat": "Android",
        "job_type": "Copilot",
        "job_name": "【MMCD】Copilot Demo",
        "user": "zhangyu233",
        "business": "clienttool",
        "category": "美团",
        "product_id": 2,
        "devices": "127.1.5.1:21",
        "app_url": "https://hyperloop-s3.sankuai.com/hpx-artifacts/3185142-973-1741353102936783/aimeituan-release_12.29.400-367253-aarch64.apk",
        "pages": [
            {
                "app": "meituan",
                "activity": "",
                "os": "Android,iOS",
                "business": "clienttool",
                "create_time": 1741659453000,
                "mini_version": "",
                "mock_id": "-",
                "scene_id": 46611,
                "remark": "",
                "source": "config_center",
                "priority": "p2",
                "params": "",
                "url": "",
                "example": "",
                "update_time": 1741659453000,
                "name": "Copilot测试",
                "online": True,
                "id": 1037553,
                "actions": "{\"text_keys\":[]}",
                "scroll_count": 0
            }
        ],
        "mock_data": "1",
        "mock_flag": 1,
        "ab_key": f"$socket_id:{socket_id}",
        "env_lock_mrn_bundle": "NA",
        "source_url": "http://qa.sankuai.com/client",
        "source_type": "Microscope",
        "use_test_device": "0",
        "app_params": "{\"runEngine\":\"Mobile\",\"pageImpl\":\"All\",\"visionComponents\":\"InputSupportChinese,CopilotDevice\",\"detectShadow\":false,\"appLogin\":\"\",\"mmp\":\"\",\"clientSwimlane\":\"\",\"serverSwimlane\":\"\",\"ssoLoginUser\":\"\",\"debug_link\":true,\"privacyMode\":false,\"use_testID\":false,\"env_mrnEvaTest\":0,\"robustMode\":\"CHANGE_CUSTOM\",\"robustCustomConfig\":{},\"checkers\":\"\",\"configJson\":[{\"type\":\"signin\",\"info\":{\"htmOffline\":0,\"account\":\"\",\"password\":\"\",\"countryCode\":\"86\"}},{\"type\":\"mmp_package\",\"info\":{\"mmpEnv\":\"prod\",\"mmpVersionId\":\"\",\"mmp_urlScheme\":\"\"}},{\"type\":\"scheme\",\"info\":{\"value\":\"${URL_SCHEME}\"}}],\"product_info\":\"{\\\"appName\\\":\\\"\\\",\\\"authority\\\":\\\"www.meituan.com/\\\",\\\"evaKey\\\":\\\"group\\\",\\\"id\\\":2,\\\"implList\\\":[\\\"Native\\\",\\\"MRN\\\",\\\"Picasso\\\",\\\"H5\\\",\\\"MP\\\"],\\\"isDebugLink\\\":true,\\\"isLyrebird\\\":true,\\\"label\\\":\\\"美团-Android\\\",\\\"name\\\":\\\"meituan\\\",\\\"os\\\":\\\"Android\\\",\\\"perfName\\\":\\\"android_platform_monitor\\\",\\\"scheme\\\":\\\"imeituan\\\",\\\"sigmaId\\\":1,\\\"type\\\":\\\"app\\\"}\",\"taskSchemes\":{\"schemes\":[\"imeituan://www.meituan.com(举例)\",\"\"]},\"action_filter\":{},\"service_env\":[]}"
    }

    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        return response.json()
    else:
        response.raise_for_status()


class CaseGenerateResponseManager:
    def __init__(self, chat_storage: SocketStorage, device_storage: SocketStorage,
                 socket: SocketIO, task_queue: Queue):
        self.chat_storage = chat_storage
        self.device_storage = device_storage
        self.model = 'gpt-4o-2024-08-06'
        self.socket = socket
        self.task_queue = task_queue
        self.test_work_dir = os.path.join('./log', 'aui_test_agent-' + str(uuid.uuid1()))
        self.driver = RemoteDriver(self.task_queue, self.socket, self.chat_storage, self.device_storage)
        self.CaseNameAgent=BaseAgent(operator="machongjian",sub_agent_id='agent-45e36dda-0')
        # 初始化ChatBotFridayAgent并传递chat_storage
        self.ChatBotAgent=ChatBotFridayAgent(model_name=self.model, operator="default_user",prompt=CHAT_BOT_PROMPT,tools=CHAT_TOOLS)
        # 注册专业Agent
        self._register_specialized_agents()
        # 将chat_storage中的历史消息同步到ChatBotAgent
        self._sync_chat_history_to_agent()

    def _register_specialized_agents(self):
        """
        注册专业领域Agent
        """
        # 创建UI测试用例专用Agent
        ui_case_agent = UICaseFridayAgent(model_name=self.model, operator="ui_case_agent",prompt=UI_CASE_PROMPT,tools=UI_CASE_TOOLS)
        # 注册到ChatBotFridayAgent
        self.ChatBotAgent.register_agent("ui_case", ui_case_agent)


        # 创建自然语言录入专用Agent
        natural_language_agent = NaturalLanguageFridayAgent(model_name=self.model, operator="natural_language_agent")
        # 注册到ChatBotFridayAgent
        self.ChatBotAgent.register_agent("natural_language", natural_language_agent)

    def send_chat_message(self, message, type='chat'):
        self.chat_storage.chat_history.append(ChatMessage(role='assistant', content=message))
        #过滤空值
        if self.ChatBotAgent.current_agent and message != None:
            self.ChatBotAgent.current_agent.chat_storage["chat_history"].append(ChatMessage(role='assistant', content=message))
        new_event = SocketEvent(event_name=type, event_data=message, direction=DIRECTIONS[3])
        self.chat_storage.events.append(new_event)
        self.socket.emit('complete', new_event.as_dict(), namespace=CHAT_NAMESPACE, to=self.chat_storage.sid)

    def send_log(self, message, type='chat'):
        new_event = SocketEvent(event_name=type, event_data=message, direction=DIRECTIONS[3])
        self.chat_storage.events.append(new_event)
        self.socket.emit('complete', new_event.as_dict(), namespace=CHAT_NAMESPACE, to=self.chat_storage.sid)

    def chat_once(self, data, role='user'):
        """
        处理用户消息，使用ChatBotFridayAgent的process_request方法
        Args:
            data: 用户消息
            role: 消息角色，默认为'user'

        Returns:
            模型生成的回复内容和完整响应
        """
        # 将用户消息添加到chat_storage
        self.chat_storage.chat_history.append(ChatMessage(role=role, content=data))
        # 同步最新消息到ChatBotAgent
        self._sync_chat_history_to_agent()

        # 使用ChatBotFridayAgent的process_request方法处理用户请求
        prompt = PROMPT
        tools = TOOLS

        # 调用process_request处理请求
        ans, resp = self.ChatBotAgent.process_request(data, prompt=prompt, tools=tools)

        # 将助手回复添加到chat_storage（如果不是系统消息）
        if role != 'system':
            # 注意：这里不需要再添加到chat_storage，因为send_chat_message会添加
            pass

        return ans, resp

    def complete_with_knowledge(self, query):
        bot = FridayBot()
        bot.get_friday_token()
        bot.bot_send_message(query)
        ans = bot.chat_bot_messages[-1]['text']
        self.send_chat_message(ans)
        return None

    def apply_for_device(self):
        self.send_chat_message('正在申请设备...大概需要5分钟，请耐心等待，期间不要刷新页面。')
        # requests.get(f'http://localhost:8002/hypejump/copilot/attach_device?peer_sid={self.chat_storage.sid}&host=localhost&port=8002')
        ret = get_available_compatibility_phones()
        assert 'ARM-Android14' in [i['model'] for i in ret['data']['devices']], '执行机申请失败'
        '''TODO 需要获取当前ip，保证设备与前端都是对同一个后端机器发起连接'''
        trigger_compatibility_job(self.chat_storage.sid)
        return None

    def reclaim_current_device(self):
        self.send_chat_message('正在回收设备...')
        self.socket.emit('action', 'stop', namespace=DRIVER_NAMESPACE, to=self.device_storage.sid)
        return "设备回收成功"

    def to_init_page(self):
        self.send_chat_message('正在回到美团首页...')
        self.driver.to_init_page()

    def save_action_to_storage(self, plan, action, oracle, result=None, url_scheme=None):
        self.chat_storage.state_memory.actions.append(MetaAgentAction(
            plan=plan, action=action, oracle=oracle, result=result, url_scheme=url_scheme
        ))
        
    def save_ui_case(self):
        bu=self.chat_storage.state_memory.params['direction']
        mapping = DIRECTION_MAPPING.get(bu, DIRECTION_MAPPING['playground'])
        parentid = mapping['pageid']
        scheme=self.chat_storage.state_memory.params['scheme']
        choices=self.CaseNameAgent.send_message(scheme)
        case_name=choices[0]['message']['content']
        #调用agent获取页面链接名称
        sceneid=self.chat_storage.state_memory.sceneid

        print('sceneid：'+str(sceneid))
        #迁移mmcd
        remove_mmcd(sceneid,case_name,parentid,4,parentid)
        self.send_chat_message(f"用例保存成功！https://qa.sankuai.com/client/scene/{sceneid}/base")
        #迁移lyrebird
        #更新基准图
        jobid=self.chat_storage.state_memory.params['jobid']
        pics=get_job_report(jobid)
        if pics:
            update_pics(pics,bu,'machongjian','12.33.40')

    def delete_ui_case(self):
        sceneid=self.chat_storage.state_memory.sceneid
        if sceneid is None:
            print('没有可删除的用例，请确认用例状态')
            return
        else:
            delete_mmcd_scene(sceneid)
            self.send_chat_message('临时用例清除完成，请刷新页面后重新输入待创建的用例信息')
            print('用例删除成功，sceneid为：' + str(sceneid))


    def ui_case_autogenerate(self,scheme,direction=None):
        if direction is None:
            direction='playground'
        self.chat_storage.state_memory.params['direction']=direction
        self.chat_storage.state_memory.params['scheme']=scheme
        # 检查 direction 是否在 DIRECTION_MAPPING 中
        if direction not in DIRECTION_MAPPING:
            self.send_chat_message('暂不支持' + direction + '方向，请刷新页面选择其他方向')
            raise Exception("用户输入方向不支持")
    
        mapping = DIRECTION_MAPPING.get(direction, DIRECTION_MAPPING['playground'])
        nodeid = mapping['nodeid']
        pageId = mapping['pageid']
        #1.启动lyrebird,默认playground方向
        # future=notification_executor.submit(LyrebirdClient.start_background_service,direction)
        # 使用轮询方式检查 Lyrebird 服务是否可用
        max_retries = 30  # 最多等待30次
        retry_interval = 2  # 每次等待2秒
        lyrebird_url = mapping['lyrebird_url']
        # self.send_chat_message('正在检查lyrebird的启动状态,方向'+direction)
        for i in range(max_retries):
            try:
                # 尝试连接 Lyrebird 服务的配置 API
                response = requests.get(f"{lyrebird_url}/api/status", timeout=3)
                print(f"检查 Lyrebird 服务状态，code为: {response.status_code}")
                if response.status_code == 200:
                    print(f"Lyrebird 服务已启动，用时 {i * retry_interval} 秒")
                    self.send_chat_message(direction + '方向lyrebird的状态正常，即将创建临时数据组')
                    break
            except requests.exceptions.RequestException:
                pass
            
            print(f"等待 Lyrebird 服务启动，已尝试 {i+1}/{max_retries} 次")
            time.sleep(retry_interval)
        else:
            # for 循环正常结束（没有 break）表示达到最大重试次数
            self.send_chat_message("Lyrebird状态异常，请检查服务状态")
            raise Exception("Lyrebird 服务启动超时")
        lb=LyrebirdClient(lyrebird_url, nodeid)
        #2.进行数据组创建，mmcd页面创建等操作，返回页面pageid
        category = self.get_appinfo_byurl(scheme)
        debug_link_template = deepcopy(lb.DEBUG_LINK_RESPONSE_DATA_TEMPLATE)
        debug_link_template[2]['info']['value'] = scheme
        case_name=generate_random_name()
        implement="MRN"
        priority=4
        business = direction
        productId=2 # 美团android为2
        app_url = "https://hyperloop-s3.sankuai.com/hpx-artifacts/3350762-973-1747810115548868/aimeituan-release_12.36.200-385991-aarch64.apk"
        if category == '点评':
            app_url = "https://apptest.sankuai.com/download/Dianping_11.41.4.190523.R.x64_190523-aarch64.apk"
            productId=10
        job_name = "【MMCD】视觉AI运行验证0430"
        user = "machongjian"
        group = lb.create_group(
            name=case_name, 
            parent_id=nodeid, 
            debug_link=debug_link_template
        )
        # 检查 创建lyrebird数据组的结果 是否为 true
        if group.get('status') == True:
            # 提取 group_id 和 scene_id
            group_id = group['message']['group_id']
            scene_id = group['message']['scene_id']
            self.send_chat_message(f"临时数据组创建成功：group_id={group_id}, scene_id={scene_id}")
        else:
            # 处理 status 不为 true 的情况
            self.send_chat_message("创建数据组失败：" + json.dumps(group))
            raise Exception("lyrebird 创建数据组失败")
        self.lyrebird_group_id = group['message']['group_id']
        shared_data['lyrebird_group_id'] = self.lyrebird_group_id
        sceneId=group['message']['scene_id']
        #更新状态机中sceneid的数值
        self.chat_storage.state_memory.sceneid=sceneId
        # MMCD保存用例
        result = add_scene(sceneId, case_name, pageId, priority)
        print("接口返回：", result)
        #MMCD设置用例产品信息
        result = set_scene_product(productId, sceneId, implement)
        print("接口返回：", result)
        self.send_chat_message(direction + "方向MMCD临时case创建成功")
        #3.调用插件，根据之前的pageid去触发job，进行mock数据录入，基准图获取和本次录制的接口数据，并回显给前端
        filtered_pages = get_page_object(business, productId, case_name)
        arm14_device = get_available_arm14_device(business, category)
        print("随选择的任意1台空闲的ARM14执行机：", arm14_device)
        result = trigger_hyperjump_job(app_url, business, category, job_name, user, arm14_device, filtered_pages, sceneId,self.chat_storage.sid, productId)
        print("触发任务结果：", result)
        #4.截图和job链接返回给用户，提示用户进行后置操作，如mock路由，debuglink的账号修改等
        self.send_chat_message("视觉测试job已成功触发，job链接为：https://qa.sankuai.com/microscope/jobInfo?jobId="+result['job_id'])
        self.send_chat_message("正在等待任务执行，3~5分钟后页面右侧将会出现页面投屏，请耐心等待并留意画面变化")
        self.chat_storage.state_memory.params['jobid']=result['job_id']
        # self.send_chat_message('视觉测试用例已经触发完成，请确认是否符合预期')
        return None    

    def get_appinfo_byurl(self,scheme):
        category='美团'
        if 'imeituan' not in scheme:
            category='点评'
        return category   


    def apply_action(self, type, message):
        '''注意，这个返回需要用BLUE的方式print'''
        chat_type = type if type in [
            'ACTION', 'PLAN_AND_ACTION', 'RUNALL'
        ] else 'chat'
        send_log_with_type = partial(self.send_log, type=chat_type)
        with PrintInterceptorV2(send_log_with_type):
            self.send_chat_message(f'Agent正在执行{type}...', type=chat_type)
            with UITestRobotContextManager(self.test_work_dir, 1, self.driver) as robot:
                try:
                    if type == 'ACTION':
                        robot.execute(message, '')
                        self.save_action_to_storage(type, message, None)
                    elif type == 'PLAN_AND_ACTION':
                        drive_task, test_task = robot.task_compose(message)
                        self.save_action_to_storage(type, drive_task, test_task)
                        robot.execute(drive_task, test_task)
                    elif type == 'RUNALL':
                        cases = find_json(self.chat_storage.state_memory.generated_cases)
                        self.send_chat_message(f'测试用例数量:{len(cases)}', type=chat_type)
                        for k, v in cases.items():
                            self.send_chat_message(f'当前被执行case:{v}', type=chat_type)
                            drive_task, test_task = robot.task_compose(str(v))
                            self.save_action_to_storage(type, drive_task, test_task)
                            robot.execute(drive_task, test_task)
                            self.driver.to_init_page()
                    elif type == 'TO_INIT':
                        self.to_init_page()
                except Exception as e:
                    logger.error('apply_action报错', e)
                    raise e
        return "执行成功"

    def auto_generate_case(self, type, message):
        self.send_chat_message('正在生成测试用例...', type='generate-case')
        send_log_with_type = partial(self.send_log, type='generate-case')
        with PrintInterceptorV2(send_log_with_type):
            with UITestRobotContextManager(self.test_work_dir, 1, self.driver) as robot:
                resp = robot.test_case_generate(mode='generate', prd=message)
            resp = json.dumps(json.loads(resp), ensure_ascii=False, indent=2)
            self.chat_storage.state_memory.generated_cases = resp
            self.send_log(resp, type='generate-case')  # 对话模型不感知 case
            self.chat_storage.update_to_es()
        return "生成case完成"

    def _sync_chat_history_to_agent(self):
        """
        将chat_storage中的历史消息同步到ChatBotAgent
        """
        # 直接将SocketStorage中的历史消息转换为ChatBotAgent需要的格式，并过滤掉content为空的消息
        self.ChatBotAgent.chat_storage["chat_history"] = [
            ChatMessage(role=msg.role, content=msg.content)
            for msg in self.chat_storage.chat_history
            if msg.content  # 过滤掉content为空的消息
        ]
def exception_handler(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Exception in {func.__name__}: {e}", exc_info=True)
            raise e
    return wrapper


def manage_event(
        chat_storage: SocketStorage, device_storage: SocketStorage,
        event: SocketEvent, socket: SocketIO, task_queue: Queue = None):
    try:
        return _manage_event_inner(chat_storage, device_storage, event, socket, task_queue)
    except Exception as e:
        # 使用sid作为key获取或创建CaseGenerateResponseManager实例
        sid = chat_storage.sid
        if sid not in response_manager_map:
            response_manager_map[sid] = CaseGenerateResponseManager(chat_storage, device_storage, socket, task_queue)

        chat_resp_manager = response_manager_map[sid]
        logger.error(f"Exception in manage_event: {e}", exc_info=True)
        chat_resp_manager.send_log('后端执行错误', type='chat')
        raise e


def _manage_event_inner(
        chat_storage: SocketStorage, device_storage: SocketStorage,
        event: SocketEvent, socket: SocketIO, task_queue: Queue = None):
    '''
    这个方法，在假设 chat_socket 和 device_ socket 都存在的情况下，打通整个交互通道
    '''
    assert not chat_storage.is_end, '对话 socket 已经关闭'

    # 使用sid作为key获取或创建CaseGenerateResponseManager实例
    sid = chat_storage.sid
    if sid not in response_manager_map:
        response_manager_map[sid] = CaseGenerateResponseManager(chat_storage, device_storage, socket, task_queue)

    chat_resp_manager = response_manager_map[sid]

    if event.event_name == 'pass' and event.direction == DIRECTIONS[0]:
        socket.emit('complete', event.event_data, namespace=CHAT_NAMESPACE, to=chat_storage.sid)
        chat_storage.events.append(event)
    elif event.direction == DIRECTIONS[2] and event.event_name == 'clear':
        chat_storage.chat_history = []
        if device_storage:
            chat_resp_manager.to_init_page()
        chat_resp_manager.send_chat_message('请向我提问，可以提问"帮我申请一个设备"或者"手机白屏怎么办"')
    elif '2Server' in event.direction and event.event_name == 'chat':
        # 检查是否有活跃的专业Agent，如果有则使用continue_conversation
        if chat_resp_manager.ChatBotAgent.current_agent:
            ans, resp = chat_resp_manager.ChatBotAgent.continue_conversation(event.event_data, prompt=PROMPT, tools=TOOLS)
        else:
            # 使用ChatBotFridayAgent处理用户请求
            ans, resp = chat_resp_manager.chat_once(event.event_data)

        # 检查是否有函数调用
        if 'function_call' in resp['data'] and len(resp['data']['function_call']) != 0:  # noqa
            func_name = resp['data']['function_call']['name']
            args = json.loads(resp['data']['function_call']['arguments'])
            if hasattr(chat_resp_manager, func_name):
                end_message = getattr(chat_resp_manager, func_name)(**args)
                if end_message:
                    # 如果函数调用返回了消息，则将其作为系统消息发送给ChatBotAgent继续处理
                    ans, resp = chat_resp_manager.chat_once(end_message, role='system')
                    chat_resp_manager.send_chat_message(ans)
                else:
                    pass  # 需要等待异步完成，所以不发送消息
        else:
            # 没有函数调用，直接发送回复
            chat_resp_manager.send_chat_message(ans)
    elif event.direction == DIRECTIONS[2] and event.event_name == 'update-case':
        chat_storage.state_memory.generated_cases = event.event_data
    elif event.event_name == 'peer':
        ans, resp = chat_resp_manager.chat_once('设备申请成功', role='system')
        chat_resp_manager.send_chat_message(ans)
    # 持久化 socket-storage
    if chat_storage:
        chat_storage.update_to_es()      
    if device_storage:
        device_storage.update_to_es()
