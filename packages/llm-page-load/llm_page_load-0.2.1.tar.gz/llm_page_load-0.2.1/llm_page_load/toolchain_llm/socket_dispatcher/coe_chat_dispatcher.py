from typing import Any, Dict
from socket_dispatcher.base_socket_dispatcher import BaseSocketDispatcher
from utils import logger
import json
import urllib.parse
from service.coe_analysis.runners.chat_6to2notto import ChatRunner_6to2not
from service.coe_analysis.runners.base import COEChatBaseRunner, ChatRunners
from service.coe_analysis.search_coe_result_item import search_coe_result_item


def get_chat_runner(type: str, result_item, _id: str) -> COEChatBaseRunner:
    if type in ChatRunner_6to2not.valid_type_list:
        runner = ChatRunner_6to2not(result_item=result_item, _id=_id, type=type)
        ChatRunners[result_item.id] = runner
        return runner


def chat_with_coe(data: Dict[str, Any], header: Dict[str, Any]):
    query = data['query']
    type = data['type']
    coe_id = data['coe_id']
    task_id = data['task_id']
    result_item, _id = search_coe_result_item(coe_id, type, task_id)
    if result_item.id in ChatRunners:
        runner = ChatRunners[result_item.id]
        runner.load_retiver(coe_id)
    else:
        runner = get_chat_runner(result_item=result_item, _id=_id, type=type)
        runner.load_retiver(coe_id)
    runner.chat(query)
    del ChatRunners[result_item.id]


def ack_token(data: Dict[str, Any], header: Dict[str, Any]):
    chain_id = data['chain_id']
    ChatRunners[chain_id].chat_callback.ack = True


class CoeChatDispatcher(BaseSocketDispatcher):
    def on_message(self, message):
        '''
        处理websocket的主要函数
        message={"path":xxx,"data":xxx}
        '''
        super().on_message(message)
        # logger.info('coe on message = ' +
        #             json.dumps(message, ensure_ascii=True))
        path = message['path']
        data = message['data']
        header = message['header']
        if 'userInfo' in header:
            info = urllib.parse.unquote(header['userInfo'])
            user_info = json.loads(info)
            # logger.info(f'[登陆信息] {user_info}')
            ssoid = user_info['ssoId']
            if ssoid is None or len(ssoid) == 0:
                logger.info('[无效登陆信息]')
            else:
                header['userInfo'] = user_info
        method_dict = {
            'chat/ask': chat_with_coe,
            'chat/ack': ack_token,
        }
        method_dict[path](data, header)
