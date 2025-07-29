'''chat.py和run.py都是大模型的调用代码，前者用于websocket版调用，后者用于普通html调用'''
from uuid import UUID
from typing import Any, List, Union
from langchain import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage
from langchain.callbacks.base import BaseCallbackHandler
from service.campaign_activity_analysis.config_reader \
    import OPENAI_API_BASE, OPENAI_API_KEY, \
    get_model_config, get_prompt, on_emit
from service.campaign_activity_analysis.datastruct import TestCaseTreeNode
from service.campaign_activity_analysis.entity_server \
    import find_all_entity, search_or_create_entity
from service.campaign_activity_analysis.rule_server import batch_find_rule, create_rule
from service.campaign_activity_analysis.runner\
    import retrive_once, get_query_thought_list
from service.campaign_activity_analysis.task_server \
    import find_task, update_task
from service.campaign_activity_analysis.tree_node_server \
    import create_node, find_node, update_node
from utils import logger
import time
import json


class ChatCallBack(BaseCallbackHandler):
    def __init__(self, node_id):
        self.node_id = node_id
        self.ack = True
        self.token = ''

    def on_llm_new_token(self, token: str, *, run_id: UUID,
                         parent_run_id: Union[UUID, None] = None,
                         **kwargs: Any) -> Any:
        self.token += token
        if (self.ack):
            on_emit('chat/new_token',
                    {'token': self.token, 'node_id': self.node_id})
            self.ack = False
            self.token = ''
        return super().on_llm_new_token(token, run_id=run_id,
                                        parent_run_id=parent_run_id, **kwargs)


CALLBACKS: List[ChatCallBack] = []
'''callback列表可以用于外部遍历，更新ack状态'''


def add_callback(node_id):
    callback = ChatCallBack(node_id)
    CALLBACKS.append(callback)
    return callback


def get_chat_prompt(node_id: str, type: str, template: str):
    node, _id = find_node(node_id)
    prompt = get_prompt(type, template)
    _json_data = {}
    if (node.type == 'middle'):
        _json_data.update(json.loads(node.content))
    _input = {}
    other_key = []
    for key in prompt.input_variables:
        if key in _json_data:
            _input[key] = _json_data[key]
            continue
        _input[key] = '{'+key+'}'
        other_key.append(key)
    return prompt.format_prompt(**_input).to_string(), other_key


def llm_chat_call(condition: str, rule_type: str, query: str, callback: ChatCallBack):
    llm = ChatOpenAI(openai_api_base=OPENAI_API_BASE,
                     openai_api_key=OPENAI_API_KEY,
                     streaming=True,
                     **get_model_config())
    prompt = ChatPromptTemplate(
        messages=[
            *retrive_once(query=condition, rule_type=rule_type, k=4),  # 使用rule的condition而非整体query，避免干扰信息
            HumanMessage(content=query)
        ],
        input_variables=[]
    )
    chain = LLMChain(prompt=prompt, llm=llm, verbose=True)
    res = chain.predict(callbacks=[callback])
    res = res.replace('\u200b', ' ')
    logger.info(f'[output] {res}')
    thought_list = get_query_thought_list(res)
    return res, thought_list


def chat_once_and_generate_children(task_id: str, node_id: str, rule_type: str,
                                    condition: str, entities: List[str],
                                    query: str, short_name: str,
                                    template: str):
    '''主要对话函数，它代表了一次增加query节点的操作，这个操作专门用于websocket'''
    task, _ = find_task(task_id)
    node, _ = find_node(node_id)
    entity_item_list = []
    if template != 'final_step':
        for entity_name in entities:
            entity = search_or_create_entity(entity_name)
            entity_item_list.append(entity)
        rule = create_rule(condition, entity_item_list=entity_item_list, short_name=short_name, type=rule_type)
        child_node = create_node(type='query', content=query, children_id=[],
                                 need_embedding=True, short_name=short_name,
                                 task_id=task_id, parent_id=node_id, reference_rule_id_list=[rule.id])
    else:
        condition = query
        rule_type = '详细设计'
        child_node = create_node(type='query', content=query, children_id=[],
                                 need_embedding=True, short_name='详细设计',
                                 task_id=task_id, parent_id=node_id, reference_rule_id_list=[])
    node.children_id.append(child_node.id)
    task.node_list.append(child_node.id)
    update_node(node)
    update_task(task)
    time.sleep(1)  # 等待新节点刷盘
    logger.info('[chat]节点创建完成 id={}'.format(child_node.id))
    on_emit('chat/create', {'message': '节点创建完毕', 'node_id': node.id})

    callback = add_callback(child_node.id)
    res, thought_list = llm_chat_call(condition, rule_type, query, callback)
    child_node.answer_message = res
    child_child_node_list: List[TestCaseTreeNode] = []
    if (thought_list is not None and len(thought_list) != 0):
        for thought in thought_list:
            thought_str = json.dumps(thought, ensure_ascii=False)
            child_child_node = \
                create_node(type='middle', task_id=task_id,
                            content=thought_str,
                            need_embedding=False,
                            short_name=thought['test_case_description'],
                            parent_id=child_node.id)
            child_node.children_id.append(child_child_node.id)
            child_child_node_list.append(child_child_node)
            task.node_list.append(child_child_node.id)
    else:
        child_child_node = create_node(type='result', task_id=task_id,
                                       content=res, need_embedding=False,
                                       short_name='结果',
                                       parent_id=child_node.id)
        child_node.children_id.append(child_child_node.id)
        child_child_node_list.append(child_child_node)
        task.node_list.append(child_child_node.id)
    update_node(child_node)
    update_task(task)
    time.sleep(1)  # 等待新节点刷盘
    on_emit('chat/end', {'message': '结果生成完毕', 'node_id': node.id})
    return child_node, child_child_node_list


def chat_on_node_with_rules(rule_list: List[str], task_id: str, node_id: str, template: str, with_detail: bool = True):
    '''
    rule_list: List[str] rule_id的列表
    task_id
    node_id
    template : prompt 模板选择
    '''
    entity_name_dict = find_all_entity()
    for k, rule in batch_find_rule(rule_list).items():
        try:
            query, vars = get_chat_prompt(node_id, type='node', template=template)
            query = query.replace('{'+vars[0]+'}', rule.rule)
            entities = [entity_name_dict[i].entity_name for i in rule.entity_id_list]
            _, middle_nodes = chat_once_and_generate_children(
                task_id=task_id, node_id=node_id, condition=rule.rule, entities=entities, rule_type=rule.type,
                query=query, short_name=rule.short_name, template=template
            )
            if not with_detail:
                continue
            for node in middle_nodes:
                query, _ = get_chat_prompt(node.id, type='node', template='last_step')
                chat_once_and_generate_children(
                    task_id=task_id, node_id=node.id, condition=rule.rule, entities=entities, rule_type='详细设计',
                    query=query, short_name='详细设计', template='last_step')
        except Exception as e:
            logger.exception(e.args)
