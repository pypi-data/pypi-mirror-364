import time
from typing import List
from service.coe_analysis.crawler.getDoc import getLatestId, getCoeJson
from service.coe_analysis.coe_task_service import create_task_by_base_coe_data, run_chain_serial
from tools.dx import send_dx_message, send_dx_message_to_person
from utils import logger
from service.lang_chain_utils.lion_client import client as lion
import json


def filter_update(coe_ids: List[str], update_start, update_end):
    valid = []
    for coe_id in coe_ids:
        resp = getCoeJson(category='history', id=coe_id)
        if 'error' in resp and resp['error'] is not None:
            logger.info(f'请求 {coe_id} 的 histroy 失败')
            continue
        if 'history' not in resp or not isinstance(resp['history'], list):
            logger.info(f'请求 {coe_id} 的 histroy 失败')
            continue
        v_flg = False  # 一般而言不是新的coe不更新
        for h in resp['history']:
            key = h.get('key', '')
            logger.info(f'coe-{coe_id} 修改 key= {key}')
            if key in ['时间线', '原因分析', '经验教训', '故障类型', '影响详情']:
                t = h['time']
                t = time.strptime(t, "%Y-%m-%d %H:%M:%S")
                t = int(time.mktime(t))
                if t > update_start:
                    # 必须在 update_start 以后有更新，不保证一定能过
                    v_flg = True
                if t > update_end:
                    # 确保不存在 update_end 以后的 coe
                    v_flg = False
                    break  # 优先停止
        if v_flg:
            valid.append(coe_id)
    return valid


def send_message(message, person_only=False):
    user_ids = json.loads(lion.config[f'{lion.app_name}.coe.cause.dx_user'])
    for user_id in user_ids:
        send_dx_message_to_person(user_id, message)
    if not person_only:
        gruops = json.loads(lion.config[f'{lion.app_name}.coe.cause.dx_group'])
        for group in gruops:
            send_dx_message(group, message)


def cause_analysis_task():
    types = ['cause']
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
    coe_ids = list(set(coe_ids))
    if len(coe_ids) == 0:
        logger.info('本周无需分析')
        return
    task_name = f'原因分析 {update_start}-{create_end}'
    coe_list = [coe_item_dict[coe_id] for coe_id in coe_ids]
    task_id = create_task_by_base_coe_data(coe_list=coe_list, name=task_name, source='循环触发',
                                           type_list=types, submitter='auto', to_submit_task=False)
    coe_id_list = [i.coe_id for i in coe_list]
    logger.info(f'循环任务 {task_name} 创建完成 = {task_id}')
    lnk = f'https://qa.sankuai.com/coe/detail/{task_id}/task_description'
    send_message(f'循环任务 [{task_name}|{lnk}] 创建完成 = {task_id}')
    run_chain_serial(coe_id_list, types, task_id)
    logger.info(f'循环任务 {task_name} 执行完成 = {task_id}')
    send_message(f'循环任务 [{task_name}|{lnk}] 执行完成 = {task_id}')
    # send_result(task_id, update_before=yesterday, prev_info_dict=prev_info_dict)


if __name__ == '__main__':
    # 定时任务执行方法
    # cd /opt/meituan/tool/compatibility; PYTHONPATH=. ES_ENV=default Env=test
    # venv/bin/python crane/cause_analysis.py
    # > /data/applogs/inf/com.sankuai.toolchain.coverage.agent/crane-cause_analysis.log 2>&1
    cause_analysis_task()
