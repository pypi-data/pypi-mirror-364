from typing import Dict, List
from service.coe_analysis.coe_chain_service import chain_result_get, search_task
from service.coe_analysis.coe_experience_service import batch_find_experience, find_experience
from service.coe_analysis.coe_task_service import get_single_task
import difflib
from service.coe_analysis.search_coe_result_item import search_all_chain
from utils import logger
from service.coe_analysis.data_structure import COEResult, COEAnalysisTask, Experience, MetaMessage, MetricsData
from service.coe_analysis.result_analysis import get_result_to_show


def get_coe_to_cal(type, chains: List[COEResult]):
    answer = []
    for chain in chains:
        if chain.is_reviewed and chain.type == type:
            answer.append(chain)
    return answer


def cal_sequence_edit_distance(task: COEAnalysisTask, coe_to_cal: List[COEResult], type: str):
    if (type != 'cause'):
        return 0
    cnt = 0
    for chain in coe_to_cal:
        for log in chain.change_log:
            if log.action == 'changeIndex':
                cnt += 1
    return round(cnt/len(coe_to_cal), 3)


def cal_mean_edit_distance(task: COEAnalysisTask, coe_to_cal: List[COEResult], type: str):
    total = 0
    dis = 0
    _, exp_dict = batch_find_experience([i.answer_message[0].exp_id for i in coe_to_cal if len(i.answer_message) > 0])
    for chain in coe_to_cal:
        try:
            org_res = chain.message[-1].content
            org_answer = org_res.split('\n\n')[0]
            first_saved_exp_id = chain.answer_message[0].exp_id
            if first_saved_exp_id not in exp_dict:
                exp_dict[first_saved_exp_id], _ = find_experience(first_saved_exp_id)
            changed_answer = exp_dict[first_saved_exp_id].data[-1].content
            matcher = difflib.SequenceMatcher(None, a=org_answer, b=changed_answer)
            dis += 1 - matcher.quick_ratio()
            total += 1
        except Exception as e:
            logger.exception(e.args)
            pass
    if (total == 0):
        return 0
    return round(dis/total, 3)


def cal_total_edit_rate(task: COEAnalysisTask, coe_to_cal: List[COEResult], type: str):
    cnt = 0
    for chain in coe_to_cal:
        to_count_log = [i for i in chain.change_log if i.action != 'reviewedTagChange']
        cnt += len(to_count_log)
    return cnt


def cal_accept_rate(task: COEAnalysisTask, coe_to_cal: List[COEResult], type: str):
    total = 0
    cnt = 0
    detail_cnt = 0
    _, exp_dict = batch_find_experience([i.answer_message[0].exp_id for i in coe_to_cal if len(i.answer_message) > 0])
    for chain in coe_to_cal:
        try:
            org_res = chain.message[-1].content
            org_answer = Experience(
                task_id=[task.id], coe_id=chain.coe_id, type=type,
                data=[
                    MetaMessage(role='user', content=chain.reason),
                    MetaMessage(role='assistant', content=org_res.split('\n\n')[0])
                ], search_text=chain.reason
            )
            first_saved_exp_id = chain.answer_message[0].exp_id
            if first_saved_exp_id not in exp_dict:
                exp_dict[first_saved_exp_id], _ = find_experience(first_saved_exp_id)
            changed_answer = exp_dict[first_saved_exp_id]
            org_type = get_result_to_show(chain, org_answer)
            changed_type = get_result_to_show(chain, changed_answer)
            if (org_type == changed_type):
                cnt += 1
                content_changed = [i for i in chain.change_log if i.action == 'contentChange']
                if (len(content_changed) == 0):
                    detail_cnt += 1
            total += 1
        except Exception as e:
            logger.exception(e.args)
            pass
    if (total == 0):
        return 0, 0
    if cnt == 0:
        return 0, 0
    return round(cnt/total, 3), round(detail_cnt/cnt, 3)


def metrics_task(task_id: str):
    task, _id = search_task(task_id)
    chains, total = search_all_chain(task.id)
    answer: Dict[str, MetricsData] = {}
    for type in task.sub_task_type_list:
        coe_to_cal = get_coe_to_cal(type, chains)
        if (len(coe_to_cal) == 0):
            continue
        accept_rate, reason_accept_rate = cal_accept_rate(task, coe_to_cal, type)
        answer[type] = MetricsData(
            sequence_edit_rate=cal_sequence_edit_distance(task, coe_to_cal, type),
            mean_edit_distance=cal_mean_edit_distance(task, coe_to_cal, type),
            total_edit_rate=cal_total_edit_rate(task, coe_to_cal, type),
            accept_rate=accept_rate,
            reason_accept_rate=reason_accept_rate,
            total=len(coe_to_cal)
        ).to_json_dict()
    return answer


def compare_task_with_base_task(task_id: str, base_task_id: str):
    result_dict, _, _, _ = chain_result_get(10000, 0, task_id)
    base_result_dict, _, _, _ = chain_result_get(10000, 0, base_task_id)
    base_result_list, _ = search_all_chain(base_task_id, from_=0, size=10000)
    base_task = get_single_task(base_task_id)
    type_list = base_task.sub_task_type_list
    answer = {}
    for type in type_list:
        total = 0
        item = {
            'total': 0,
            'consistant': 0,
            'rate': 0
        }
        for coe in base_result_list:
            if (coe.is_done and coe.is_reviewed):
                total += 1
                coe_id = coe.coe_id
                if (result_dict[coe_id][type]['content'] == base_result_dict[coe_id][type]['content']):
                    item['consistant'] += 1
        if (total == 0):
            continue
        item['total'] = total
        item['rate'] = item['consistant']/item['total']
        answer[type] = item
    return answer
