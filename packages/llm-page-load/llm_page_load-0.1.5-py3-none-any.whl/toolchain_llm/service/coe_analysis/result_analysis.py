from service.coe_analysis.data_structure import COEResult, Experience
import re
from utils import logger


def check_changed(result_item: COEResult, answer: str):
    # 计算是否有更改
    for log in result_item.change_log:
        if log.action in ['reviewedTagChange', 'changeIndex', 'reasonableTagChange']:
            continue
        else:
            answer += '（修改）'
            break
    return answer


def get_result_to_show(result_item: COEResult, first_saved_exp: Experience):
    '''进行结果分析的静态方法'''
    try:
        if (result_item.is_done is False and result_item.error is not None):
            return result_item.error
        type = result_item.type
        pattern = None
        if (type in ['cause']):
            pattern = re.compile(r'\[(.*?)\]')
        elif type in ["to_test", "to_claim", "to_check", "to_grey",
                      "to_inspect", "to_rollback", "not_to_delay",
                      "not_to_illagle_change_data", 'null_check']:
            pattern = re.compile(r'结果[:：]\s*([\u4e00-\u9fa5]+)')
        elif type in ['fund_acc', 'fund_activity_save', 'rule_safety']:
            pattern = re.compile(r'结果[:：]\s*([\u4e00-\u9fa5]+)')
        elif type in ["trigger_condition"]:
            pattern = re.compile(r'结果[:：]\s*([\u4e00-\u9fa5]+)')
        elif type in ['determinate_search']:
            pattern = re.compile(r'结果[:：]\s*([\u4e00-\u9fa5]+)')
        first_answer = first_saved_exp.data[-1].content
        if (pattern and first_answer):
            match = pattern.findall(first_answer)
            if (len(match) > 0):
                return str(match[0])
        return first_answer
    except Exception as e:
        logger.exception(e.args)
        return None
