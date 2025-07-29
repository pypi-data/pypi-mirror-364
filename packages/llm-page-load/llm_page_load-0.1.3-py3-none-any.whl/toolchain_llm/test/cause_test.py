from typing import Dict, List
from sklearn import preprocessing
from service.coe_analysis.aggr_task_service import aggr_task_create
from service.coe_analysis.coe_chain_service import \
    bulk_create_result_info, search_task, update_chain_result, update_task
from service.coe_analysis.coe_experience_service import batch_find_experience, experience_mark_update, find_experience
from service.coe_analysis.coe_store_service import _get_result_, batch_sync_coe_result, list_coe, search_coe, sync_coe_result, sync_once
from service.coe_analysis.coe_task_service import create_task
from service.coe_analysis.config_reader import OPENAI_API_BASE, OPENAI_API_KEY
from service.coe_analysis.crawler.getDoc import getLatestId
from service.coe_analysis.crawler_data_service import sync_crawler_data, delete_passed, find_crawler_data
from service.coe_analysis.runners import get_runner_by_type
from service.coe_analysis.search_coe_result_item import batch_search_chain_by_id, search_all_chain, search_coe_result_item
from utils import get_now_str, logger, read_json, write_json, write_io
from service.coe_analysis.llm_sdk_importer import es_util
from service.coe_analysis.data_structure import BaseCoeData, COEResult, Experience
import re
from service.lang_chain_utils.embedding import embed
import time
import jieba
from concurrent.futures import ThreadPoolExecutor, Future, wait
from sklearn.metrics import roc_auc_score, pairwise_distances
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, AIMessage
from token_count.tokenizer import count_token


def run_chain_once(coe_id, type, task_id, force=True):
    '''执行一次子任务，force代表是否强制执行，如果否，那么不重复执行已完成的任务'''
    result_item, _id = search_coe_result_item(coe_id, type, task_id)
    if result_item.is_done and not force:
        return
    if result_item.is_reviewed:
        return
    try:
        # result_item.is_reviewed = False
        # result_item.pre_checked_passed = True
        # result_item.is_done = False
        runner = get_runner_by_type(result_item=result_item, _id=_id, type=type)
        runner.to_do_total = True  # 必须进行LLM提问
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
            logger.warn(
                f'[文本获取失败] coe_id={coe_id},type={type},doc_len={len(documents)}')
            raise Exception(f'[文本获取失败] doc_len={len(documents)}')
        logger.info(f'[2.预校验] coe_id={coe_id},type={type}')
        if not runner.pre_check():
            logger.info('[2.预校验] 不需要进行llm提问')
            runner.done()
            return
        logger.info(
            f'[3.总结链执行] coe_id={coe_id},type={type},doc_len={len(documents)}')
        existing_answer = runner.summary_and_thought(documents)
        logger.info(
            f'[4.分析结果] coe_id={coe_id},type={type}')
        answer = runner.analysis_and_answer(existing_answer)
        logger.info(f'[5.Done] coe_id={coe_id},type={type}\nanswer={answer}')
        runner.done()
    except Exception as e:
        # 保存错误信息，is_done变为false
        result_item.error = str(e)
        result_item.is_done = False
        body = {
            "doc": result_item.to_json_dict()
        }
        es_util.update('coe_analysis_detail', id=_id, body=body)
        raise e
    return


def create_in_all(data, name, type_list=['to_test']):
    coe_id_list = [i['coe_id'] for i in data]
    coe_list = [BaseCoeData.from_json(i).to_json_dict() for i in data]
    task_id = create_task(coe_list, name=name, source='自动触发', type_list=type_list, submitter='lyl',
                          to_submit_task=False)
    logger.info(f'task id = {task_id}')
    bulk_create_result_info(coe_id_list=coe_id_list, type_list=type_list, task_id=task_id)
    # task, _id = search_task(task_id)
    # task.is_active = True
    # update_task(task=task, _id=_id)
    return task_id


def metricx(task_id, top_p=1):
    result_list, total = search_all_chain(task_id)
    yes = 0
    total = 0
    for result_item in result_list:
        if len(result_item.answer_message) == 0:
            continue
        coe, _id = search_coe(result_item.coe_id)
        if coe.cause_analysis.rd_result == 'None':
            continue
        total += 1
        for p in range(top_p):
            res = _get_result_(result_item, p)
            if res and res == coe.cause_analysis.rd_result:
                yes += 1
                break
    print(f'task_id={task_id} top-{top_p}结果 {yes}/{total}={yes/total}')
    return yes, total


def del_exp_5month(task_id='10376470799079360590495123018797289762', type='cause'):
    result_list, total = search_all_chain(task_id, from_=0, size=1000)
    # _, exp_dict = batch_find_experience([i.answer_message[0].exp_id for i in result_list if len(i.answer_message) > 0])
    for chain in result_list:
        if chain.type != type:
            continue
        # chain.is_reviewed = False
        # update_chain_result(chain=chain)
        try:
            sync_coe_result(chain.coe_id, type=type)
        except Exception as e:
            logger.exception(f'同步 {chain.coe_id} 失败'+ e.args)
        # answer = chain.answer_message[0].exp_id
        # exp = exp_dict.get(answer)
        # experience_mark_update(exp.id, is_marked=True, sleep=False)


def get_5month_data(task_id='135466354620276601608175835433368817954', type='cause'):
    result_list, total = search_all_chain(task_id, from_=0, size=1000)
    items = []
    for chain in result_list:
        if chain.type != type:
            continue
        res = _get_result_(chain)
        item = {
            'coe_id': chain.coe_id,
            'brief': chain.brief,
            'level': chain.level,
            'cause': res
        }
        items.append(item)
    write_json('test/data/baseline_cause_5month.json', items)


def get_6month_data():
    coe_list, total = list_coe(create_begin='2023-06-01', create_end='2023-06-30',
                               size=80, _from=0, is_exclude_light_template=True)
    coes = []
    for ind, coe in enumerate(coe_list):
        if coe.cause_analysis is None:
            continue
        if coe.cause_analysis.rd_result is None:
            continue
        # if coe.cause_analysis.analysis_result is not None:
        #     continue
        coes.append({
            'index': ind,
            'brief': coe.brief,
            'coe_id': str(coe.coe_id),
            'level': coe.level,
            'cause': coe.cause_analysis.rd_result
        })
    write_json('test/data/baseline_cause_6month.json', coes)

# 279769762081047964678516856588471374114 原因分析13数据集
# 71554415070163054370816446425208983842  原因分析13数据集，有规则
# 72647669748284547755302006952713785634  原因分析13数据集，有规则B
# 135466354620276601608175835433368817954 5月标准结果
# 10376470799079360590495123018797289762 原因分析5月gpt-4测评
# 203427561608963338040830040347234013474 原因分析7月gpt-4测评
# 241819513759714651790002378773920485666 原因分析6月


def calcluate_acc(task_id: str, data: List[dict], type: str = 'cause'):
    result_list, _ = search_all_chain(task_id, from_=0, size=10000)
    result_dict = {str(item.coe_id): item for item in result_list if item.type == type and len(item.message) != 0}
    total = 0
    acc = 0
    for item in data:
        coe_id = item.get('coe_id')
        brief = item.get('brief')
        if 'cause' not in item:
            continue
        total += 1
        result = result_dict[coe_id]
        ans = _get_result_(result_item=result)
        cause = item.get('cause')
        if ans == cause:
            acc += 1
        else:
            print(f'线上问题: {brief}\ncoe_id: {coe_id}\nLLM分析: {ans}\n标准: {cause}\n')
    print(f'{acc}/{total} = {acc/total}')
    return acc/total


def main():
    data = read_json('test/data/baseline_cause_6month.json')
    cur_type = 'cause'
    # task_id = create_in_all(data, name='原因分析6月', type_list=['cause'])
    # print(task_id)
    # task_id = '279769762081047964678516856588471374114'
    # task_id = '71554415070163054370816446425208983842'
    # task_id = '40925475018717133271756641305578829794'
    task_id = '172277232291932626729440512393527818210'
    # coe_id_list = [(d['coe_id'], d) for d in data if d['coe_id']]

    features: List[Future] = []
    coe_id_list = [('249853', {})]
    for coe_id, item in coe_id_list:
        print(coe_id)
        # delete_passed(coe_id)
        # sync_crawler_data(coe_id)
        # no_self_prove = False
        try:
            # feature = coe_executor.submit(run_chain_once, coe_id, cur_type, task_id, True, no_self_prove)
            # features.append(feature)
            run_chain_once(coe_id=coe_id, type=cur_type, force=True, task_id=task_id)
        except Exception as e:
            logger.exception(e.args)

    wait(features)


class SetList:
    def __init__(self):
        self.data = set()

    def add(self, d):
        self.data.add(d)

    def __dict__(self):
        return list(self.data)


def _delete_task():
    task_id = '88653637685825202761681672668035319777'
    result_list, _ = search_all_chain(task_id=task_id)
    from service.coe_analysis.llm_sdk_importer import es_util
    client = es_util.client
    exit_coe_ids = set()
    choosed_coe_list = []
    for result in result_list:
        if result.coe_id not in exit_coe_ids:
            exit_coe_ids.add(result.coe_id)
            choosed_coe_list.append(BaseCoeData(coe_id=result.coe_id, brief=result.brief, level=result.level))
            continue
        # chains, _ids = batch_search_chain_by_id(chain_id_list=[result.id])
        # for exp in result.answer_message:
        #     try:
        #         exp_id = exp.exp_id
        #         exp, exp_id_ = find_experience(id=exp_id)
        #         client.delete(index='coe_analysis_experience', id=exp_id_)
        #     except Exception as e:
        #         logger.error(e)
        # client.delete(index='coe_analysis_detail', id=_ids[0])
    # search_coe_result_item_list(coe_id=coe_id, type=type, task_id=task_id)
    task, _id = search_task(task_id=task_id)
    task.choosed_coe_list = choosed_coe_list
    update_task(task=task, _id=_id)
    time.sleep(1)
    batch_sync_coe_result(coe_id_list=list(exit_coe_ids), type_list=['cause'])


if __name__ == '__main__':
    # get_6month_data()
    # main()
    # calcluate_acc('241819513759714651790002378773920485666', data=read_json('test/data/baseline_cause_6month.json'))
    _delete_task()
