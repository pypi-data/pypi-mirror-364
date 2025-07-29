from typing import List, Tuple
from service.coe_analysis.coe_experience_service import batch_find_experience
from service.coe_analysis.data_structure import COEResult
from service.coe_analysis.llm_sdk_importer import es_util


def search_coe_result_item(coe_id=None, type=None, task_id=None):
    index = 'coe_analysis_detail'
    inner = []
    if coe_id:
        inner.append({"term": {"coe_id": coe_id}})
    if type:
        inner.append({"term": {"type": type}})
    if task_id:
        inner.append({"term": {"task_id": task_id}})
    query_josn = {
        "query": {"bool": {"must": inner}}
    }
    answer = es_util.search(index=index, query=query_josn)
    coe_result_item = COEResult.from_es(answer[0])
    _id = answer[0]['_id']
    return coe_result_item, _id


def search_coe_result_item_with_experience(coe_id, type, task_id):
    index = 'coe_analysis_detail'
    query_josn = {
        "query": {"bool": {"must": [
            {"term": {"coe_id": coe_id}},
            {"term": {"type": type}},
            {"term": {"task_id": task_id}}
        ]}}
    }
    answer = es_util.search(index=index, query=query_josn)
    coe_result_item = COEResult.from_es(answer[0])
    _id = answer[0]['_id']
    answer_message, _ = batch_find_experience(
        [i.exp_id for i in coe_result_item.answer_message])
    similiar_case_list, _ = batch_find_experience(
        [i.exp_id for i in coe_result_item.similiar_case_list])
    return coe_result_item, _id, similiar_case_list, answer_message


def search_all_chain(task_id, from_=0, size=10000):
    index = 'coe_analysis_detail'
    query_json = {
        "_source": {"excludes": ['search_vector']},
        "query": {"bool": {"must": [{"term": {"task_id": task_id}}]}},
        "sort": [{"coe_id": {"order": "desc"}}]
    }
    answer = es_util.client.search(
        body=query_json, index=index, from_=from_, size=size, headers=es_util.headers)
    total = answer['hits']['total']['value']
    result_list = [COEResult.from_es(i) for i in answer['hits']['hits']]
    return result_list, total


def batch_search_chain_by_id(chain_id_list: List[str], size: int = 1000) -> Tuple[List[COEResult], List[str]]:
    try:
        query_josn = {
            "query": {"bool": {"must": [
                {"terms": {"id": chain_id_list}}
            ]}},
            "size": size
        }
        answer = es_util.search(index='coe_analysis_detail', query=query_josn)
        items = [COEResult.from_es(i) for i in answer]
        _ids = [i['_id'] for i in answer]
        return items, _ids
    except Exception:
        return None, None
