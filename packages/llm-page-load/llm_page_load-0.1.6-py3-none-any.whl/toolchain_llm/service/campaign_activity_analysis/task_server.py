import uuid
from service.campaign_activity_analysis.es_client import client, headers,\
    TaskIndex, es_client
from typing import List, Dict, Tuple
from utils import get_now_str
from service.campaign_activity_analysis.tree_node_server \
    import batch_find_node, get_node_deep, find_node
from service.campaign_activity_analysis.datastruct \
    import ChangeLog, TestCaseGenerationTask, DeepTask
import difflib


def create_task(task_name: str, status: str, **kargs)\
        -> TestCaseGenerationTask:
    id = str(uuid.uuid1().int)
    time_stamp = get_now_str()
    task = TestCaseGenerationTask(
        id=id, task_name=task_name, edit_date=time_stamp, status=status,
        **kargs)
    client.index(TaskIndex, body=task.to_json_dict(), headers=headers)
    es_client.refresh(TaskIndex)
    return task


def find_task(id: str) -> Tuple[TestCaseGenerationTask, str]:
    query_josn = {
        "query": {"bool": {"must": [
            {"match": {"id": id}},
        ]}}
    }
    answer = client.search(index=TaskIndex, body=query_josn, headers=headers)
    item = TestCaseGenerationTask.from_es(answer['hits']['hits'][0])
    _id = answer['hits']['hits'][0]['_id']
    return item, _id


def add_task_change_log(task_id: str, changelog: ChangeLog):
    task, _id = find_task(task_id)
    task.change_log.append(changelog)
    data = {
        "doc": task.to_json_dict()
    }
    client.update(index=TaskIndex, id=_id, body=data, headers=headers)


def find_all_task(_size=100, _from=0):
    body = {
        "query": {"bool": {"must": [
            {"match_all": {}}
        ]}},
        "sort": {"edit_date": {"order": "desc"}}
    }
    response = client.search(body=body, index=TaskIndex,
                             size=_size, from_=_from, headers=headers)
    tasks = [TestCaseGenerationTask.from_es(
        i) for i in response['hits']['hits']]
    return tasks


def batch_find_task(id_list: List[str]) -> Dict[str, TestCaseGenerationTask]:
    query = {
        "query": {"bool": {"must": [{"terms": {"id": id_list}}]}},
    }
    answer = client.search(index=TaskIndex, body=query, headers=headers)
    answer = [TestCaseGenerationTask.from_es(
        i) for i in answer['hits']['hits']]
    dict_ans = {i.id: i for i in answer}
    return dict_ans


def get_task_deep(id: str) -> DeepTask:
    '''调用递归方法get_node_deep，返回的是DeepTask结果，也就是带有树指针的结构体'''
    task, _id = find_task(id)
    nd_dict = batch_find_node(task.node_list)
    deep_task = DeepTask.from_json(task.to_json_dict())
    deep_task.tree_result = get_node_deep(deep_task.root_node, nd_dict=nd_dict)
    return deep_task


def update_task(task: TestCaseGenerationTask):
    _, _id = find_task(task.id)
    data = {
        "doc": task.to_json_dict()
    }
    client.update(index=TaskIndex, id=_id, body=data, headers=headers)


def rec_count(item):
    if 'children' not in item:
        if item['type'] != 'query':
            return 1
        else:
            return 0
    else:
        count = 0
        for i in item['children']:
            count += rec_count(i)
        if item['type'] != 'query':
            count += 1
        return count


def div(a, b):
    try:
        return round(a/b, 3)
    except Exception:
        return 0


def task_metricx(id: str):
    task, _id = find_task(id)
    nd_dict = batch_find_node(task.node_list)
    deep_task = DeepTask.from_json(task.to_json_dict())
    deep_task.tree_result = get_node_deep(deep_task.root_node, nd_dict=nd_dict)

    ask_node_count = rec_count(deep_task.tree_result)
    not_accept_count = 0
    result_edit_distance = 0
    result_count = 0
    ans_count = 0
    ans_edit_distance = 0
    for changelog in deep_task.change_log:
        node = nd_dict.get(changelog.ref_node_id, None)
        if node is None:
            node = find_node(changelog.ref_node_id)
        if changelog.type == 'REMOVE_CHILDREN':
            not_accept_count += 1
        elif changelog.type == 'ADD_ANSWER_NODE':
            not_accept_count += 1
        elif changelog.type == 'UPDATE_ANSWER_NODE':
            matcher = difflib.SequenceMatcher(None, a=changelog.old_content, b=changelog.new_content)
            edit_distance = 1 - matcher.quick_ratio()
            if node.type == 'result':
                result_edit_distance += edit_distance
                result_count += 1
            else:
                ans_count += 1
                ans_edit_distance += edit_distance
    deny_ratio = div(not_accept_count, ask_node_count)
    result_edit_distance = div(result_edit_distance, result_count)
    ans_edit_distance = div(ans_edit_distance, ans_count)
    return deny_ratio, result_edit_distance, ans_edit_distance
