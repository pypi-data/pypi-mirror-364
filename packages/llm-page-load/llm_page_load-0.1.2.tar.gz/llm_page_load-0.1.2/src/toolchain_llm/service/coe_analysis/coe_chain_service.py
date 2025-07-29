import json
from concurrent.futures import Future, ThreadPoolExecutor, wait
from typing import Dict, List
from service.coe_analysis.coe_experience_service \
    import batch_find_experience, find_experience, save_experience_by_id
from service.coe_analysis.coe_result_to_wiki import make_wiki_for_general,  \
    make_wiki_for_report, make_wiki_for_report_text, make_wiki_for_report_V2
from service.coe_analysis.crawler import getDoc
import uuid
import time
from datetime import datetime

from service.coe_analysis.crawler.getDoc import get_tag, getCoeJson, getToDoText
from service.coe_analysis.data_structure import BaseCoeData, COEAnalysisTask, COEResult, ChangeLog, COEStoreageData
from service.coe_analysis.result_analysis import get_result_to_show
from service.coe_analysis.runners import get_runner_by_type
from service.coe_analysis.search_coe_result_item import search_all_chain, search_coe_result_item
from tools.dx import send_dx_message_to_person
from utils import logger
import jieba.analyse
import jieba
from service.coe_analysis.llm_sdk_importer import TASK_TYPES, es_util, is_type_regietered
from service.lang_chain_utils.lion_client import client as lion
from service.lang_chain_utils.embedding import embed
from utils import get_now_str
from service.coe_analysis.coe_store_service import batch_search_coe_storage, search_coe
from llmcore_sdk.utils.wiki_utils import WikiDocument, wiki_maker
import re
import requests
import traceback
from service.coe_analysis.coe_thread_executor import coe_es_writer

lion.fetch_config()
post_xgpt_agent = lion.config.get(f'{lion.app_name}.post_xgpt_agent')
post_xgpt_agent_dict = json.loads(post_xgpt_agent)
XGPT_URL = post_xgpt_agent_dict["xgpt_url"]
XGPT_TOKEN = post_xgpt_agent_dict["xgpt_token"]


def create_result_info(coe_id, type, task_id):
    index = 'coe_analysis_detail'
    id = str(uuid.uuid1().int)
    coe = getDoc.getCoeJson('', coe_id)
    brief = coe['incident']['brief']
    level = coe['incident']['level']
    occur_time = coe['incident']['occur_time'].replace(' ', 'T') + 'Z'
    edit_time = get_now_str()
    coe_result_item = COEResult(task_id=[str(task_id)], edit_time=edit_time, coe_id=str(
        coe_id), type=type, id=id, brief=brief, occur_time=occur_time, level=level)
    index_json = coe_result_item.to_json_dict()
    es_util.index(index=index, body=index_json, id=id)


def create_result_info_by_item(result_item: COEResult):
    index = 'coe_analysis_detail'
    id = str(uuid.uuid1().int)
    edit_time = get_now_str()
    result_item.id = id
    result_item.edit_time = edit_time
    index_json = result_item.to_json_dict()
    es_util.index(index=index, body=index_json, id=id)
    return result_item


def batch_search_chain_by_id_with_experience_as_json(chain_id_list: List[str], size: int = 1000):
    try:
        query_josn = {
            "_source": {"excludes": ['search_vector']},
            "query": {"bool": {"must": [
                {"terms": {"id": chain_id_list}}
            ]}},
            "size": size
        }
        answer = es_util.search(index='coe_analysis_detail', query=query_josn)
        items = [COEResult.from_es(i) for i in answer]
        exp_ids = []
        for item in items:
            exp_ids.extend([i.exp_id for i in item.answer_message])
        exp_list, exp_dict = batch_find_experience(id_list=exp_ids)
        ans = {}
        for item in items:
            ans_msg = [exp_dict.get(i.exp_id, None) for i in item.answer_message]
            json_item = item.to_json_dict()
            json_item['answer_message'] = [i.to_json_dict() for i in ans_msg if i is not None]
            ans[item.coe_id] = json_item
        return ans
    except Exception:
        return None, None


def bulk_create_result_info(coe_id_list, type_list, task_id):
    index = 'coe_analysis_detail'
    body = []
    result_item_list = []
    for coe_id in coe_id_list:
        coe = getDoc.getCoeJson('', coe_id)
        for type in type_list:
            try:
                result_item, _id = search_coe_result_item(coe_id=coe_id, type=type, task_id=task_id)
                if result_item is not None:
                    result_item_list.append(result_item)
                    continue
            except Exception:
                pass
            id = str(uuid.uuid1().int)
            brief = coe['incident']['brief']
            level = coe['incident']['level']
            occur_time = coe['incident']['occur_time'].replace(' ', 'T') + 'Z'
            edit_time = get_now_str()
            coe_result_item = COEResult(task_id=[str(task_id)], edit_time=edit_time, coe_id=str(
                coe_id), type=type, id=id, brief=brief, occur_time=occur_time, level=level)
            index_json = coe_result_item.to_json_dict()
            body.append({
                "index": {"_index": index}
            })
            result_item_list.append(coe_result_item)
            body.append(index_json)
    if len(body) == 0:
        return result_item_list
    result = es_util.client.bulk(body=body, headers=es_util.headers)
    if result["errors"]:
        raise Exception("bulk操作失败,错误信息为:{}".format(result["errors"]))
    return result_item_list


def bulk_create_chain_by_object(chains: List[COEResult]):
    index = 'coe_analysis_detail'
    body = []
    for chain in chains:
        body.append({"index": {"_index": index}})
        body.append(chain.to_json_dict())
    result = es_util.client.bulk(body=body, headers=es_util.headers)
    if result["errors"]:
        raise Exception("bulk操作失败,错误信息为:{}".format(result["errors"]))


def run_chain_once(coe_id, type, task_id, force=True, extra_args=[]):
    '''执行一次子任务，force代表是否强制执行，如果否，那么不重复执行已完成的任务'''
    result_item, _id = search_coe_result_item(coe_id, type, task_id)
    try:
        result_item.is_reviewed = False
        result_item.pre_checked_passed = True
        result_item.is_done = False
        runner = get_runner_by_type(result_item=result_item, _id=_id, type=type, extra_args=extra_args)
        if result_item.is_done and not force:
            return runner
        coe_id = result_item.coe_id
        type = result_item.type
        result_item.message = []
        result_item.answer_message = []
        result_item.change_log = []
        result_item.similiar_case_list = []

        logger.info(f'[1.文本获取] coe_id={coe_id},type={type}')
        documents = runner.load()  # 完整的COE信息
        additional_information = get_additional_information(documents, coe_id)
        documents = runner.split(documents)  # 当前token应该不需要切分了
        if len(documents) == 0:
            logger.warn(
                f'[文本获取失败] coe_id={coe_id},type={type},doc_len={len(documents)}')
            raise Exception(f'[文本获取失败] doc_len={len(documents)}')

        logger.info(f'[2.预校验] coe_id={coe_id},type={type}')
        if not runner.pre_check():
            logger.info('[2.预校验] 不需要进行llm提问')
            runner.done()
            return coe_id, type, task_id, force
        logger.info(
            f'[3.总结链执行] coe_id={coe_id},type={type},doc_len={len(documents)}')
        existing_answer = runner.summary_and_thought(documents)  # COE总结

        logger.info(
            f'[4.分析结果] coe_id={coe_id},type={type}\nexisting_answer={existing_answer}')
        if type in post_xgpt_agent_dict:      # 所有Xgpt的Agent都走调用
            type_uuid = post_xgpt_agent_dict[type]
            result = post_new_open_session(type_uuid, 'wangyan229')
            sessionId = result.get("data", {}).get("sessionId")

            # -----根据类型追加对应的内容-----
            type_to_info_mapping = {
                'todo_analysis': ['todo_information'],
                # 'cause_analysis': ['cause_information'],
                'new_analysis': ['risk_assistant_information'],
                'monitor_online_analysis': ['time_information', 'fault_discovery_information'],
                'qa_test_analysis': ['qa_test_information'],
                'risk_assistant_analysis': ['risk_assistant_information']
            }

            for info_key in type_to_info_mapping.get(type, []):
                existing_answer += additional_information.get(info_key, '')
            if type == 'cause_analysis':
                existing_answer = documents[0].page_content

            xgpt_resp = post_open_chat(type_uuid, sessionId, "wangyan229", existing_answer)
            logger.info(f'xgpt分析返回={xgpt_resp},type={type}')

            answer = runner.deal_answer(existing_answer, xgpt_resp)
        else:
            answer = runner.analysis_and_answer(existing_answer)
        logger.info(
            f'[5.Done] 会同步回写COE维度数据 coe_id={coe_id},type={type}\nanswer={answer}')
        runner.done()
    except Exception as e:
        # 保存错误信息，is_done变为false
        logger.exception(e.args)
        result_item.error = str(e) + '\n' + traceback.format_exc(limit=1)
        result_item.is_done = False
        logger.info(result_item.to_json_dict())
        body = {
            "doc": result_item.to_json_dict()
        }
        es_util.update('coe_analysis_detail', id=_id, body=body)
    return runner


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


def run_chain(task_id, force=False, result_list: List[COEResult] = None):
    try:
        task, _id = search_task(task_id=task_id)
        task.state = '执行中'
        coe_es_writer.submit(update_task, task, _id)
    except Exception as e:
        logger.exception('[任务获取出现异常]' + str(e))
        return
    if result_list is None:
        result_list, _ = search_all_chain(task_id)
    done = {'data': 0}  # 线程安全
    total = len(task.choosed_coe_list)
    type_count = len(task.sub_task_type_list)
    done_count = {str(k.coe_id): 0 for k in task.choosed_coe_list}
    futures: List[Future] = []
    lion.fetch_config()
    excutor = ThreadPoolExecutor(max_workers=int(lion.config[lion.app_name + '.chain_thread_max_num']),
                                 thread_name_prefix='chain-thread')

    def call_back(worker: Future):
        if worker.exception():
            logger.exception("子任务执行异常: {}".format(worker.exception()))
            return
        try:
            runner = worker.result()
            coe_id = runner.result_item.coe_id
            # type = runner.type
            type = runner.result_item.type
            logger.info("called worker callback function, {},{}".format(coe_id, type))
            if (coe_id in done_count):
                done_count[coe_id] += 1
                if (done_count[coe_id] == type_count):
                    done['data'] += 1
            done_data = done['data']
            progress = f'{done_data}/{total}'
            task.progress = progress
            coe_es_writer.submit(update_task, task, _id)
        except Exception as e:
            logger.exception(
                f'[子任务 callback 异常] coeid={coe_id}, type={type} task_id={task_id}' + str(e))

    # for coe in task.choosed_coe_list:
    #     coe_id = coe.coe_id
    #     future = excutor.submit(sync_crawler_data, coe_id)
    #     futures.append(future)

    for item in result_list:
        type = item.type
        coe_id = item.coe_id
        if not is_type_regietered(type):
            logger.warn(f'{type} 没有注册')
            continue
        extral_args = task.extral_args
        if extral_args is None:
            extral_args = []
        future = excutor.submit(run_chain_once, coe_id, type, task_id, force, extral_args)
        future.add_done_callback(call_back)
        futures.append(future)
    try:
        wait(futures)
    except Exception as e:
        logger.exception(e.args)
    answers = []
    for f in futures:
        runner = f.result()
        answers.append(runner)
    time_stamp = time.time()
    now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.localtime(time_stamp))
    task.end_date = now
    task.state = '已完成'
    try:
        update_task(task, _id)
    except Exception as e:
        logger.exception("更新任务失败" + e.args)
    return answers


def run_chain_serial(coe_id_list, type_list, task_id, mis_id=None, name=None):
    lion.fetch_config()
    fresh_time = int(lion.config.get(f'{lion.app_name}.fresh_time', 1))
    try:
        result_list = bulk_create_result_info(coe_id_list, type_list, task_id)
    except Exception as e:
        logger.exception('[子任务创建失败]' + str(e))
    time.sleep(fresh_time)  # 写入需要 1s 进行刷盘
    run_chain(task_id, force=False, result_list=result_list)
    if mis_id:
        import os
        time.sleep(fresh_time * 3)  # 等待异步写入完成
        task_link = f'https://qa.sankuai.com/coe/detail/{task_id}/coe_result'
        if not os.getenv('Env', 'test') == 'prod':
            task_link += '#test'
        message = [f'您的[COE智能分析任务|{task_link}]完成']

        # 生成WIKI,短期方案：名称带wiki
        if "wiki" in name:
            title = name.rstrip("wiki")
            if 'cause_analysis' in type_list and 'debt_label' in type_list and 'todo_analysis' in type_list:
                _doc_link = make_wiki_for_report(task_id, title)
                message.append(f'报告链接: {_doc_link}')  # 添加报告链接并换行---生成到店业务平台研发部COE 列表（2025年X月）
            else:
                _doc_link = make_wiki_for_general(task_id, type_list, title)
                message.append(f'报告链接: {_doc_link}')  # 添加报告链接并换行
        else:
            result_dict, total, aggrs, cloud = chain_result_get(9000, 0, task_id)
            for tp, aggr in aggrs.items():
                for item in TASK_TYPES:
                    if item['type'] == tp:
                        tp = item['title']
                agg_str = []
                total = len(coe_id_list)
                for i in aggr:
                    key = i['name']
                    count = i['value']
                    rate = 0
                    if total != 0:
                        rate = count / total * 100
                    agg_str.append('{} 有 {:d}个({:.2f}%)'.format(key, count, rate))
                if isinstance(message, list):
                    message.append(tp + '：' + '，'.join(agg_str))
                    message = '\n'.join(message)
        send_dx_message_to_person(mis_id, message)


def get_additional_information(documents: list, coe_id: str):
    # 初始化信息字典
    additional_information = {
        "todo_information": '',
        "cause_information": '',
        "time_information": '',
        "qa_test_information": '',
        "fault_discovery_information": '',
        "risk_assistant_information": ''
    }
    for document in documents:
        desc = document.metadata.get('desc')
        category = document.metadata.get('category')
        page_content = document.page_content

        if desc in ['[正确做法]', '[经验教训]']:
            additional_information["todo_information"] += page_content
        elif desc == '[原因分析信息]':
            if category == '分析故障根因':
                additional_information["cause_information"] += page_content
            elif category == '分析测试流程':
                additional_information["qa_test_information"] += page_content
            elif category == '分析故障发现':
                additional_information["fault_discovery_information"] += page_content
        elif desc == '[时间线信息]':
            additional_information["time_information"] += page_content
    # 风险助手Agent需要APPKEY
    coe_info = getCoeJson('', coe_id)
    additional_information["risk_assistant_information"] = "appKey:" + str(coe_info['incident'].get('appkey', ''))

    return additional_information


def get_word_cloud(document: str):
    stop = open('./service/coe_analysis/cn_stopwords.txt')
    stopwords = stop.read().split('\n')
    keywords = jieba.lcut(document)
    counts = {}
    for i in keywords:
        if len(i) > 1:
            counts[i] = counts.get(i, 0) + 1
    for word in stopwords:
        counts.pop(word, 0)
    freq = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    return freq[:30]


def chain_result_get(size, from_, task_id):
    time0 = time.time()
    task, _task_id = search_task(task_id)
    result_list, total = search_all_chain(task_id, from_=from_, size=size)
    time1 = time.time()
    result_dict = {}
    coe_store_list, _ids = batch_search_coe_storage(
        [i.coe_id for i in result_list])
    coe_store_dict = {i.coe_id: i for i in coe_store_list}
    for item in result_list:
        if item.type not in task.sub_task_type_list:
            continue
        if item.coe_id in coe_store_dict:
            coe_store = coe_store_dict[item.coe_id].to_json_dict()
        else:
            coe_store = {}
        result_dict[item.coe_id] = {
            'coe_id': item.coe_id, 'brief': item.brief, 'coe_store': coe_store}
    aggrs = {item.type: {} for item in result_list}
    reason_all = []
    time2 = time.time()
    _, exp_dict = batch_find_experience([i.answer_message[0].exp_id for i in result_list if len(i.answer_message) > 0
                                         and i.answer_message[0].exp_id is not None])
    time3 = time.time()
    for item in result_list:
        if item.type not in task.sub_task_type_list:
            continue
        try:
            item_content = item.to_json_dict()
            if (not item.is_done or len(item.answer_message) == 0):
                result_to_show = item.error if item.error is not None else 'error'
                item_content['content'] = result_to_show
                result_dict[item.coe_id][item.type] = item_content
            else:
                first_saved_exp_id = item.answer_message[0].exp_id
                if first_saved_exp_id not in exp_dict and first_saved_exp_id is not None:
                    sub_time_0 = time.time()
                    exp_dict[first_saved_exp_id], _ = find_experience(
                        first_saved_exp_id)
                    sub_time_1 = time.time()
                    logger.info('\t由于没有找到exp_id所以执行find_experience,耗时 {}s'.format(
                        sub_time_1 - sub_time_0))
                result_to_show = get_result_to_show(
                    result_item=item, first_saved_exp=exp_dict.get(first_saved_exp_id))
                exp = exp_dict.get(first_saved_exp_id)
                if exp:
                    item_content['content'] = result_to_show
                    item_content['pre_checked_passed'] = exp.pre_checked_passed
                    result_dict[item.coe_id][item.type] = item_content
                else:
                    item_content['content'] = result_to_show
                    result_dict[item.coe_id][item.type] = item_content
            if (item.type == 'cause'):
                reason_all.append(item.reason)
            if (result_to_show):
                count = aggrs[item.type].get(result_to_show, 0)
                aggrs[item.type][result_to_show] = count + 1
        except Exception as e:
            logger.exception('没有找到结果' + e.args)
    aggrs = {k: [{"name": kk, "value": vv} for kk, vv in v.items()]
             for k, v in aggrs.items()}
    time4 = time.time()
    try:
        # word_cloud = get_word_cloud('\n'.join(reason_all))
        word_cloud = None
    except Exception as e:
        logger.error(e.args)
        word_cloud = None
    time5 = time.time()
    logger.info('search_all_chain耗时 {}s'.format(time1 - time0))
    logger.info('多次search_coe耗时 {}s'.format(time2 - time1))
    logger.info('batch_find_experience 耗时 {}s'.format(time3 - time2))
    logger.info('结果汇总耗时 {}s'.format(time4 - time3))
    logger.info('云图耗时 {}s'.format(time5 - time4))
    return result_dict, total, aggrs, word_cloud


def update_chain_result(chain: COEResult):
    index = 'coe_analysis_detail'
    query_josn = {
        "query": {"bool": {"must": [
            {"term": {"id": chain.id}},
        ]}}
    }
    answer = es_util.search(index=index, query=query_josn)
    _id = answer[0]['_id']
    body = {
        "doc": chain.to_json_dict()
    }
    es_util.client.update(index, id=_id, body=body, headers=es_util.headers)


def chain_result_save(item: Dict, change_log: ChangeLog):
    fresh_time = int(lion.config.get(f'{lion.app_name}.fresh_time', 1))
    _index = 'coe_analysis_detail'
    task_id = item['task_id'][0]
    coe_id = item['coe_id']
    type = item['type']
    result, _id = search_coe_result_item(
        task_id=task_id, coe_id=coe_id, type=type)

    if change_log.action == 'changeIndex':
        result.edit_time = get_now_str()
        new_answer_message = []
        for index in change_log.new_index_list:
            new_answer_message.append(result.answer_message[index])
        result.answer_message = new_answer_message
        if (result.change_log):
            result.change_log.append(change_log)
        else:
            result.change_log = [change_log]
        data = {
            "doc": result.to_json_dict()
        }
        es_util.update(_index, id=_id, body=data)
    elif change_log.action == 'contentChange':
        result.edit_time = get_now_str()
        index = change_log.exp_index
        exp, e_id = find_experience(result.answer_message[index].exp_id)
        index = change_log.msg_index
        if (index == 0):
            exp.search_text = change_log.new_message.content
            exp.search_embedding = embed.embed_query(exp.search_text)
        exp.data[index] = change_log.new_message
        save_experience_by_id(exp, e_id)
        if (result.change_log):
            result.change_log.append(change_log)
        else:
            result.change_log = [change_log]
        data = {
            "doc": result.to_json_dict()
        }
        es_util.update(_index, id=_id, body=data)
    elif change_log.action == 'reviewedTagChange':
        # 不更新修改时间
        result.is_reviewed = change_log.new_tag
        if (result.change_log):
            result.change_log.append(change_log)
        else:
            result.change_log = [change_log]
        data = {
            "doc": result.to_json_dict()
        }
        es_util.update(_index, id=_id, body=data)
        # experience_mark_update(exp_id, is_marked=change_log.new_tag, sleep=False)  # 有可能发生mark失败
    elif change_log.action == 'reasonableTagChange':
        result.is_reasonable = change_log.new_tag
        if (result.change_log):
            result.change_log.append(change_log)
        else:
            result.change_log = [change_log]
        data = {
            "doc": result.to_json_dict()
        }
        es_util.update(_index, id=_id, body=data)
    es_util.refresh(_index)
    time.sleep(fresh_time)


#   新建智能体会话获取sessionId

def post_new_open_session(uuid, operator):
    """
    创建智能体会话，创建后，使用会话id与智能体进行具体对话
    :param uuid: 智能体唯一标识
    :param operator: 操作者
    :return: 响应结果
    """
    # 构造 URL
    url = f"{XGPT_URL}/openApi/rpa/newOpenSession?subAgentId={uuid}"

    # 请求头
    headers = {
        "Token": f"{XGPT_TOKEN}",  # key一定为 Token
        "User-Agent": "PythonClient/1.0",  # 设置 User-Agent
        "Content-Type": "application/json"  # 指定请求体为 JSON 格式
    }
    # 请求体
    payload = {
        "subAgentId": uuid,
        "operator": operator,
        "name": "新建智能体会话获取sessionId"
    }
    try:
        # 发送 POST 请求
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()  # 检查请求是否成功
        return response.json()  # 返回 JSON 响应
    except requests.exceptions.RequestException as e:
        print(f"请求失败: {e}")
        return None


#   智能体对话
def post_open_chat(uuid, sessionId, operator, content):
    """
    与智能体对话并获得智能体响应
    :param uuid: 智能体唯一标识
    :param sessionId: 会话 ID
    :param operator: 操作者
    :param multiCount: 多次计数
    :param stream: 流标识默认是True
    :param message: 消息内容
    :return: 响应结果
    """
    url = f"{XGPT_URL}/openApi/rpa/openChat?subAgentId={uuid}"
    headers = {
        "Token": f"{XGPT_TOKEN}",  # 使用 Bearer 格式的 Token
        "User-Agent": "PythonClient/1.0",  # 设置 User-Agent
        "Content-Type": "application/json"  # 指定请求体为 JSON 格式
    }
    # 组装对话输入
    message = {
        "role": "user",
        "content": content
    }
    payload = {
        "subAgentId": uuid,
        "sessionId": sessionId,
        "operator": operator,
        "multiCount": 0,
        "stream": False,
        "message": message
    }
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()  # 检查请求是否成功
        return response.json()  # 返回 JSON 响应
    except requests.exceptions.RequestException as e:
        print(f"请求失败: {e}")
        return None


def test():
    fresh_time = int(lion.config.get(f'{lion.app_name}.fresh_time', 1))
    create_result_info('164183', 'cause', '123')
    time.sleep(fresh_time)  # 写入需要 1s 进行刷盘
    run_chain_once('164183', 'cause', '123')


if __name__ == '__main__':
    index = 'coe_analysis_task'
    query = {
        "query": {"bool": {"must": [{"match_all": {}}], }},
        "from": 0,
        "size": 1000,
    }
    answer = es_util.search(query=query, index=index)
    for ans in answer:
        source = ans['_source']
        _id = ans['_id']
        task = COEAnalysisTask.from_json(source)
        task_id = source['id']
        result_list, total = search_all_chain(task_id)
        coe_list = []
        coe_id_set = set()
        type_set = set()
        for chain in result_list:
            type_set.add(chain.type)
            if (chain.coe_id not in coe_id_set):
                coe_id_set.add(chain.coe_id)
                coe_list.append(BaseCoeData(coe_id=chain.coe_id,
                                            brief=chain.brief, level=chain.level))
        task.choosed_coe_list = coe_list
        task.sub_task_type_list = list(type_set)
        if (total == 0):
            task.is_active = False
        update_task(task, _id)
