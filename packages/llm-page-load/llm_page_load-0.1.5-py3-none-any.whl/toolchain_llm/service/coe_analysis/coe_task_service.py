import time
from typing import List, Dict
import uuid
from service.coe_analysis.coe_chain_service import run_chain_serial, run_chain
from service.coe_analysis.coe_store_service import batch_sync_coe_storage
from service.coe_analysis.data_structure import Arg, BaseCoeData, COEAnalysisTask
from service.coe_analysis.runners import COETopicAnalysisRunner
from utils import logger
from service.coe_analysis.llm_sdk_importer import es_util
from service.lang_chain_utils.lion_client import client as lion
from service.coe_analysis.coe_thread_executor import coe_executor


def search_task(task_id):
    index = 'coe_analysis_task'
    query = {"query": {"bool": {"must": [{"term": {"id": task_id}}]}}}
    answer = es_util.search(index=index, query=query)
    task = COEAnalysisTask.from_es(answer[0])
    return task, answer[0]['_id']


def update_task(task: COEAnalysisTask, _id: str):
    index = 'coe_analysis_task'
    data = {
        "doc": task.to_json_dict()
    }
    es_util.update(index, id=_id, body=data)


def create_task(
        coe_list: List[Dict],
        name: str, source: str, type_list: List[str],
        submitter: str, to_submit_task: bool = True, extra_args: List[Arg] = [], mis_id=None):
    lion.fetch_config()
    logger.info(f'type list is {type_list}')
    time_stamp = time.time()
    now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.localtime(time_stamp))
    id = str(uuid.uuid1().int)
    index = 'coe_analysis_task'
    # 创建主任务 document
    task = COEAnalysisTask(
        id=id, start_date=now, name=name, submitter=submitter, source=source, state='执行中', extral_args=extra_args,
        progress=f"0/{len(coe_list)}", choosed_coe_list=coe_list, sub_task_type_list=type_list, is_active=True)
    es_util.index(index=index, body=task.to_json_dict(), id=id)
    # 进行同步coestorage
    coe_id_list = [i['_id'] for i in coe_list if '_id' in i]
    coe_executor.submit(batch_sync_coe_storage, coe_id_list)
    # 创建子任务列表，并执行子任务
    if to_submit_task:
        coe_executor.submit(run_chain_serial, coe_id_list, type_list, id, mis_id, name)
    return id


def create_task_sync(
        coe_list: List[Dict],
        name: str, source: str, type_list: List[str],
        submitter: str, to_submit_task: bool = True, to_sync_coe_storage: bool = True):
    lion.fetch_config()
    logger.info(f'type list is {type_list}')
    time_stamp = time.time()
    now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.localtime(time_stamp))
    id = str(uuid.uuid1().int)
    index = 'coe_analysis_task'
    # 创建主任务 document
    task = COEAnalysisTask(
        id=id, start_date=now, name=name, submitter=submitter, source=source, state='执行中',
        progress=f"0/{len(coe_list)}", choosed_coe_list=coe_list, sub_task_type_list=type_list, is_active=True)
    es_util.index(index=index, body=task.to_json_dict(), id=id)
    # 进行同步coestorage
    coe_id_list = [i['_id'] for i in coe_list if '_id' in i]
    if to_sync_coe_storage:
        batch_sync_coe_storage(coe_id_list=coe_id_list)
    # 创建子任务列表，并执行子任务
    if to_submit_task:
        run_chain_serial(coe_id_list, type_list, id)
    return id


def add_coe(coe: BaseCoeData, type: str, task_id: str, to_submit_task: bool = True, threading=False):
    task, _id = search_task(task_id=task_id)
    task.choosed_coe_list.append(coe)
    sub_task_type_list = set(task.sub_task_type_list)
    sub_task_type_list.add(type)
    task.sub_task_type_list = list(sub_task_type_list)
    update_task(task=task, _id=_id)
    if to_submit_task:
        if threading:
            coe_executor.submit(run_chain_serial, [coe.coe_id], [type], task.id)
        else:
            run_chain_serial([coe.coe_id], [type], task_id)


def create_task_by_base_coe_data(coe_list: List[BaseCoeData], name: str, source: str, type_list: List[str],
                                 submitter: str, to_submit_task: bool = True, extral_args: List[Arg] = [],
                                 mis_id: str = None):
    lion.fetch_config()
    logger.info(f'type list is {type_list}')
    time_stamp = time.time()
    now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.localtime(time_stamp))
    id = str(uuid.uuid1().int)
    index = 'coe_analysis_task'
    # 创建主任务 document
    task = COEAnalysisTask(
        id=id, start_date=now, name=name, submitter=submitter, source=source, state='执行中', extral_args=extral_args,
        progress=f"0/{len(coe_list)}", choosed_coe_list=coe_list, sub_task_type_list=type_list, is_active=True)
    es_util.index(index=index, body=task.to_json_dict(), id=id)
    # 创建子任务列表，并执行子任务
    if to_submit_task:
        coe_id_list = [i.coe_id for i in coe_list]
        coe_executor.submit(run_chain_serial, coe_id_list, type_list, id, mis_id)
    return id


def rerun_task(task_id):
    # 不强制执行已经执行了的任务
    coe_executor.submit(run_chain, task_id, force=False)


def get_all_task(size, from_, other_must_inner=[]):
    index = 'coe_analysis_task'
    must_inner = other_must_inner + [{"term": {"is_active": 'true'}}]
    query_json = {
        "query": {
            "bool": {"must": must_inner}
        },
        "sort": [
            {
                "start_date": {"order": "desc"}
            }
        ]
    }
    answer = es_util.client.search(body=query_json, index=index, from_=from_, size=size, headers=es_util.headers)
    hits = answer['hits']['hits']
    task_list = []
    for item in hits:
        task = COEAnalysisTask.from_es(item)
        if (task.start_date is not None):
            task.start_date = task.start_date.split('T')[0]
        if (task.end_date is not None):
            task.end_date = task.end_date.split('T')[0]
        task_list.append(task)
    total = answer['hits']['total']['value']
    return task_list, total


def topic_analysis(topic, task_id):
    runner = COETopicAnalysisRunner(task_id)
    answer, result_list = runner.analysis_once(topic)
    return answer, result_list


def get_single_task(task_id):
    index = 'coe_analysis_task'
    query_json = {
        "query": {
            "bool": {"must": [{"term": {"id": task_id}}]}
        }
    }
    answer = es_util.search(query=query_json, index=index)
    task = COEAnalysisTask.from_es(answer[0])
    if (task.start_date is not None):
        task.start_date = task.start_date.split('T')[0]
    if (task.end_date is not None):
        task.end_date = task.end_date.split('T')[0]
    return task


def test():
    # print(create_task([1,2,3],"测试测试","测试触发"))
    get_all_task(begin_time="2023-05-01", end_time='2023-07-01', size=10, from_=1)


if __name__ == '__main__':
    test()
