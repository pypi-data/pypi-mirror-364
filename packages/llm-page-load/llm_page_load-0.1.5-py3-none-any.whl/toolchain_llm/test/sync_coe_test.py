from service.coe_analysis.coe_chain_service import chain_result_save
from service.coe_analysis.coe_store_service import batch_sync_coe_result, batch_sync_coe_storage, list_coe, search_coe, search_coe_result_item_list, sync_coe_result
from service.coe_analysis.coe_task_service import search_task, update_task
from service.coe_analysis.crawler.getDoc import getLatestId
from service.coe_analysis.data_structure import ChangeLog
from service.coe_analysis.llm_sdk_importer import TASK_TYPES, es_util
from service.coe_analysis.search_coe_result_item import search_all_chain, search_coe_result_item
from utils import get_now_str, read_json, logger
import time
import tqdm


def remove_marked():
    begin = '2023-05-01'
    end = '2023-05-31'
    coe_list, total = list_coe(begin, end, size=200, _from=0)
    for coe in coe_list:
        result_list, _ids = search_coe_result_item_list(coe.coe_id, type='cause',
                                                        task_id='135466354620276601608175835433368817954')
        for r, _id in zip(result_list, _ids):
            # if r.is_reviewed:
            chain_result_save(r.to_json_dict(),
                                  change_log=ChangeLog(
                                      action='reviewedTagChange',
                                      new_tag=True,
                                      old_tag=False
                                  ))


def sync_all_result():
    types = [i['type'] for i in TASK_TYPES]
    types = ['cause']
    begin = '2023-05-01'
    end = '2023-05-31'
    coe_list, total = list_coe(begin, end, size=200, _from=0)
    for coe in coe_list:
        for type in types:
            logger.info(f'开始同步 coeid={coe.coe_id} type={type}')
            try:
                sync_coe_result(coe.coe_id, type=type)
            except Exception as e:
                logger.exception(e.args)


def main(a):
    time_stamp = time.time() - 86400*15*a
    tenday_stamp = int(time_stamp - 86400*15)
    now = time.strftime("%Y-%m-%d", time.localtime(time_stamp))
    tenday = time.strftime("%Y-%m-%d", time.localtime(tenday_stamp))
    logger.info(f'coe同步任务开始，搜寻 {tenday} ~ {now} 存在更新的 coe')
    coe_ids, coe_item_dict = getLatestId(update_start=tenday, create_start=tenday,
                                         create_end=now, level='')
    batch_sync_coe_storage(coe_ids)


def mark_task_detail_edit_time(task_id, types):
    task, _task_id = search_task(task_id=task_id)
    task.name = task.name + '[调优]'
    result_list, _ = search_all_chain(task_id=task_id)
    coe_id_list = set()
    for result_item in tqdm.tqdm(result_list):
        item, _id = search_coe_result_item(
            coe_id=result_item.coe_id,
            type=result_item.type,
            task_id=task.id)
        assert item.id == result_item.id
        coe_id_list.add(item.coe_id)
        item.edit_time = '2000-01-01T00:00:00Z'
        es_util.update('coe_analysis_detail', id=_id, body={"doc": item.to_json_dict()})
    update_task(task, _task_id)
    coe_id_list = list(coe_id_list)
    time.sleep(1)
    batch_sync_coe_result(coe_id_list=coe_id_list, type_list=types)


def get_experienc_by_id(id_list):
    index = 'coe_analysis_experience'
    query = {
        "_source": {"excludes": ['search_embedding']},
        "query": {"bool": {"must": [{"terms": {"id": id_list}}]}},
    }
    answer = es_util.client.search(index=index, body=query, headers=es_util.headers, size=10000)
    hits = [i for i in answer['hits']['hits']]
    _ids = [i['_id'] for i in answer['hits']['hits']]
    return hits, _ids


def true_delete_result_item(coe_id, task_id, type):
    item, _id = search_coe_result_item(coe_id=coe_id, type=type, task_id=task_id)
    exphits, exp_ids = get_experienc_by_id([i.exp_id for i in item.answer_message])
    actions = [{'delete': {"_index": 'coe_analysis_experience', '_id': id}} for id in exp_ids]
    actions.append({'delete': {"_index": 'coe_analysis_detail', '_id': _id}})
    resp = es_util.client.bulk(body=actions, headers=es_util.headers)
    print(resp)


def remove_light_analysis_result(task_id, type_list):
    result_list, _ = search_all_chain(task_id=task_id)
    coe_id_list = set()
    for coe in tqdm.tqdm(result_list):
        coe_store_data, _ = search_coe(coe.coe_id)
        if coe_store_data.coe_template_name == '轻量记录':
            true_delete_result_item(coe.coe_id, coe.task_id[0], coe.type)
            coe_id_list.add(coe.coe_id)
    coe_id_list = list(coe_id_list)
    time.sleep(1)
    batch_sync_coe_result(coe_id_list=coe_id_list, type_list=type_list)


if __name__ == '__main__':
    remove_light_analysis_result('183563198296074837544123449536711931915', ['to_test'])
    remove_light_analysis_result('59248959909929266482361625829710411787', [
        "to_test", "to_claim", "to_check", "to_grey", "to_inspect", "to_rollback", "not_to_delay",
        "not_to_illagle_change_data"
    ])
    remove_light_analysis_result('136913029988078801139023364952049498123', ['to_test'])
    # mark_task_detail_edit_time('49727601233289460096801380273987434507', ['to_inspect'])
    # mark_task_detail_edit_time('81971156569386265959084015758111848459', ['to_rollback'])
    # mark_task_detail_edit_time('10272206538188609726881725498555545611', ['to_rollback'])
    # mark_task_detail_edit_time('231007924929587559603181727043402774539', ['to_claim'])
    # mark_task_detail_edit_time('324085932901600189016670577982425184267', ['to_claim'])
    # mark_task_detail_edit_time('130023219200329409398545700046791686155', ['to_test'])
    # mark_task_detail_edit_time('183563198296074837544123449536711931915', ['to_test'])
    # mark_task_detail_edit_time('59248959909929266482361625829710411787', [
    #     "to_test", "to_claim", "to_check", "to_grey", "to_inspect", "to_rollback", "not_to_delay",
    #     "not_to_illagle_change_data"
    # ])
    # mark_task_detail_edit_time('136913029988078801139023364952049498123', ['to_test'])
    # data = read_json('test/data/baseline_cause.json')
    # ids = [d['coe_id'] for d in data]
    # batch_sync_coe_storage(ids)
    # sync_all_result()
    # for i in range(6, 18):
    #     print(i)
    #     main(i)

    # remove_marked()
    # sync_all_result()
    # sync_coe_result('244085', type='cause')
