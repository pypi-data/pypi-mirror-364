from crane.mole_tag_analysis import mole_tag_task_inner
from service.coe_analysis.coe_chain_service import run_chain
from service.coe_analysis.coe_experience_service import find_experience, save_experience_by_id
from service.coe_analysis.coe_store_service import batch_sync_coe_result, batch_sync_coe_storage, list_coe
from service.coe_analysis.coe_task_service import add_coe, search_task, update_task
from service.coe_analysis.data_structure import BaseCoeData
from service.coe_analysis.crawler.getDoc import getCoeJson
from service.coe_analysis.runners import get_runner_by_type
from service.coe_analysis.runners.fund import COEFundAggregrateClassifyRunner
from service.coe_analysis.search_coe_result_item import search_coe_result_item
from utils import read_json, write_json
import re


def add_coe_and_run(coe_id: str, task_id: str, type: str):
    json_info = getCoeJson('', coe_id)
    brief = json_info['incident']['brief']
    level = json_info['incident']['level']
    coe = BaseCoeData(
        coe_id=coe_id,
        brief=brief,
        level=level
    )
    add_coe(coe, type, task_id=task_id, to_submit_task=True)


def force_run_coe(coe_id, task_id, type):
    result, _id = search_coe_result_item(coe_id, type, task_id)
    run_chain(task_id, force=True, result_list=[result])


def rerun(coe_id: str, task_id: str, type='fund_aggr_classify'):
    chain, _id = search_coe_result_item(
        coe_id=coe_id, type=type, task_id=task_id)
    runner = COEFundAggregrateClassifyRunner(result_item=chain, _id=_id)
    runner.init_prompt(type)
    exp, exp_id = find_experience(chain.answer_message[0].exp_id)
    runner.ask_fund_security()
    if len(runner.cls_ans) != 0:
        exp.data[-1].content += ', ' + ', '.join(runner.cls_ans)
        save_experience_by_id(exp, exp_id)
    runner.done()


def fund_search(coe_id, task_id, type):
    pt = '需要你判断线上问题是否符合如下情况之一：'
    pattern = r'回答[：:]\s*(.*)'
    chain, _id = search_coe_result_item(
        coe_id=coe_id, type=type, task_id=task_id)
    for e in chain.answer_message:
        exp, exp_id = find_experience(e.exp_id)
        if pt in exp.data[0].content:
            ans = re.findall(pattern, exp.data[-1].content)
            if len(ans) > 0 and ans[0] == '是':
                print(chain.brief)
                return chain.brief
    return False


if __name__ == '__main__':
    # task_name = '资金安全分析7-8月'
    coes, _ = list_coe(create_begin='2024-01-01', create_end='2024-02-10', size=10000, _from=0,
                       is_exclude_deleted=True, is_exclude_light_template=True)
    coe_ids = [coe.coe_id for coe in coes if '演练' not in coe.brief]
    write_json('test/data/coeids-01-02.json', coe_ids)
    # coe_ids = read_json('test/data/coeids-7-8.json')
    # task_id = mole_tag_task_inner(coe_ids=coe_ids, task_name=task_name, sync=False)
    # print(task_id)
    # batch_sync_coe_result(coe_id_list=coe_ids, type_list=['fund_aggr_classify'])

    # task_id = '171014066648277000957578087319000322338'
    # type = 'fund_aggr_classify'
    # coes = []
    # for i in coe_ids:
    #     ans = fund_search(i, task_id, type)
    #     if ans:
    #         coes.append(i)
    # print(coes)
    # for coe_id in ['249972']:
    #     force_run_coe(coe_id, task_id, type)
    # # run_chain(task_id=task_id, force=True)
