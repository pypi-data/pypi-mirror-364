from typing import List
from service.coe_analysis.crawler import getDoc
import uuid
import time
from service.coe_analysis.llm_sdk_importer import es_util
from service.lang_chain_utils.lion_client import client as lion
from service.lang_chain_utils.embedding import embed
from service.coe_analysis.data_structure import Experience, MetaMessage


def create_experience(type: str, coe_id: str, task_id: str,
                      message_list: List[MetaMessage],
                      pre_checked_passed: bool = False, need_embedding: bool = True) -> Experience:
    id = str(uuid.uuid1().int)
    search_text = message_list[0].content
    if coe_id is not None:
        coeJson = getDoc.getCoeJson('', coe_id)
        brief = coeJson['incident']['brief']
        level = coeJson['incident']['level']
    else:
        level = ''
        brief = ''
        coe_id = '0'
    embedding = None
    if need_embedding:
        embedding = embed.embed_query(search_text)
    exp = Experience(
        task_id=task_id,
        coe_id=coe_id,
        type=type,
        data=message_list,
        search_text=search_text,
        search_embedding=embedding,
        id=id,
        is_marked=False,
        brief=brief,
        level=level,
        pre_checked_passed=pre_checked_passed
    )
    es_util.index(index='coe_analysis_experience',
                  body=exp.to_json_dict(), id=id)
    return exp


def find_experience(id: str):
    index = 'coe_analysis_experience'
    query = {
        "_source": {"excludes": ['search_embedding']},
        "query": {"bool": {"must": [{"term": {"id": id}}]}},
    }
    answer = es_util.search(index=index, query=query)
    return Experience.from_es(answer[0]), answer[0]['_id']


def batch_find_experience(id_list: List[str]):
    if len(id_list) == 0:
        return [], {}
    index = 'coe_analysis_experience'
    query = {
        "_source": {"excludes": ['search_embedding']},
        "query": {"bool": {"must": [{"terms": {"id": id_list}}]}},
    }
    answer = es_util.client.search(
        index=index, body=query, headers=es_util.headers, size=10000)
    answer = [Experience.from_es(i) for i in answer['hits']['hits']]
    dict_ans = {i.id: i for i in answer}
    return [dict_ans[i] for i in id_list if i in dict_ans], dict_ans


def bulk_create_exp_by_object(exps: List[Experience]):
    index = 'coe_analysis_experience'
    body = []
    for exp in exps:
        body.append({"index": {"_index": index}})
        body.append(exp.to_json_dict())
    result = es_util.client.bulk(body=body, headers=es_util.headers)
    if result["errors"]:
        raise Exception("bulk操作失败,错误信息为:{}".format(result["errors"]))


def save_experience(experience: Experience):
    # 只有 marked 才会从这里修改
    fresh_time = int(lion.config.get(f'{lion.app_name}.llm.fresh_time', 1))
    index = 'coe_analysis_experience'
    search_text = experience.search_text
    search_embedding = embed.get_embedding(search_text)
    experience.search_embedding = search_embedding
    experience.is_marked = True
    if (experience.id):
        query = {
            "query": {"bool": {"must": [{"term": {"id": experience.id}}]}},
        }
        answer = es_util.client.search(
            index=index, body=query, headers=es_util.headers)
        if (answer['hits']['total']['value'] > 0):
            _id = answer['hits']['hits'][0]['_id']
            data = {
                "doc": experience.to_json_dict()
            }
            es_util.update(index, id=_id, body=data)
        else:
            index_json = experience.to_json_dict()
            es_util.index(index=index, body=index_json, id=experience.id)
    else:
        id = str(uuid.uuid1().int)
        experience.id = id
        index_json = experience.to_json_dict()
        es_util.index(index=index, body=index_json, id=id)
    time.sleep(fresh_time)  # 写入需要 1s 进行刷盘
    return experience.id


def save_experience_by_id(experience: Experience, _id: str):
    index = 'coe_analysis_experience'
    data = {
        "doc": experience.to_json_dict()
    }
    es_util.update(index, id=_id, body=data)


def get_experience(type, size, from_):
    index = 'coe_analysis_experience'
    query_json = {
        "_source": ["id", "data", "task_id", "type", "coe_id", "search_text",
                    "brief", "level"],
        "query": {"bool": {"must": [
            {"term": {"type": type}},
            {"term": {"is_marked": True}}
        ]}},
        "sort": [{"id": {"order": "desc"}}]
    }
    answer = es_util.client.search(
        body=query_json, index=index, from_=from_, size=size,
        headers=es_util.headers)
    total = answer['hits']['total']['value']
    result_list = [Experience.from_es(i) for i in answer['hits']['hits']]
    return result_list, total


def experience_mark_update(id, is_marked, sleep=True):
    fresh_time = int(lion.config.get(f'{lion.app_name}.fresh_time', 1))
    index = 'coe_analysis_experience'
    exp, _id = find_experience(id=id)
    # if (exp.pre_checked_passed or is_marked is False):
    exp.is_marked = is_marked
    body = {
        "doc": exp.to_json_dict()
    }
    es_util.update(index=index, id=_id, body=body)
    if sleep:
        time.sleep(fresh_time)  # 写入需要 1s 进行刷盘
    return


if __name__ == '__main__':
    index = 'coe_analysis_experience'
