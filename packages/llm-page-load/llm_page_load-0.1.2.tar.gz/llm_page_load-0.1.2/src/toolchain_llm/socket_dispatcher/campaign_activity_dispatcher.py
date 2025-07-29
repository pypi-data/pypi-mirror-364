import time
from typing import Any, Dict
from service.campaign_activity_analysis.chat \
    import CALLBACKS, chat_once_and_generate_children, get_chat_prompt, chat_on_node_with_rules
from service.campaign_activity_analysis.task_server import create_task, update_task
from service.campaign_activity_analysis.tree_node_server import create_node, update_node
from socket_dispatcher.base_socket_dispatcher import BaseSocketDispatcher
from utils import logger
import json
from service.campaign_activity_analysis.config_reader \
    import on_emit
from service.campaign_activity_analysis.es_client import es_client, TaskIndex, TreeNodeIndex
import urllib.parse


def chat_on_node(data: Dict[str, Any], header: Dict[str, Any]):
    '''
    这个方法是在websocket里面与树节点对话的方法,会动态触发思维导图的更新
    task_id
    node_id
    condition
    entities: [str] 活动名列表
    query: 提问
    short_name
    template
    '''
    logger.info(f'[chat_on_node] data={data}')
    try:
        _, middle_nodes = chat_once_and_generate_children(**data)
        for node in middle_nodes:
            query, _ = get_chat_prompt(node.id, type='node', template='last_step')
            data.update({
                'node_id': node.id,
                'query': query,
                'template': 'last_step',
                'short_name': '详细设计',
                'rule_type': '详细设计'
            })
            chat_once_and_generate_children(**data)
    except Exception as e:
        logger.exception(e.args)


def callback_ack(data: Dict[str, Any], header: Dict[str, Any]):
    '''
    每次on_token都需要之前返回过ack才进行发送,不然的话会线程过多卡住其他请求
    node_id
    '''
    node_id = data['node_id']
    for callback in CALLBACKS:
        if callback.node_id == node_id:
            callback.ack = True


def create_root_task(data: Dict[str, Any], header: Dict[str, Any]):
    '''
    task_name:任务名
    rules: List[str] rule_id的列表
    activity_name: 主要活动
    '''
    task_name = data['task_name']
    rules = data['rules']
    root_name = data['activity_name']
    if 'userInfo' in header and 'userLogin' in header['userInfo']:
        user_name = header['userInfo']['userLogin']
    else:
        user_name = 'auto'
    logger.info(f'[create_task] data={data}')

    # 开始任务
    try:
        task = create_task(task_name=task_name, rule_list=rules,
                           status='running', root_name=root_name,
                           user_name=user_name)
        root = create_node(type='root', task_id=task.id,
                           content='root', need_embedding=False)
        time.sleep(1)
        root.children_id = []
        task.root_node = root.id
        root.short_name = task.root_name
        update_node(root)
        update_task(task)
        es_client.refresh(TaskIndex)
        es_client.refresh(TreeNodeIndex)
        on_emit('task/create/done', {'message': '任务创建完毕', 'task_id': task.id})
        chat_on_node_with_rules(rule_list=task.rule_list, task_id=task.id, node_id=root.id, template='first_step')
    except Exception as e:
        logger.exception(e.args)
    return task


def mutiple_rules_chat(data: Dict[str, Any], header: Dict[str, Any]):
    '''
    rule_list: [str] id列表
    task_id
    node_id
    template
    '''
    logger.info(f'[mutiple_rules_chat] data={data}')
    try:
        chat_on_node_with_rules(**data)
    except Exception as e:
        logger.exception(e.args)


class CampaignActivityDispatcher(BaseSocketDispatcher):
    def on_message(self, message):
        '''
        处理websocket的主要函数
        message={"path":xxx,"data":xxx}
        '''
        # super().on_message(message)
        # logger.info('campaign on message = ' +json.dumps(message, ensure_ascii=True))
        path = message['path']
        data = message['data']
        header = message['header']
        if 'userInfo' in header:
            info = urllib.parse.unquote(header['userInfo'])
            user_info = json.loads(info)
            # logger.info(f'[登陆信息] {user_info}')
            ssoid = user_info['ssoId']
            if ssoid is None or len(ssoid) == 0:
                logger.warn('[无效登陆信息]')
            else:
                header['userInfo'] = user_info
        method_dict = {
            'chat/node/ask': chat_on_node,
            'chat/ack': callback_ack,
            'task/create': create_root_task,
            'chat/node/with_rule': mutiple_rules_chat
        }
        method_dict[path](data, header)
