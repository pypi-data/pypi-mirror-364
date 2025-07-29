import time
from typing import List
from service.coe_analysis.coe_store_service import batch_sync_coe_storage, sync_once, batch_search_coe_storage
from service.coe_analysis.crawler.getDoc import getLatestId
from service.coe_analysis.coe_task_service import create_task_by_base_coe_data, run_chain_serial
from tools.dx import send_dx_message, send_dx_message_to_person
from utils import logger
from service.coe_analysis.data_structure import BaseCoeData
from service.lang_chain_utils.lion_client import client as lion
import json
from crane.cause_analysis import filter_update


def send_message(message, person_only=False):
    user_ids = json.loads(lion.config[f'{lion.app_name}.coe.cause.dx_user'])
    for user_id in user_ids:
        send_dx_message_to_person(user_id, message)
    if not person_only:
        gruops = json.loads(lion.config[f'{lion.app_name}.coe.cause.dx_group'])
        for group in gruops:
            send_dx_message(group, message)


def mole_tag_task_inner(coe_ids: List[str], task_name: str, sync: bool = True):
    lion.fetch_config()
    types = ['fund_aggr_classify']
    if sync:
        for coe_id in coe_ids:
            sync_once(coe_id=coe_id)
    if len(coe_ids) == 0:
        logger.info('本周无需分析')
        return
    coe_list, _ = batch_search_coe_storage(coe_ids=coe_ids)
    coe_list = [BaseCoeData(
        coe_id=i.coe_id, brief=i.brief, level=i.level
    ) for i in coe_list]
    task_id = create_task_by_base_coe_data(coe_list=coe_list, name=task_name, source='循环触发',
                                           type_list=types, submitter='auto', to_submit_task=False)
    coe_id_list = [i.coe_id for i in coe_list]
    logger.info(f'循环任务 {task_name} 创建完成 = {task_id}')
    lnk = f'https://qa.sankuai.com/coe/detail/{task_id}/task_description'
    send_message(f'循环任务 [{task_name}|{lnk}] 创建完成 = {task_id}')
    run_chain_serial(coe_id_list, types, task_id)
    logger.info(f'循环任务 {task_name} 执行完成 = {task_id}')
    batch_sync_coe_storage(coe_id_list=coe_ids)
    send_message(f'循环任务 [{task_name}|{lnk}] 执行完成 = {task_id}')
    return task_id


def mole_tag_task():
    time_stamp = time.time()
    lion.fetch_config()
    delay_conf = json.loads(lion.config.get(f'{lion.app_name}.coe.cause.delay_day'))
    create_start_stamp = int(time_stamp - 86400*delay_conf['create_start'])  # 拉10天的COE，其中昨天有修改的都要重新算
    update_start_stamp = int(time_stamp - 86400*delay_conf['update_start'])
    create_end_stamp = int(time_stamp - 86400*delay_conf['create_end'])
    create_start = time.strftime("%Y-%m-%d", time.localtime(create_start_stamp))
    update_start = time.strftime("%Y-%m-%d", time.localtime(update_start_stamp))
    create_end = time.strftime("%Y-%m-%d", time.localtime(create_end_stamp))
    coe_ids, coe_item_dict = getLatestId(update_start=update_start, create_start=create_start,
                                         create_end=create_end, level='')
    # coe_ids = filter_update(coe_ids, update_start=update_start_stamp, update_end=create_end_stamp)
    task_name = f'mole平台打标 {update_start}-{create_end}'
    return mole_tag_task_inner(coe_ids=coe_ids, task_name=task_name)


if __name__ == '__main__':
    # 定时任务执行方法
    # cd /opt/meituan/tool/compatibility; PYTHONPATH=. ES_ENV=default Env=test
    # venv/bin/python crane/cause_analysis.py
    # > /data/applogs/inf/com.sankuai.toolchain.coverage.agent/crane-cause_analysis.log 2>&1
    mole_tag_task()
