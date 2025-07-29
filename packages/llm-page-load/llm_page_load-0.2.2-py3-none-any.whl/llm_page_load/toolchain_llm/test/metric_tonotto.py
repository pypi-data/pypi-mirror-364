from typing import List
from service.coe_analysis.coe_store_service import _get_result_, list_coe
from datetime import datetime, timedelta
from service.coe_analysis.coe_task_service import get_all_task
from service.coe_analysis.data_structure import COEResult, COEStoreageData, Tag
from service.coe_analysis.search_coe_result_item import search_all_chain
from utils import write_io


def count_rate(type, coes: List[COEStoreageData]):
    total = len(coes)
    acc = 0
    for coe in coes:
        tag: Tag = getattr(coe, type)
        if tag.analysis_result_raw == tag.analysis_result:
            acc += 1
    return acc / total


types = [
    {"title": '要测试', 'type': 'to_test'},
    {"title": '要周知', 'type': 'to_claim'},
    {"title": '要审核', 'type': 'to_check'},
    {"title": '要灰度', 'type': 'to_grey'},
    {"title": '要观测', 'type': 'to_inspect'},
    {"title": '要可回滚', 'type': 'to_rollback'},
    {"title": '不要延报故障', 'type': 'not_to_delay'},
    {"title": '不要违规变更数据', 'type': 'not_to_illagle_change_data'},
]


def count_total(coes: List[COEStoreageData]):
    acc = 0
    total = len(coes)
    for coe in coes:
        flg = True
        for item in types:
            type = item['type']
            tag: Tag = getattr(coe, type)
            if tag.analysis_result_raw != tag.analysis_result:
                flg = False
        if flg:
            acc += 1
    return acc / total


def make_excel():
    start_date = datetime(2024, 2, 1)
    end_date = datetime(2024, 11, 30)
    current_date = start_date
    data = []
    while current_date <= end_date:
        begin = current_date.strftime('%Y-%m-%d')
        next_month = (current_date + timedelta(days=31)).replace(day=1)
        last_day_of_month = next_month - timedelta(days=1)
        end = last_day_of_month.strftime('%Y-%m-%d')
        hits, total = list_coe(begin, end, size=100, _from=0)
        current_date = next_month
        item = {'date': begin}
        for type in types:
            rate = count_rate(type['type'], hits)
            item[type['title']+'一致率'] = '{:.2f}'.format(rate*100)
        item['整体一致率'] = '{:.2f}'.format(count_total(hits)*100)
        data.append(item)
    write_io('test/data/acc.xlsx', data)


def get_detective_search():
    task_list, total = get_all_task(
        1000, 0, other_must_inner=[
            {"wildcard": {"name": "*COE 判别式筛查*"}}
        ])
    data = []
    for task in task_list:
        print(task)
        length = len(task.choosed_coe_list)
        if length < 20:
            continue
        result_list, total = search_all_chain(task_id=task.id)
        item = {
            '触发者': task.submitter,
            '数量': length
        }
        for result in result_list:
            if isinstance(result, COEResult):
                tag = _get_result_(result)
                count = item.get(tag, 0)
                count += 1
                item[tag] = count
        data.append(item)
    write_io('test/data/acc.xlsx', data)


if __name__ == '__main__':
    get_detective_search()
