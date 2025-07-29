from typing import List
from service.coe_analysis.coe_store_service import batch_sync_coe_storage, sync_once, batch_search_coe_storage, search_coe  # noqa
from service.coe_analysis.crawler.getDoc import getLatestId
from service.coe_analysis.coe_task_service import create_task_by_base_coe_data, run_chain_serial
from tools.dx import send_dx_message, send_dx_message_to_person
from utils import logger
from service.coe_analysis.data_structure import BaseCoeData, COEStoreageData, Tag
from service.lang_chain_utils.lion_client import client as lion
from llmcore_sdk.utils.wiki_utils import WikiDocument, wiki_maker
import datetime
import json
import os
import numpy as np

from service.coe_analysis.llm_sdk_importer import es_util
Env = os.getenv('Env', 'test')


__N = {
    "to_test": ["要测试"],
    "to_claim": ["要周知"],
    "to_check": ["要审核"],
    "to_grey": ["要灰度"],
    "to_inspect": ["要观测"],
    "to_rollback": ["要可回滚"],
    "not_to_delay": ["不要延报故障", "不要瞒报故障"],
    "not_to_illagle_change_data": ["不要违规变更数据"],
}


def send_message(message, person_only=False, precheck=False):
    pass
#     user_ids = json.loads(lion.config[f'{lion.app_name}.coe.tonotto.dx_user'])
#     groups = json.loads(lion.config[f'{lion.app_name}.coe.tonotto.dx_group'])
#     if precheck or Env == 'test':
#         user_ids = ['liyilun02']
#         groups = []
#     for user_id in user_ids:
#         # send_dx_message_to_person(user_id, message)
#     if not person_only:
#         for group in groups:
#             send_dx_message(group, message)


def make_wiki(coe_ids: str, task_name: str, types: list, raw_len: int, light_len: int, task_id):
    related_coe: List[COEStoreageData] = []
    phase_dict = {}
    for coe_id in coe_ids:
        try:
            coe, _id = search_coe(coe_id)
            is_related = False
            phase = []
            for type in types:
                flg = False
                tag: Tag = coe.__getattribute__(type)
                if tag.rd_result in ["违反", "无法确定", "涉及"]:
                    flg = True
                if tag.analysis_result in ["违反", "无法确定", "涉及"]:
                    flg = True
                if tag.analysis_result_raw in ["违反", "无法确定", "涉及"]:
                    flg = True
                if flg:
                    is_related = True
                    phase.append(type)
            if is_related:
                related_coe.append(coe)
                phase_dict[coe.coe_id] = phase
        except Exception as e:
            logger.info(f'没有拉取到 COE {coe_id}, {str(e)}')
    doc = WikiDocument.make_root_doc()
    doc.append_title(title=task_name)
    doc.append_paragraph(text=f'{task_name} 共计 {raw_len} 条 coe, 排除轻量模板 {light_len} 条, 共计 {len(coe_ids)} 条参与智能初筛，智能初筛后 {len(related_coe)} 个 coe 进入人工初筛（QA X2主R）')  # noqa
    p = doc.append_paragraph(text='详情可查看：')
    p.append_link(href='https://qa.sankuai.com/coe/coestorage', text='https://qa.sankuai.com/coe/coestorage')
    tb = doc.append_table()
    hed = tb.append_table_row()
    hed.append_table_item('table_header', text=' ', colwidth=[50])
    hed.append_table_item('table_header', text='COE链接', colwidth=[350])
    hed.append_table_item('table_header', text='可能违规项', colwidth=[350])
    for coe in related_coe:
        row = tb.append_table_row()
        row.append_table_item(type='table_cell', numCell=True, text=' ', colwidth=[50])
        item = row.append_table_item(type='table_cell', colwidth=[350])
        pg = item.append_paragraph()
        pg.append_link(href=f'https://coe.mws.sankuai.com/detail/{coe.coe_id}', text=coe.brief)
        if coe.level:
            pg.append_text(text=f'-{coe.level}')
        if coe.coe_template_name:
            pg.append_text(text=f'-{coe.coe_template_name}')
        item = row.append_table_item(type='table_cell', colwidth=[350])
        pg = item.append_paragraph()
        for ph in phase_dict[coe.coe_id]:
            pg.append_link(text=__N[ph][0], href=f'https://qa.sankuai.com/coe/result_tab/task_id/{task_id}?coe_id={coe.coe_id}&type={ph}')  # noqa
    parentId = lion.config[f'{lion.app_name}.coe.tonotto.parentId']
    res = wiki_maker(content=doc.to_json_dict(), title=task_name, parentId=parentId)
    response = res.json()
    logger.info(response)
    _id = None
    if response['status'] == 200:
        _id = response['data']
        lnk = f'https://km.sankuai.com/collabpage/{_id}'
        logger.info(f"报告链接: {lnk}")
        return lnk
    raise Exception('没有完成报告')


def tnt_task_inner(coe_ids: List[str], task_name: str, types: List[str], precheck=False):
    for coe_id in coe_ids:
        sync_once(coe_id=coe_id)
    if len(coe_ids) == 0:
        logger.info('本月没有线上问题')
        send_message(f'{task_name} ： 没有发现有效 COE', precheck=precheck)
        return
    coe_list, _ = batch_search_coe_storage(coe_ids=coe_ids)
    coe_list = [BaseCoeData(
        coe_id=i.coe_id, brief=i.brief, level=i.level
    ) for i in coe_list]
    task_id = create_task_by_base_coe_data(coe_list=coe_list, name=task_name, source='循环触发',
                                           type_list=types, submitter='auto', to_submit_task=False)
    # send_message(f'[{task_name}|https://qa.sankuai.com/coe/detail/{task_id}/coe_result] 任务创建完成，LLM 开始进行六要两不要分析',
    #              precheck=precheck)
    coe_id_list = [i.coe_id for i in coe_list]
    # logger.info(f'循环任务 {task_name} 创建完成 = {task_id}')
    run_chain_serial(coe_id_list, types, task_id)
    # logger.info(f'循环任务 {task_name} 执行完成 = {task_id}')
    batch_sync_coe_storage(coe_id_list=coe_ids)
    return task_id


def get_coeids(type):
    lion.fetch_config()
    query_json ={
                "query": {
                    "bool": {
                    "must": [
                        # {
                        # "terms": {
                        #     f"{type}.analysis_result_raw.keyword": [
                        #     "没违反" ,
                        #     "无法确定",
                        #     "违反"
                        #     ]
                        # }
                        # },
                        {
                        "range": {
                            "create_at.keyword": {
                            "gte": "2024-02-01T12:48:33Z",
                            "lte": "2024-08-06T12:48:33Z"
                            }
                        }
                        }
                    ],
                    "must_not": [],
                    "should": [],
                    "filter": []
                    }
                },
                "size": "1000",
                "sort": [
                    {
                    "create_at.keyword": {
                        "order": "desc"
                    }
                    }
                ]
            }
    answer = es_util.search(index='coe_sync_data', query=query_json)
    coe_ids = [item['_id'] for item in answer if item['_source'].get('coe_template_id',1)!=30]
    np.array(coe_ids)
    np.save(f'coe_ids_all.npy', coe_ids)

def tnt_task(type):
    lion.fetch_config()
    types = [type]
    coe_ids = np.load(f'coe_ids_{type}.npy', allow_pickle=True).tolist()
    task_name = type
    task_id = tnt_task_inner(coe_ids=coe_ids, task_name=task_name, types=types)
    print(task_id)

if __name__ == '__main__':
    # get_coeids('to_check')
    tnt_task('to_check')
