from typing import List, Tuple
from service.coe_analysis.coe_experience_service import create_experience, get_experience
from service.coe_analysis.coe_store_service import batch_search_coe_storage, batch_sync_coe_storage, sync_coe_result
from service.coe_analysis.coe_task_service import create_task, create_task_by_base_coe_data
from service.coe_analysis.config_reader import OPENAI_API_BASE, OPENAI_API_KEY
from service.coe_analysis.crawler.getDoc import getLatestId
from service.coe_analysis.crawler_data_service import sync_crawler_data, delete_passed, find_crawler_data
from service.coe_analysis.runners import get_runner_by_type
from service.coe_analysis.runners.tonotto import COE6to2notRunner
from service.file_config_reader import read_lion_file_config
from utils import logger, read_json, write_json, write_io
import logging
from service.coe_analysis.data_structure import Answer, BaseCoeData, COEAnalysisTask, COEResult, COEStoreageData, Experience, MetaMessage, Tag
import re
import time
from concurrent.futures import ThreadPoolExecutor, Future, wait
from sklearn.metrics import roc_auc_score
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, AIMessage
import service.coe_analysis.coe_chain_service as chain_service
from service.coe_analysis.llm_sdk_importer import (COE_ANALYSIS_DETAIL, COE_ANALYSIS_EXPERIENCE,  # noqa
                                                   COE_ANALYSIS_TASK, COE_SYNC_DATA)  # noqa
from llmcore_sdk.data_connection.es_client import LLMElasticsearchClient
import configparser
import os


ES_ENV = os.getenv('ES_ENV', 'default')
config = read_lion_file_config('es_client.conf')


def get_es_client(env):
    accesskey = config[env]['accesskey']
    appkey = config[env]['appkey']
    is_online_env = config[env]['isOnlineEnv'] == 'true'
    es_util = LLMElasticsearchClient(
        accesskey=accesskey, appkey=appkey, is_online_env=is_online_env)
    return es_util


es_prod_client = get_es_client('deploy')
es_test_client = get_es_client('default')


def search_task(task_id, client: LLMElasticsearchClient):
    index = 'coe_analysis_task'
    query = {"query": {"bool": {"must": [{"term": {"id": task_id}}]}}}
    answer = client.search(index=index, query=query)
    task = COEAnalysisTask.from_es(answer[0])
    return task, answer[0]['_id']


def search_coe(coe_id, es_util:LLMElasticsearchClient) -> Tuple[COEStoreageData, str]:
    try:
        query_josn = {
            "_source": {"excludes": ['brief_embedding', 'cause_embedding',
                                     'content_embedding', 'experience_embedding']},
            "query": {"bool": {"must": [
                {"match": {"coe_id": coe_id}},
            ]}}
        }
        answer = es_util.search(index=COE_SYNC_DATA, query=query_josn)
        item = COEStoreageData.from_es(answer[0])
        _id = answer[0]['_id']
        return item, _id
    except Exception:
        return None, None


def diff_prod_with_test(prod_task_id, test_task_id):
    prod_task, _id = search_task(task_id=prod_task_id, client=es_prod_client)
    test_task, _id = search_task(task_id=test_task_id, client=es_test_client)
    prod_coe_ids = set([i.coe_id for i in prod_task.choosed_coe_list])
    test_coe_ids = set([i.coe_id for i in test_task.choosed_coe_list])
    coe_ids = list(prod_coe_ids.intersection(test_coe_ids))
    types = ["to_test", "to_claim", "to_check", "to_grey",
             "to_inspect", "to_rollback", "not_to_delay",
             "not_to_illagle_change_data"]
    print(len(coe_ids))
    diff_coes = set()
    for coe_id in coe_ids:
        prod_coe, _ = search_coe(coe_id, es_util=es_prod_client)
        test_coe, _ = search_coe(coe_id, es_util=es_test_client)
        for type in types:
            brief = prod_coe.brief
            prod_tag: Tag = prod_coe.__getattribute__(type)
            test_tag: Tag = test_coe.__getattribute__(type)
            if prod_tag.analysis_result_raw != test_tag.analysis_result_raw:
                print(f'''{brief}(链接https://coe.mws.sankuai.com/detail/{coe_id}) 的 {type} 存在差异
prod-{prod_tag.analysis_result_raw}][链接为https://qa.sankuai.com/coe/result_tab/task_id/{prod_tag.analysis_task_id[0]}/coe_id={coe_id}&type={type}
test-{test_tag.analysis_result_raw}][链接为https://qa.sankuai.com/coe/result_tab/task_id/{test_tag.analysis_task_id[0]}/coe_id={coe_id}&type={type}#test
结束''')
            diff_coes.add(coe_id)
    print('COE维度不一致率: {}/{}={:.4f}'.format(len(diff_coes), len(coe_ids), len(diff_coes)/len(coe_ids)))


def calculate_rate(task_id, es_util):
    task, _id = search_task(task_id=task_id, client=es_util)
    coe_ids = [i.coe_id for i in task.choosed_coe_list]
    types = ["to_test", "to_claim", "to_check", "to_grey",
             "to_inspect", "to_rollback", "not_to_delay",
             "not_to_illagle_change_data"]
    for type in types:
        ratio = {}
        total = len(coe_ids)
        for coe_id in coe_ids:
            coe, _ = search_coe(coe_id, es_util=es_util)
            tag: Tag = coe.__getattribute__(type)
            # if tag.analysis_result_raw in ['无法确定', '无法判断']:
            r = ratio.get(tag.analysis_result_raw, 0)
            r += 1
            ratio[tag.analysis_result_raw] = r
        for lb, cnt in ratio.items():
            print('[{}]-[{}]:{}/{}={:.4f}%'.format(type, lb, cnt, total, cnt/total*100))


def main(coe_ids, task_name, types):
    coe_list, _ = batch_search_coe_storage(coe_ids=coe_ids)
    coe_list = [BaseCoeData(
        coe_id=i.coe_id, brief=i.brief, level=i.level
    ) for i in coe_list]
    # task_id = create_task_by_base_coe_data(coe_list=coe_list, name=task_name, source='测试触发',
    #                                        type_list=types, submitter='auto', to_submit_task=False)
    task_id = '267380893275846069214437182293653066018'
    coe_id_list = [i.coe_id for i in coe_list]
    logger.info(f'任务 {task_name} 创建完成 = {task_id}')
    chain_service.run_chain_serial(coe_id_list, types, task_id)


if __name__ == '__main__':
    coe_ids = ['271616', '274108', '273030', '272638', '273744', '273086', '273863', '273058']
    # coe_ids = ['273744', '273086', '273863', '273058']
    types = ['to_claim']
    main(coe_ids, '六要两不要图片任务', types)
    # calculate_rate('106792110787954586783442319728139309346', es_util=es_test_client)

    # diff_prod_with_test(prod_task_id='9633917094104047104584363958045673441',
    #                     test_task_id='106792110787954586783442319728139309346')
