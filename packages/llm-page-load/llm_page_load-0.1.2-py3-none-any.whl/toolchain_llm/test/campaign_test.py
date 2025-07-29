from typing import List
from service.campaign_activity_analysis.datastruct import ChangeLog, TestCaseTreeNode
from service.campaign_activity_analysis.entity_server import find_all_entity
from service.campaign_activity_analysis.es_client import TaskIndex, TreeNodeIndex, es_client
from service.campaign_activity_analysis.rule_server import find_all_rule
from service.campaign_activity_analysis.runner import retrive_once
from service.campaign_activity_analysis.chat import chat_on_node_with_rules, llm_chat_call, get_chat_prompt
from service.campaign_activity_analysis.task_server import create_task, update_task, find_task
from service.campaign_activity_analysis.tree_node_server import create_node, get_node_with_exp_message, update_node, find_node, batch_find_node
from test.campaign_data.retrive_aim import retrive_aim
from test.campaign_data.rules_stacking import rules_stacking
import re
from langchain.schema import AIMessage
import time
from utils import logger, write_io, write_json


def test_retrive(aims):
    total = 0
    acc = 0
    for aim in aims:
        inp = aim['input']
        exp = aim['expect']
        retrive_ans = retrive_once(**inp)
        _pass = False
        actual = []
        for msg in retrive_ans:
            if isinstance(msg, AIMessage):
                continue
            actual.append(msg.content)
            if 'search' in exp:
                _match = re.search(exp['search'], msg.content)
                if _match:
                    acc += 1
                    _pass = True
                    break
        if not _pass:
            logger.info(f'{inp} 不准确，期望={exp}，实际={actual}')
        total += 1
    logger.info(f'经验知识抽取准确率 = {acc}/{total} = {acc/total}')
    return acc/total


def dump_rules():
    rules = find_all_rule()
    rules = [rule.to_json_dict() for rule in rules]
    write_json('test/campaign_data/rules.json', rules)


def create_root_task(task_name='叠加baseline', rule_list=[]):
    task = create_task(task_name=task_name, rule_list=rule_list,
                       status='running', root_name=task_name,
                       user_name='auto')
    root = create_node(type='root', task_id=task.id, content='root', need_embedding=False)
    es_client.refresh(TaskIndex)
    es_client.refresh(TreeNodeIndex)
    root.children_id = []
    task.root_node = root.id
    root.short_name = task.root_name
    update_node(root)
    update_task(task)
    es_client.refresh(TaskIndex)
    es_client.refresh(TreeNodeIndex)
    return task.id


def expect_by_rule_content(content: str, act1, act2):
    if '可以叠加' in content:
        return {
            'search': [r'可以[\u4e00-\u9fa5]*叠加'],
            'length': 1
        }
    elif '无法叠加' in content:
        return {
            'search': [act1+r"[\u4e00-\u9fa5]*金额大于",   # 第一个更优惠
                       act2+r"[\u4e00-\u9fa5]*金额大于"],  # 第二个更优惠
            'length': 2
        }

    s = re.findall('可以配置', content)
    if len(s) > 1:
        return {
            'length': 7
        }
    else:
        return {
            'search': [r'可以叠加', act1+r"[\u4e00-\u9fa5]*更优惠", act2+r"[\u4e00-\u9fa5]*更优惠", r'金额[相等|等于]'],
            'length': 4
        }


def test_stacking(task_id: str = None, rule_item_list: List = []):
    entity_name_dict = find_all_entity()
    for k, v in entity_name_dict.items():
        if '闲时立减' in v.entity_name:
            v.entity_name = '闲时立减'
            entity_name_dict[k] = v
            break

    def find_rule_item(node: TestCaseTreeNode):
        for item in rule_item_list:
            if item['rule'] in node.content:
                return item
        return None
    # 重跑任务
    # rule_list = [item['id'] for item in rule_item_list]
    # if task_id is None:
    #     task_id = create_root_task('叠加baseline', rule_list)
    # logger.info('测试任务的id为:' + task_id)
    task, _id = find_task(task_id)
    # task.rule_list = rule_list
    # root, _id = find_node(task.root_node)
    # if root.change_log is None:
    #     root.change_log = []
    # root.change_log.append(ChangeLog(type='删除子节点', ref_node_id=root.id,
    #                        old_children=root.children_id, new_children=[]))
    # root.children_id = []
    # update_node(root)
    # update_task(task)
    # es_client.refresh(TaskIndex)
    # es_client.refresh(TreeNodeIndex)
    # chat_on_node_with_rules(rule_list=rule_list, task_id=task.id, node_id=root.id,
    #                         template='first_step', with_detail=False)
    # 进行测试
    time.sleep(1)
    root, _id = find_node(task.root_node)
    nodes_dict = batch_find_node(root.children_id)
    nodes = [v for _, v in nodes_dict.items()]
    total = 0
    acc = 0
    for node in nodes:
        children_dict = batch_find_node(node.children_id)
        children = [v for _, v in children_dict.items()]
        item = find_rule_item(node)
        total += len(children)
        if item:
            if 'expect' in item:
                expect = item['expect']
            else:
                act1 = entity_name_dict[item['entity_id_list'][0]].entity_name
                act2 = entity_name_dict[item['entity_id_list'][1]].entity_name
                expect = expect_by_rule_content(item['rule'], act1=act1, act2=act2)
            if 'search' in expect:
                yes = 0
                for ptn in expect['search']:
                    for child in children:
                        if re.search(ptn, child.content):
                            yes += 1
                            break
                if yes == expect['length']:
                    acc += yes
                else:
                    logger.info(f'{item} 不准确，期望={expect}')
            elif len(children) == expect['length']:
                acc += len(children)
            else:
                logger.info(f'{item} 不准确，期望={expect}')
        else:
            logger.info(f'没有找到 {node.content}')
    logger.info(f'回答准确率 = {acc}/{total} = {acc/total}')
    return acc/total


if __name__ == '__main__':
    # test_retrive(retrive_aim)
    task_id = '162647287267835067372957879583293575458'
    test_stacking(task_id=task_id, rule_item_list=rules_stacking[:15])
    task_id = '17731262790779954854836059596109386018'
    test_stacking(task_id=task_id, rule_item_list=rules_stacking[15:30])
    task_id = '314677551990357427692406261880010576162'
    test_stacking(task_id=task_id, rule_item_list=rules_stacking[30:])
