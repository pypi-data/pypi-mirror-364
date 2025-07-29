from concurrent.futures import Future, ThreadPoolExecutor, wait
import time
from typing import Any, List, Dict
import uuid
from service.coe_analysis.search_coe_result_item import search_all_chain
from service.coe_analysis.data_structure import BaseCoeData, COEAnalysisTask, COEResult
from service.coe_analysis.runners.coe_cause_aggr import (
    aggr_get_done_runner, aggr_get_runner_by_type, get_aggr_getter_by_type)
from service.coe_analysis.search_coe_result_item import search_coe_result_item
from utils import get_now_str, logger
from service.coe_analysis.llm_sdk_importer import es_util
from service.lang_chain_utils.lion_client import client as lion
from service.coe_analysis.coe_task_service import search_task, update_task
from service.coe_analysis.coe_thread_executor import coe_executor


def bulk_create_aggr_result_info(aggr_id_list, type, task_id):
    index = 'coe_analysis_detail'
    body = []
    result_item_list = []
    for aggr_id in aggr_id_list:
        id = str(uuid.uuid1().int)
        brief = ''
        level = ''
        occur_time = get_now_str()
        edit_time = get_now_str()
        coe_result_item = COEResult(task_id=[str(task_id)], edit_time=edit_time, coe_id=str(
            aggr_id), type=type, id=id, brief=brief, occur_time=occur_time, level=level)
        index_json = coe_result_item.to_json_dict()
        body.append({
            "index": {"_index": index}
        })
        result_item_list.append(coe_result_item)
        body.append(index_json)
    result = es_util.client.bulk(body=body, headers=es_util.headers)
    if result["errors"]:
        raise Exception("bulk操作失败,错误信息为:{}".format(result["errors"]))
    return result_item_list


def aggr_run_chain_once_outter(data_list: List[Any], aggr_id: str, task_id: str, type: str, cause: str, force=True):
    try:
        aggr_run_chain_once(data_list, aggr_id, task_id, type, cause, force)
    except Exception as e:
        logger.exception('执行失败', str(e))


def aggr_run_chain_once(data_list: List[Any], aggr_id: str,
                        task_id: str, type: str, cause: str, force=True):
    result_item, _id = search_coe_result_item(aggr_id, type, task_id)
    # if result_item.is_done and not force:
    #     return coe_id, type, task_id, force
    try:
        result_item.is_reviewed = False
        result_item.pre_checked_passed = True
        result_item.is_done = False
        runner = aggr_get_runner_by_type(result_item=result_item, _id=_id, type=type, data_list=data_list, cause=cause)
        coe_id = result_item.coe_id
        type = result_item.type
        result_item.message = []
        result_item.answer_message = []
        result_item.change_log = []
        result_item.similiar_case_list = []
        logger.info(f'[1.文本获取] coe_id={coe_id},type={type}')
        documents = runner.load()
        documents = runner.split(documents)
        if (len(documents) == 0):
            logger.warn(f'[文本获取失败] coe_id={coe_id},type={type},doc_len={len(documents)}')
            raise Exception(f'[文本获取失败] doc_len={len(documents)}')
        logger.info(f'[2.预校验] coe_id={coe_id},type={type}')
        if not runner.pre_check():
            logger.info('[2.预校验] 不需要进行llm提问')
            runner.done()
            return coe_id, type, task_id, force
        logger.info(f'[3.总结链执行] coe_id={coe_id},type={type},doc_len={len(documents)}')
        existing_answer = runner.summary_and_thought(documents)
        logger.info(f'[4.分析结果] coe_id={coe_id},type={type}\nexisting_answer={existing_answer}')
        answer = runner.analysis_and_answer(existing_answer)
        logger.info(f'[5.Done] 会同步回写COE维度数据 coe_id={coe_id},type={type}\nanswer={answer}')
        runner.done()
        time.sleep(1)  # 等待数据库刷新完成
    except Exception as e:
        # 保存错误信息，is_done变为false
        result_item.error = str(e)
        result_item.is_done = False
        logger.info(result_item.to_json_dict())
        body = {
            "doc": result_item.to_json_dict()
        }
        es_util.update('coe_analysis_detail', id=_id, body=body)
        logger.exception(e.args)
    return coe_id, type, task_id, force


def aggr_run_chain_serial(
        create_begin, create_end, type,
        task_id: str, cause: str, k=20, force=True):
    # 做聚类
    getter = get_aggr_getter_by_type(type)
    getter.init(create_begin, create_end, cause=cause, size=500, k=k,
                is_exclude_light_template=True)
    data_dict: Dict[str, List[Any]] = getter.load()
    # 改进度
    try:
        task, _id = search_task(task_id=task_id)
        task.choosed_coe_list = [BaseCoeData(
            brief=coe.brief, coe_id=coe.coe_id, level=coe.level,
        ) for coe in getter.coe_list]
        task.state = '执行中'
        task.progress = f'0/{len(data_dict.keys())}'
        update_task(task, _id)
        es_util.refresh('coe_analysis_task')
    except Exception as e:
        logger.exception('[任务获取出现异常]' + str(e))
        return
    # 创建子任务列表，并执行子任务
    lion.fetch_config()
    fresh_time = int(lion.config.get(f'{lion.app_name}.fresh_time', 1))
    try:
        result_list = bulk_create_aggr_result_info([str(k) for k, v in data_dict.items()], type, task_id)
        time.sleep(fresh_time)  # 写入需要 1s 进行刷盘
    except Exception as e:
        logger.exception('[子任务创建失败]' + str(e))

    if result_list is None:
        result_list, _ = search_all_chain(task_id)
    done = {'data': 0}  # 线程安全
    total = len(data_dict.keys())
    type_count = len(task.sub_task_type_list)
    done_count = {str(k): 0 for k, _ in data_dict.items()}
    futures: List[Future] = []
    lion.fetch_config()
    excutor = ThreadPoolExecutor(max_workers=int(lion.config[lion.app_name+'.chain_thread_max_num']),
                                 thread_name_prefix='chain-thread')

    def call_back(worker: Future):
        '''更新进度'''
        if worker.exception():
            logger.exception("子任务执行异常: {}".format(worker.exception()))
            return
        try:
            coe_id, type, task_id, force = worker.result()
            logger.info("called worker callback function, {},{},{}".format(coe_id, type, force))
            if (coe_id in done_count):
                done_count[coe_id] += 1
                if (done_count[coe_id] == type_count):
                    done['data'] += 1
            done_data = done['data']
            progress = f'{done_data}/{total}'
            task.progress = progress
            time.sleep(1)
            update_task(task, _id)
            time.sleep(1)
        except Exception as e:
            logger.exception(f'[子任务 callback 异常] coeid={coe_id}, type={type} task_id={task_id}', e)

    # for coe in task.choosed_coe_list:
    #     coe_id = coe.coe_id
    #     future = excutor.submit(sync_crawler_data, coe_id)
    #     futures.append(future)

    for item in result_list:
        type = item.type
        aggr_id = item.coe_id
        if aggr_id not in data_dict:
            continue
        data_list = data_dict[aggr_id]
        future = excutor.submit(aggr_run_chain_once, data_list, aggr_id, task_id, type, cause, force)
        future.add_done_callback(call_back)
        futures.append(future)
    try:
        wait(futures)
    except Exception as e:
        logger.exception(e.args)

    time.sleep(2)
    try:
        # 执行最后评测
        done_runner = aggr_get_done_runner(type=type, task_id=task_id)
        if done_runner:
            done_runner.aggr_to_one()
            done_runner.done()

        time_stamp = time.time()
        now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.localtime(time_stamp))
        task, _id = search_task(task_id)
        task.end_date = now
        task.state = '已完成'
        update_task(task, _id)
    except Exception as e:
        logger.exception(e.args)


def aggr_task_create(name, submitter, source, cause, create_begin, create_end, k=75,
                     type='aggr_by_experience'):
    lion.fetch_config()
    time_stamp = time.time()
    now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.localtime(time_stamp))
    id = str(uuid.uuid1().int)
    index = 'coe_analysis_task'
    # 创建主任务 document
    task = COEAnalysisTask(
        id=id, start_date=now, name=name, submitter=submitter, source=source, state='执行中',
        progress="-/-", choosed_coe_list=[], sub_task_type_list=[type], is_active=True)
    es_util.index(index=index, body=task.to_json_dict(), id=id)
    es_util.refresh(index)
    coe_executor.submit(aggr_run_chain_serial, create_begin, create_end, type, task.id, cause, k)
    return id
