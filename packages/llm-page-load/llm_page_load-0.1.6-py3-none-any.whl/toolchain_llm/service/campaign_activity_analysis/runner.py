import uuid
import json
from typing import Dict, List
from langchain import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, \
    SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain.schema import HumanMessage, AIMessage, BaseMessage
from service.campaign_activity_analysis.task_server \
    import create_task, find_task, update_task
from service.campaign_activity_analysis.tree_node_server \
    import node_similarity_search, get_node_with_exp_message, find_node,\
    create_node, create_node_by_instance, update_node, get_query_thought_list
from service.campaign_activity_analysis.entity_server \
    import search_or_create_entity, batch_find_entity
from service.campaign_activity_analysis.rule_server \
    import batch_find_rule, create_rule
from service.campaign_activity_analysis.config_reader \
    import get_config, OPENAI_API_BASE, OPENAI_API_KEY, \
    get_model_config, get_prompt
from service.campaign_activity_analysis.datastruct \
    import TestCaseTreeNode, TestCaseGenerationTask, CampaignRule
from service.campaign_activity_analysis.es_client \
    import es_client, TreeNodeIndex
from concurrent.futures import ThreadPoolExecutor
from token_count.tokenizer import count_token
from utils import logger
import time

executor = ThreadPoolExecutor(max_workers=int(get_config('thread_max_num')))


def retrive_once(query: str, rule_type: str, k: int = 3, max_token: int = 2000) -> List[BaseMessage]:
    '''此处的retrive,通过get_node_with_exp_message方法,找出answer_message,保证真实性,但是需要多步查询'''
    nodes = node_similarity_search(query=query, rule_type=rule_type, k=k)
    messages = []
    nodes = get_node_with_exp_message(nodes)
    token = 0
    for node in nodes:
        human = node.content.replace('\u200b', '')
        ai = node.answer_message.replace('\u200b', '')
        add_token = count_token(human) + count_token(ai)
        if (token+add_token > max_token):
            continue
        messages.append(HumanMessage(content=human, example=True))
        messages.append(AIMessage(content=ai, example=True))
        token += add_token
    return messages


def final_step(parent: TestCaseTreeNode):
    '''单独列出最后一问的方法'''
    system = get_prompt('stacking', 'system')
    last_step = get_prompt('stacking', 'last_step')
    input = json.loads(parent.content)
    prompt = ChatPromptTemplate(messages=[
        SystemMessagePromptTemplate(prompt=system),
        HumanMessagePromptTemplate(prompt=last_step)
    ], input_variables=last_step.input_variables)
    llm = ChatOpenAI(openai_api_base=OPENAI_API_BASE,
                     openai_api_key=OPENAI_API_KEY, streaming=True,
                     **get_model_config())
    chain = LLMChain(prompt=prompt, llm=llm, verbose=True)
    query = HumanMessagePromptTemplate(
        prompt=last_step).format(**input).content
    logger.info(f'[input]{query}')
    _id = str(uuid.uuid1().int)
    query_node = TestCaseTreeNode(id=_id, type='query', task_id=parent.task_id,
                                  content=query, parent_id=parent.id,
                                  short_name='详细设计')
    for i in range(3):
        try:
            result = chain.predict(**input)
            query_node.answer_message = result
            break
        except Exception as e:
            logger.exception(e.args)
            logger.info('睡30s')
            time.sleep(30)
    logger.info(f'[output]{result}')
    child = create_node(type='result', content=result, need_embedding=True,
                        task_id=parent.task_id, parent_id=_id, short_name='结果')
    query_node.children_id = [child.id]
    create_node_by_instance(query_node, need_embedding=True)
    if (parent.children_id is None or len(parent.children_id) == 0):
        parent.children_id = []
    parent.children_id.append(_id)
    update_node(parent)
    return [_id, child.id]


def root_extend_by_rule(rule: CampaignRule, parent: TestCaseTreeNode):
    '''从某个节点进行提问,需要传入的是叠加规则'''
    first_step = get_prompt('stacking', 'first_step')
    system = get_prompt('stacking', 'system')
    input = {'condition': rule.rule}
    index = 1
    entities = []
    for id, entity in batch_find_entity(id_list=rule.entity_id_list).items():
        input[f'entity{index}'] = entity.entity_name
        entities.append(entity)
        index += 1
    llm = ChatOpenAI(openai_api_base=OPENAI_API_BASE,
                     openai_api_key=OPENAI_API_KEY, streaming=True,
                     **get_model_config())
    query = first_step.format(**input)
    prompt = ChatPromptTemplate(
        messages=[
            SystemMessagePromptTemplate(prompt=system),
            *retrive_once(query=rule.rule, rule_type=rule.type),  # 使用rule的condition进行匹配，避免干扰信息过多
            HumanMessage(content=query)
        ],
        input_variables=[]
    )
    _id = str(uuid.uuid1().int)
    query_node = TestCaseTreeNode(id=_id, task_id=parent.task_id, type='query',
                                  content=query, parent_id=parent.id,
                                  reference_rule_id_list=[rule.id])
    parent.children_id.append(query_node.id)
    if (rule.type == 'stacking'):
        query_node.short_name = f'与{entity.entity_name}{rule.rule}'
    query = create_node_by_instance(query_node, need_embedding=True)
    update_node(parent)
    es_client.refresh(TreeNodeIndex)
    chain = LLMChain(prompt=prompt, llm=llm, verbose=True)
    logger.info(f'[input]{prompt.format()}')
    for i in range(3):
        try:
            result = chain.predict()
            query_node.answer_message = result
            break
        except Exception as e:
            logger.exception(e.args)
            logger.info('睡30s')
            time.sleep(30)
    logger.info(f'[output]{result}')
    answer_list = get_query_thought_list(result)
    child_id_list = []
    deep_id = []
    for answer in answer_list:
        child = create_node(content=json.dumps(answer, ensure_ascii=False),
                            task_id=parent.task_id, type='middle',
                            need_embedding=False, parent_id=_id,
                            short_name=answer['test_case_description'])
        child_id_list.append(child.id)

        more_id = final_step(child)
        deep_id += more_id

    query_node.children_id = child_id_list
    update_node(query_node)
    es_client.refresh(TreeNodeIndex)

    return [_id, *deep_id], _id


def chat_with_stack_rule(task: TestCaseGenerationTask):
    '''从叠加规则构造思维导图,但是没有接入websocket'''
    try:
        root = create_node(type='root', task_id=task.id,
                           content='root', need_embedding=False)
        id_list = [root.id]
        root.children_id = []
        task.root_node = root.id
        root.short_name = task.root_name
        time.sleep(1)
        update_node(root)
        update_task(task)
        for k, rule in batch_find_rule(task.rule_list).items():
            task.progress += 1
            new_ids, child_id = root_extend_by_rule(rule, root)
            id_list += new_ids
            task.node_list = id_list
            # root.children_id.append(child_id)
            update_node(root)
            update_task(task)
        task.status = 'done'
        time.sleep(1)
        update_task(task)
    except Exception as e:
        logger.exception(e.args)
    return task


def chat_with_node(task: TestCaseGenerationTask, node: TestCaseTreeNode,
                   rule: CampaignRule):
    '''从某个节点进行提问,这个方法已经废弃'''
    new_ids, child_id = root_extend_by_rule(rule, node)
    task.node_list += new_ids
    update_node(node)
    update_task(task)


def run_task_by_info_dict(payload: Dict, username: str) \
        -> TestCaseGenerationTask:
    '''创建新的思维导图的主要方法'''
    task_name = payload['task_name']
    activity_name = payload['activity_name']
    activity_stack_rule_map = payload['activity_stack_rule_map']
    main_act = search_or_create_entity(activity_name)
    rules = []
    for k, v in activity_stack_rule_map.items():
        sub_act = search_or_create_entity(k)
        rule = create_rule(v, entity_item_list=[
                           main_act, sub_act], type='stacking')
        rules.append(rule.id)
    time.sleep(1)
    task = create_task(task_name=task_name, rule_list=rules,
                       status='running', root_name=activity_name,
                       user_name=username)
    executor.submit(chat_with_stack_rule, task)
    return task


def run_task_by_node(payload: Dict):
    '''从某个节点进行提问,这个方法已经废弃'''
    node_id = payload['node_id']
    task_id = payload['task_id']
    entity_list = payload['entity_list']
    content = payload['content']
    type = payload['type']
    entity_item_list = []
    for entity_name in entity_list:
        entity = search_or_create_entity(entity_name)
        entity_item_list.append(entity)
    rule = create_rule(content, entity_item_list=entity_item_list, type=type)
    node, _ = find_node(node_id)
    task, _ = find_task(task_id)
    executor.submit(chat_with_node, task, node, rule)


if __name__ == '__main__':
    p = get_prompt('stacking', 'first_step')
    print(p)
