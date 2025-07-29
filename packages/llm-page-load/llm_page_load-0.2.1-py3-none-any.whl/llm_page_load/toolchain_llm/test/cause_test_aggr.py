from typing import Dict, List
import uuid
from sklearn import preprocessing
from service.coe_analysis.aggr_task_service import aggr_run_chain_serial, aggr_task_create
from service.coe_analysis.coe_chain_service import \
    bulk_create_result_info, search_task, update_chain_result, update_task
from service.coe_analysis.coe_experience_service import batch_find_experience, experience_mark_update, find_experience
from service.coe_analysis.coe_store_service import _get_result_, list_coe, search_coe, sync_coe_result, sync_once
from service.coe_analysis.coe_task_service import create_task
from service.coe_analysis.config_reader import OPENAI_API_BASE, OPENAI_API_KEY
from service.coe_analysis.crawler.getDoc import getLatestId
from service.coe_analysis.crawler_data_service import sync_crawler_data, delete_passed, find_crawler_data
from service.coe_analysis.runners import get_runner_by_type
from service.coe_analysis.runners.coe_cause_search import CauseTreeSearchRunner
from service.coe_analysis.search_coe_result_item import batch_search_chain_by_id, search_all_chain, search_coe_result_item
from utils import GPT35NAME, get_now_str, logger, read_json, write_json, write_io
from service.coe_analysis.llm_sdk_importer import es_util
from service.coe_analysis.data_structure import BaseCoeData, COEAnalysisTask, COEResult, Experience
import re
from service.lang_chain_utils.embedding import embed
import time
import jieba
from concurrent.futures import ThreadPoolExecutor, Future, wait
from sklearn.metrics import roc_auc_score, pairwise_distances
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, AIMessage
from token_count.tokenizer import count_token
import sklearn.cluster
import numpy as np
from tqdm import tqdm


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
            logger.exception(f'同步 {chain.coe_id} 失败' + e.args)
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
    task_id = '241819513759714651790002378773920485666'
    coe_id_list = [(d['coe_id'], d) for d in data if d['coe_id']]

    features: List[Future] = []
    coe_id_list = [('246815', {}), ('245499', {})]
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


def key_words_aggr_prepare():
    cause = '代码逻辑'
    create_begin = '2023-05-01'
    create_end = '2023-07-30'
    size = 1000
    coe_list, _ = list_coe(create_begin, create_end, size, 0,
                           is_exclude_light_template=True,
                           other_must_inner=[{"term": {"cause_analysis.analysis_result.keyword": cause}}])
    chain_ids = []
    for i in coe_list:
        if i.cause_analysis and i.cause_analysis.analysis_result_id:
            chain_ids.append(i.cause_analysis.analysis_result_id)
    chains, _ = batch_search_chain_by_id(chain_id_list=chain_ids)
    data = []
    excludes = ['问题', '逻辑', '错误']
    for chain in tqdm(chains):
        first_saved_exp_id = chain.answer_message[0].exp_id
        exp, _ = find_experience(first_saved_exp_id)
        text = exp.data[-1].content
        pattern = r"关键词[:：]\s*(.+)"
        result = re.search(pattern, text)
        category = result.group(1)
        category = re.split(r',\s*|，\s*|、\s*', category)
        for key in category:
            key_exclude = key
            for ex in excludes:
                key_exclude = key_exclude.replace(ex, '')
            data.append({
                'keyword': key_exclude,
                'embedding': embed.get_embedding(key_exclude),
                'chain_id': chain.id
            })
    write_json('test/data/cause_aggr_keywords.json', data=data)


class SetList:
    def __init__(self):
        self.data = set()

    def add(self, d):
        self.data.add(d)

    def __dict__(self):
        return list(self.data)


def key_words_aggr():
    cause_aggr_keywords = read_json('test/data/cause_aggr_keywords.json')
    chain_ids = list(set([d['chain_id'] for d in cause_aggr_keywords]))
    chains, _ = batch_search_chain_by_id(chain_id_list=chain_ids)
    chain_dict = {chain.id: chain for chain in chains}
    data = np.array([d['embedding'] for d in cause_aggr_keywords])
    data = preprocessing.normalize(data)
    # dis = pairwise_distances(data)
    # dis_l = []
    # for i in range(data.shape[0]):
    #     for j in range(i+1,data.shape[0]):
    #         dis_l.append(dis[i][j])
    # dis_l = np.array(dis_l)
    # import matplotlib.pyplot as plt
    # plt.hist(dis_l)
    # plt.show()
    # cluster = sklearn.cluster.KMeans(n_clusters=50, init='k-means++')
    cluster = sklearn.cluster.AgglomerativeClustering(n_clusters=75, compute_distances=True)
    result = cluster.fit_predict(data)
    clusted_coe_dict: Dict[str, List] = {}
    clusted_preview: Dict[str, Dict] = {}
    for d, cluster in zip(cause_aggr_keywords, result):
        c = str(cluster)
        if c not in clusted_coe_dict:
            clusted_coe_dict[c] = []
            clusted_preview[c] = {}
            clusted_preview[c]['ls'] = []
            clusted_preview[c]['chains'] = SetList()
            clusted_preview[c]['brief'] = SetList()
        chain_id = d['chain_id']
        chain = chain_dict[chain_id]
        clusted_preview[c]['chains'].add(chain_id)
        clusted_preview[c]['brief'].add(chain.brief)
        clusted_coe_dict[c].append(d)
        clusted_preview[c]['ls'].append(d['keyword'])
    write_json('test/data/clusted_preview.json', data=clusted_preview)
    model_name = GPT35NAME
    llm = ChatOpenAI(model_name=model_name,
                     openai_api_base=OPENAI_API_BASE,
                     openai_api_key=OPENAI_API_KEY,
                     request_timeout=60,
                     max_retries=6)
    for c, ls in tqdm(clusted_preview.items()):
        txt = '\n'.join(ls['ls'])
        # print(f'''请从这些关键词里面提取出公共的关键词:\n{txt}''')
        ans = llm.predict(f'''请问以下这些关键词共同体现了什么样的问题:\n{txt}\n\n请用以下格式进行作答:\n共同问题概括:\n具体描述:''')
        clusted_preview[c]['ans'] = ans
        # print(ans)
    write_json('test/data/clusted_preview.json', data=clusted_preview)


def key_words_aggr_step2():
    clusted_preview = read_json('test/data/clusted_preview.json')
    pattern = r'共同问题概括[:：]\s*(.+)'
    ans = []
    for c, data in clusted_preview.items():
        r = re.findall(pattern, data['ans'])
        if len(r) > 0:
            ans.append(r[0].split('\n')[0])
    # for c, data in clusted_preview.items():
        # ans.extend(data['ls'])
    model_name = GPT35NAME
    # model_name = 'gpt-4'
    llm = ChatOpenAI(model_name=model_name,
                     openai_api_base=OPENAI_API_BASE,
                     openai_api_key=OPENAI_API_KEY,
                     request_timeout=120,
                     max_retries=6)
    text = '\n'.join(ans)
    # ask = f'''在处理的过程中，业务人员发现以下问题:\n {text}\n\n请对其进行去重后再列举出来'''
    # print("Human: "+ask)
    # a = llm.predict(ask)
    # print("AI: "+a)
    a = text
    ask = f'''在处理的过程中，业务人员发现以下问题:\n {a}\n\n请将其归纳为10个共性问题，按照以下格式输出: 1.xxx问题: 包括了xxx,xxx,xxx,xxx'''
    print("Human: "+ask)
    b = llm.predict(ask)
    print("AI: "+b)


def key_words_aggr_step3():
    keys = []
    prev_ans = '''1. 数据处理问题: 包括了订单状态和数据状态的不兼容和不一致问题、数据查询与展示问题、数据生成和团单草稿的问题、数据解析问题、数据重复问题。
2. 并发控制和线程管理问题: 包括了并发控制和线程管理问题、并发创建商品和并发创建闲置房产品的问题、问题涉及到多线程环境下的资源共享和线程上下文的传递。
3. 接口使用和参数传递问题: 包括了接口参数传递问题、后端接口返回空数组数据或空参数、参数传递和接口使用方面的问题、参数拼接和编码问题。
4. 前端处理问题: 包括了前端处理问题导致交易前端代码无法正常请求接口参数信息、页面调用和事件触发问题、网页加载和浏览过程中的效率和用户体验问题。
5. 资金管理问题: 包括了资金分配和管理问题、促销和优惠方面的问题、与金额处理和结算方式相关的问题、金额计算和转换的准确性问题。
6. 业务逻辑问题: 包括了电销判断和判断当前用户是否可下钻的关键词都涉及到判断和决策的过程、商品标识和履约发货的问题、门票出票与处理失败引发的消费问题、存在多个组件的bug和系统的bug。
7. 系统状态和管理问题: 包括了缓存相关的问题、关于系统状态和序列码的问题、系统购物车和代理接口调用的问题、APP崩溃。
8. 基础设施问题: 包括了网络连接问题或服务器故障、存在域名相关问题、缺乏有效的数据保护措施、兼容性问题、内存管理问题。
9. 时间管理和任务安排问题: 包括了时间管理和任务安排、时间相关问题、时间范围的界定问题、经济增长中的不平衡和不可持续性。
10. 组件和模块管理问题: 包括了混淆了app和pc业务导致代码复用困难、关于组件的使用和管理存在一些问题、字段管理和操作相关问题、缺乏城市id导致无法获取相关信息、转义模型的选择信息存在问题。'''
    for line in prev_ans.splitlines():
        pattern = r'包括了(.*)'
        line = re.findall(pattern, line)[0]
        key = re.split(r',\s*|，\s*|、\s*', line)
        keys.extend(key)
    print(keys)
    print(len(keys))

    model_name = GPT35NAME
    # model_name = 'gpt-4'
    llm = ChatOpenAI(model_name=model_name,
                     openai_api_base=OPENAI_API_BASE,
                     openai_api_key=OPENAI_API_KEY,
                     request_timeout=120,
                     max_retries=6)

    create_begin = '2023-05-01'
    create_end = '2023-07-30'
    size = 30
    cause = '代码逻辑'
    cause_aggr_step3: Dict = {}
    for ind, key in tqdm(enumerate(keys)):
        coe_list, _ = list_coe(create_begin, create_end, size, 0,
                               is_exclude_light_template=True, cause_search=key,
                               other_must_inner=[{"term": {"cause_analysis.analysis_result.keyword": cause}}])
        chain_ids = []
        for i in coe_list:
            if i.cause_analysis and i.cause_analysis.analysis_result_id:
                chain_ids.append(i.cause_analysis.analysis_result_id)
        chains, _ = batch_search_chain_by_id(chain_id_list=chain_ids)
        text = []
        for chain in chains:
            first_saved_exp_id = chain.answer_message[0].exp_id
            exp, _ = find_experience(first_saved_exp_id)
            t = exp.data[-1].content
            brief = chain.brief
            ans = re.findall(r'分类思路和原因[:：]\s*(.*)', t)[0]
            ans = ans.split('\n')[0]
            ans = re.split(r',\s*|，\s*|、\s*|。\s*', ans)
            ans = '，'.join([a for a in ans if '代码逻辑' not in a and '逻辑错误' not in a and a != '因此' and len(a) != 0])
            txt = f'{ind}. [{brief}]\n - {ans}'
            text.append(txt)
        text = '\n\n'.join(text)
        prompt = f'请逐一判断以下线上问题是否属于"{key}":\n{text}\n\n\n请你逐条进行分析，按照以下格式输出:\n - 序号:\n - 标题:\n - 判断:是或者否\n - 理由:'
        print(prompt)
        ans = llm.predict(prompt)
        print(ans)
        aa = ans.split('\n\n')
        bb = []
        for a in aa:
            try:
                f = re.findall(r'判断[:：]\s*(.*)\n', a)[0]
                if '否' not in f:
                    bb.append(a)
            except Exception:
                pass
        cause_aggr_step3[key] = ans
        print(f'{key}: {bb}')
    write_json('test/data/cause_aggr_step3.json', cause_aggr_step3)


def key_words_aggr_m3e_step3():
    keys = []
    prev_ans = '''1. 数据处理问题: 包括了订单状态和数据状态的不兼容和不一致问题、数据查询与展示问题、数据生成和团单草稿的问题、数据解析问题、数据重复问题。
2. 并发控制和线程管理问题: 包括了并发控制和线程管理问题、并发创建商品和并发创建闲置房产品的问题、问题涉及到多线程环境下的资源共享和线程上下文的传递。
3. 接口使用和参数传递问题: 包括了接口参数传递问题、后端接口返回空数组数据或空参数、参数传递和接口使用方面的问题、参数拼接和编码问题。
4. 前端处理问题: 包括了前端处理问题导致交易前端代码无法正常请求接口参数信息、页面调用和事件触发问题、网页加载和浏览过程中的效率和用户体验问题。
5. 资金管理问题: 包括了资金分配和管理问题、促销和优惠方面的问题、与金额处理和结算方式相关的问题、金额计算和转换的准确性问题。
6. 业务逻辑问题: 包括了电销判断和判断当前用户是否可下钻的关键词都涉及到判断和决策的过程、商品标识和履约发货的问题、门票出票与处理失败引发的消费问题、存在多个组件的bug和系统的bug。
7. 系统状态和管理问题: 包括了缓存相关的问题、关于系统状态和序列码的问题、系统购物车和代理接口调用的问题、APP崩溃。
8. 基础设施问题: 包括了网络连接问题或服务器故障、存在域名相关问题、缺乏有效的数据保护措施、兼容性问题、内存管理问题。
9. 时间管理和任务安排问题: 包括了时间管理和任务安排、时间相关问题、时间范围的界定问题、经济增长中的不平衡和不可持续性。
10. 组件和模块管理问题: 包括了混淆了app和pc业务导致代码复用困难、关于组件的使用和管理存在一些问题、字段管理和操作相关问题、缺乏城市id导致无法获取相关信息、转义模型的选择信息存在问题。'''
    for line in prev_ans.splitlines():
        pattern = r'包括了(.*)'
        line = re.findall(pattern, line)[0]
        key = re.split(r',\s*|，\s*|、\s*', line)
        keys.extend(key)
    print(keys)
    print(len(keys))

    model_name = GPT35NAME
    # model_name = 'gpt-4'
    llm = ChatOpenAI(model_name=model_name,
                     openai_api_base=OPENAI_API_BASE,
                     openai_api_key=OPENAI_API_KEY,
                     request_timeout=120,
                     max_retries=6)

    create_begin = '2023-05-01'
    create_end = '2023-07-30'
    size = 1000
    cause = '代码逻辑'
    coe_list, _ = list_coe(create_begin, create_end, size, 0,
                           is_exclude_light_template=True,
                           other_must_inner=[{"term": {"cause_analysis.analysis_result.keyword": cause}}])

    cause_aggr_step3: Dict = {}
    for ind, key in tqdm(enumerate(keys)):
        chain_ids = []
        for i in coe_list:
            if i.cause_analysis and i.cause_analysis.analysis_result_id:
                chain_ids.append(i.cause_analysis.analysis_result_id)
        chains, _ = batch_search_chain_by_id(chain_id_list=chain_ids)
        text = []
        for chain in chains:
            first_saved_exp_id = chain.answer_message[0].exp_id
            exp, _ = find_experience(first_saved_exp_id)
            t = exp.data[-1].content
            brief = chain.brief
            ans = re.findall(r'分类思路和原因[:：]\s*(.*)', t)[0]
            ans = ans.split('\n')[0]
            ans = re.split(r',\s*|，\s*|、\s*|。\s*', ans)
            ans = '，'.join([a for a in ans if '代码逻辑' not in a and '逻辑错误' not in a and a != '因此' and len(a) != 0])
            txt = f'{ind}. [{brief}]\n - {ans}'
            text.append(txt)
        text = '\n\n'.join(text)
        prompt = f'请逐一判断以下线上问题是否属于"{key}":\n{text}\n\n\n请你逐条进行分析，按照以下格式输出:\n - 序号:\n - 标题:\n - 判断:是或者否\n - 理由:'
        print(prompt)
        ans = llm.predict(prompt)
        print(ans)
        aa = ans.split('\n\n')
        bb = []
        for a in aa:
            try:
                f = re.findall(r'判断[:：]\s*(.*)\n', a)[0]
                if '否' not in f:
                    bb.append(a)
            except Exception:
                pass
        cause_aggr_step3[key] = ans
        print(f'{key}: {bb}')
    write_json('test/data/cause_aggr_step3.json', cause_aggr_step3)


def aggr_test():
    task_id = aggr_task_create(
        name='聚合分析-代码逻辑', submitter='lyl', source='测试触发', cause='代码逻辑', k=6, create_begin='2023-05-01',
        create_end='2023-07-30', type='aggr_by_second_classify', to_submit_task=True)
    print(task_id)

    # task_id = aggr_task_create_from_task(name='聚合分析-代码逻辑-from-task-Hierarchical', submitter='lyl', source='测试触发',
    #                                      type='aggr_by_second_classify_from_task',
    #                                      from_task_id='203427561608963338040830040347234013474', cause='代码逻辑', k=7)
    # print(task_id)

    # task_id = aggr_tree_task_create(name='聚合分析-代码逻辑', submitter='lyl', source='测试触发', cause='代码逻辑',
    #                                 k=6, create_begin='2023-07-01', create_end='2023-07-30',
    #                                 type='aggr_by_aianswer_to_tree')
    # print(task_id)


def main_aggr(name):
    time_stamp = time.time()
    now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.localtime(time_stamp))
    id = str(uuid.uuid1().int)
    index = 'coe_analysis_task'
    # 创建主任务 document
    task = COEAnalysisTask(
        id=id, start_date=now, name=name, submitter='auto', source='手动触发', state='执行中',
        progress="-/-", choosed_coe_list=[], sub_task_type_list=['aggr_simple'], is_active=True)
    es_util.index(index=index, body=task.to_json_dict(), id=id)
    es_util.refresh(index)
    aggr_run_chain_serial('2023-07-01', '2023-12-31', type='aggr_simple', task_id=task.id, cause='配置问题', k=20)
    return id


def make_io(task_id: str):
    search_runner = CauseTreeSearchRunner(task_id=task_id)
    items, result_item, rootList = search_runner.tree_search()
    data = []
    for item in items:
        data.append({
            'brief': item['brief'],
            'link': 'https://coe.mws.sankuai.com/detail/' + item['coe_id'],
            '二级分类': item['parent_list'][-2],
            '三级分类': item['parent_list'][-3],
            '描述': item['text'],
            '得分': item['score']
        })
    write_io(f'test/data/{task_id}.treesearch.xlsx', data)


if __name__ == '__main__':
    # main_aggr('2023H2配置问题下钻（RD自填分类）')
    make_io('243357652976599931549218315775233757474')

    # del_exp_5month()
    # aggr_test()
    # key_words_aggr_prepare()
    # key_words_aggr()
    # key_words_aggr_step2()

    # word2vec_prepare()
    # word2vec_aggr()

    # get_6month_data()
    # main()
    # calcluate_acc('241819513759714651790002378773920485666', data=read_json('test/data/baseline_cause_6month.json'))
