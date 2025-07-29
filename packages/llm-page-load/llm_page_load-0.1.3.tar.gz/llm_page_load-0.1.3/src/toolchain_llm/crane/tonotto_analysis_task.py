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
    user_ids = json.loads(lion.config[f'{lion.app_name}.coe.tonotto.dx_user'])
    groups = json.loads(lion.config[f'{lion.app_name}.coe.tonotto.dx_group'])
    if precheck or Env == 'test':
        user_ids = ['liyilun02']
        groups = []
    for user_id in user_ids:
        send_dx_message_to_person(user_id, message)
    if not person_only:
        for group in groups:
            send_dx_message(group, message)


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
    send_message(f'[{task_name}|https://qa.sankuai.com/coe/detail/{task_id}/coe_result] 任务创建完成，LLM 开始进行六要两不要分析',
                 precheck=precheck)
    coe_id_list = [i.coe_id for i in coe_list]
    logger.info(f'循环任务 {task_name} 创建完成 = {task_id}')
    run_chain_serial(coe_id_list, types, task_id)
    logger.info(f'循环任务 {task_name} 执行完成 = {task_id}')
    batch_sync_coe_storage(coe_id_list=coe_ids)
    return task_id


def tnt_task(precheck=False):
    lion.fetch_config()
    types = ["to_test", "to_claim", "to_check", "to_grey", "to_inspect", "to_rollback", "not_to_delay",
             "not_to_illagle_change_data"]
    if precheck:
        types = ['to_claim', 'not_to_delay', 'to_rollback']
    # 获取当前日期
    current_date = datetime.date.today()
    # 获取上个月的1号
    if current_date.month == 1:
        first_day_of_last_month = datetime.date(current_date.year - 1, 12, 1)
    else:
        first_day_of_last_month = datetime.date(current_date.year, current_date.month - 1, 1)
    # 获取上个月的最后一天
    last_day_of_last_month = current_date.replace(day=1) - datetime.timedelta(days=1)
    create_start = first_day_of_last_month.strftime("%Y-%m-%d")
    update_start = first_day_of_last_month.strftime("%Y-%m-%d")
    create_end = last_day_of_last_month.strftime("%Y-%m-%d")
    category = ['backend', 'app', 'data', 'security']
    coe_ids, _ = getLatestId(update_start=update_start, create_start=create_start,
                             create_end=create_end, level='', categoryDate=category, category=category)
    raw_len = len(coe_ids)
    ids2, _ = getLatestId(update_start=update_start, create_start=create_start, coe_template_id=30,
                          create_end=create_end, level='', categoryDate=category, category=category)
    light_len = len(ids2)
    coe_ids = list(set(coe_ids) - set(ids2))
    task_name = f'六要两不要分析 {create_start}-{create_end}'
    if lion.config[f'{lion.app_name}.coe.tonotto.crane.debug'] == 'true':
        task_id = '168117857076819690310111547551002261474'
    else:
        task_id = tnt_task_inner(coe_ids=coe_ids, task_name=task_name, types=types, precheck=precheck)
    link = make_wiki(coe_ids=coe_ids, task_name=task_name, types=types,
                     raw_len=raw_len, light_len=light_len, task_id=task_id)
    task_lnk = f'https://qa.sankuai.com/coe/detail/{task_id}/coe_result'
    store_lnk = f'https://qa.sankuai.com/coe/coestorage?startDate={create_start}&endDate={create_end}'
    send_message(f'[{task_name}|{task_lnk}] 分析完成，[学城报告|{link}]',
                 person_only=True, precheck=precheck)
    send_message(f'[{task_name}|{task_lnk}] 智能分析完成，请 @chenchaoyi @zhaoyuanni @gongxixi @penglong02 @huojian 于当月12号前完成疑似违规 coe 的人工筛查，并与研发 X2 对齐违规结论，在[系统|{store_lnk}]上完成结果上报',   # noqa
                 precheck=precheck)


if __name__ == '__main__':
    # 定时任务执行方法
    # cd /opt/meituan/tool/compatibility; PYTHONPATH=. ES_ENV=default Env=test
    # venv/bin/python crane/cause_analysis.py
    # > /data/applogs/inf/com.sankuai.toolchain.coverage.agent/crane-cause_analysis.log 2>&1
    tnt_task()
