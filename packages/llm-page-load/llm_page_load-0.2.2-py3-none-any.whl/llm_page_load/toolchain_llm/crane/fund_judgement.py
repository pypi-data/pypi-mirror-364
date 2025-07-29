import time
from service.coe_analysis.search_coe_result_item import search_all_chain
from service.coe_analysis.coe_experience_service import batch_find_experience, find_experience
from service.coe_analysis.coe_store_service import list_coe, search_coe
from service.coe_analysis.crawler.getDoc import getCoeAsItemDict, getLatestId, get_tag, getCoeJson
from service.coe_analysis.coe_task_service import create_task_by_base_coe_data, run_chain_serial
from service.coe_analysis.llm_sdk_importer import COE_SYNC_DATA
from service.coe_analysis.result_analysis import get_result_to_show
from service.coe_analysis.search_coe_result_item import search_coe_result_item
from utils import logger
from service.coe_analysis.llm_sdk_importer import es_util
from tools.dx import send_dx_message, send_dx_message_to_person
from service.lang_chain_utils.lion_client import client as lion
from service.coe_analysis.coe_store_service import sync_once
import json
import os


def get_coe_tags(coe_id):
    tags = get_tag(coe_id)
    tag_content = []
    for phase in ['订单损失量', '涉及金额（元）', '实际资损金额（元）', '财务差异金额（元）']:
        if phase not in tags:
            continue
        text = tags[phase]
        try:
            if float(text) > 0:
                tag_content.append(f'  · {phase}: {text}')
        except Exception:
            pass
    if len(tag_content) == 0:
        tag_content = '  · 资金损失统计：暂无统计'
    else:
        tag_content = '\n'.join(tag_content)
    return tag_content


def get_default_message(task_url=None, update_before=None):
    if update_before is None:
        time_stamp = time.time()
        delay_conf = json.loads(lion.config.get(f'{lion.app_name}.coe.fund_safety_delay_day'))
        update_before = int(time_stamp - 86400*delay_conf['update_start'])
        update_before = time.strftime("%Y-%m-%d", time.localtime(update_before))

    if task_url:
        return f'''巡检修改时间范围在 {update_before} 之后的COE，没有发现资金安全COE。如有遗漏，请在「[巡检任务|{task_url}]」中进行反馈。'''
    else:
        return f'''巡检修改时间范围在 {update_before} 之后，没有发现COE的标题更新或者资损内容更新'''


def send_result(task_id, update_before, prev_info_dict: dict = {}):
    ES_ENV = os.getenv('ES_ENV', 'test')
    result_dict = get_answer(task_id=task_id)
    type = 'fund_judgement'
    hash_tag = '#prod' if ES_ENV == 'deploy' else ''
    task_url = f'https://qa.sankuai.com/coe/detail/{task_id}/coe_result' + hash_tag
    mole_url = 'https://mole.vip.sankuai.com/horus/#/maintain/capital-loss-event/mark'
    messages = [f'📢发现以下线上COE疑似有资金安全问题，请责任同学在[Mole平台|{mole_url}]完成资损COE防御手段的复盘!\n'
                + f' ([巡检|{task_url}]修改时间范围在 {update_before} 0点之后的有内容新增或者修改的COE）']
    for coe_id, v in result_dict.items():
        try:
            item_content = v[type]
            answer = item_content['content']
            brief = item_content['brief']
            tag_content = get_coe_tags(coe_id)
            incident = getCoeJson('', coe_id)['incident']
            create_at = incident['create_at']
            org_path = incident['org_path']
            # if coe_id in prev_info_dict and prev_info_dict[coe_id] == answer:
            #     prev = prev_info_dict[coe_id]
            #     logger.info(f'{brief} : 之前判断结果为 {prev}, 现在判断结果为 {answer}, 结果没有改变，不进行上报')
            #     continue
            if answer in ['是', '缺少内容无法确认，倾向于认为有资金安全风险', '缺少内容']:
                coe_lnk = f'https://coe.mws.sankuai.com/detail/{coe_id}?tab=detail'
                lnk = f'https://qa.sankuai.com/coe/result_tab/task_id/{task_id}' + \
                    hash_tag+f'?coe_id={coe_id}&type=fund_judgement'
                if answer == '是':
                    answer = '存在风险'
                messages.append(f"【[{brief}|{coe_lnk}]】\n  · COE创建时间：{create_at}\n  · 团队：{org_path}\n" +
                                f"  · LLM资金风险判断：[{answer}|{lnk}]\n{tag_content}")
        except Exception as e:
            logger.exception(e.args)
            pass
    if len(messages) == 1:
        logger.info('没有召回')
        messages = get_default_message(task_url=task_url, update_before=update_before)
    else:
        messages = '\n\n'.join(messages)
    send_message(messages)


def send_message(message):
    lion.fetch_config()
    user_ids = json.loads(lion.config[f'{lion.app_name}.coe.fund.dx_user'])
    for user_id in user_ids:
        send_dx_message_to_person(user_id, message)
    gruops = json.loads(lion.config[f'{lion.app_name}.coe.fund.dx_group'])
    for group in gruops:
        send_dx_message(group, message)


def get_answer(task_id):
    result_list, total = search_all_chain(task_id, from_=0, size=1000)
    result_dict = {item.coe_id: {'coe_id': item.coe_id, 'brief': item.brief} for item in result_list}
    _, exp_dict = batch_find_experience([i.answer_message[0].exp_id for i in result_list if len(i.answer_message) > 0])

    for item in result_list:
        item_content = item.to_json_dict()
        if (not item.is_done or len(item.answer_message) == 0):
            result_to_show = item.error if item.error is not None else 'error'
        else:
            first_saved_exp_id = item.answer_message[0].exp_id
            if first_saved_exp_id not in exp_dict:
                exp_dict[first_saved_exp_id], _ = find_experience(first_saved_exp_id)
            result_to_show = get_result_to_show(result_item=item, first_saved_exp=exp_dict.get(first_saved_exp_id))
        item_content['content'] = result_to_show
        result_dict[item.coe_id][item.type] = item_content
    return result_dict


def is_title_change(prev_task_id, coe_id, now_title, type='fund_judgement'):
    result_item, _id = search_coe_result_item(coe_id=coe_id, type=type, task_id=prev_task_id)
    return result_item.brief == now_title


def get_prev_info(coe_ids):
    prev_info_dict = {}
    coe_ids_new = set()
    for coe_id in coe_ids:
        sync_once(str(coe_id))
        time.sleep(1)
        coe, _id = search_coe(str(coe_id))
        try:
            prev_info_dict[coe_id] = coe.fund_safety.is_fund_danger.analysis_result
        except Exception:
            prev_info_dict[coe_id] = ''
        try:
            result_item, _id = search_coe_result_item(coe_id=coe_id, type='fund_judgement',
                                                      task_id=coe.fund_safety.is_fund_danger.analysis_task_id[0])
            if coe.brief == result_item.brief and coe.fund_safety.is_fund_danger.analysis_result == '不相关':
                # 不相关且没改变名字，就绝对不相关了
                continue
            if not result_item.is_reviewed:
                coe_ids_new.add(coe_id)
        except Exception:
            coe_ids_new.add(coe_id)
    return prev_info_dict, list(coe_ids_new)


def get_deleted(create_start, create_end):
    # 获取可能是最近删除的COE
    coe_ids, coe_item_dict = getCoeAsItemDict(create_start=create_start, create_end=create_end, level='')
    already_in_codes, _ = list_coe(create_begin=create_start, create_end=create_end, size=1000, _from=0)
    deleted = []
    for coe in already_in_codes:
        coe_id = coe.coe_id
        if coe_id not in coe_item_dict:
            deleted.append(coe_id)

    answer = []
    for coe_id in deleted:
        try:
            history = getCoeJson('history', coe_id)
            history = history['history']
            delete_flg = False
            for h in history:
                if h.get('new', '') == "已删除":
                    delete_flg = True
                    break
            if delete_flg:
                answer.append(coe_id)
        except Exception as e:
            logger.exception(f"无法获取 {coe_id}" + e.args)

    return answer


def fund_judgement_job():
    types = ['fund_judgement']
    time_stamp = time.time()
    lion.fetch_config()
    delay_conf = json.loads(lion.config.get(f'{lion.app_name}.coe.fund_safety_delay_day'))
    tenday_stamp = int(time_stamp - 86400*delay_conf['create_start'])  # 拉10天的COE，其中昨天有修改的都要重新算
    yesterday_stamp = int(time_stamp - 86400*delay_conf['update_start'])
    now = time.strftime("%Y-%m-%d", time.localtime(time_stamp))
    yesterday = time.strftime("%Y-%m-%d", time.localtime(yesterday_stamp))
    coe_ids, coe_item_dict = getLatestId(update_start=yesterday, create_start=tenday_stamp,
                                         create_end=now, level='')
    # 跑的前后需要进行对比
    # 需要过滤已经review过的资金安全分析，不用重跑
    prev_info_dict, coe_ids = get_prev_info(coe_ids)
    if len(coe_ids) == 0:
        logger.info('今日无需进行分析')
        send_message(get_default_message())
        return
    task_name = f'资金安全分析{yesterday}-{now}'
    coe_list = [coe_item_dict[coe_id] for coe_id in coe_ids]
    task_id = create_task_by_base_coe_data(coe_list=coe_list, name=task_name, source='循环触发',
                                           type_list=types, submitter='auto', to_submit_task=False)
    coe_id_list = [i.coe_id for i in coe_list]
    logger.info(f'循环任务 {task_name} 创建完成 = {task_id}')
    run_chain_serial(coe_id_list, types, task_id)
    logger.info(f'循环任务 {task_name} 执行完成 = {task_id}')
    send_result(task_id, update_before=yesterday, prev_info_dict=prev_info_dict)


def mark_delete_once(coe_id):
    coe_store_data, _id = search_coe(coe_id)
    coe_store_data.is_deleted = True
    # 存入
    body = {
        "doc": coe_store_data.to_json_dict()
    }
    es_util.update(index=COE_SYNC_DATA, id=_id, body=body)


def mark_deleted():
    time_stamp = time.time()
    lion.fetch_config()
    delay_conf = json.loads(lion.config.get(f'{lion.app_name}.coe.fund_safety_delay_day'))
    create_start = int(time_stamp - 86400*delay_conf['create_start'])  # 拉10天的COE，其中昨天有修改的都要重新算
    create_end = time.strftime("%Y-%m-%d", time.localtime(time_stamp))
    create_start = time.strftime("%Y-%m-%d", time.localtime(create_start))
    ids = get_deleted(create_start=create_start, create_end=create_end)
    for id in ids:
        mark_delete_once(coe_id=id)


if __name__ == '__main__':
    # 定时任务执行方法
    # cd /opt/meituan/tool/compatibility; PYTHONPATH=. ES_ENV=default Env=test
    # venv/bin/python crane/fund_judgement.py
    # > /data/applogs/inf/com.sankuai.toolchain.coverage.agent/crane-fund_judgement.log 2>&1
    fund_judgement_job()
    mark_deleted()
    # send_result('265230966279001719957562732503743461346', yesterday, prev_info_dict=prev_info_dict)
    # coe_ids = get_deleted('2023-09-20', '2023-09-30')
    # print(coe_ids)
