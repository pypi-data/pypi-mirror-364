import uuid
from service.campaign_activity_analysis.es_client import client, headers, \
    EntityIndex
from typing import List, Dict
from service.campaign_activity_analysis.datastruct\
      import CampaignEntity


def search_or_create_entity(entity_name: str) -> CampaignEntity:
    '''
    输入活动名，直接寻找活动实体，如果没有找到则进行新建
    返回CampaignEntity数据结构
    '''
    entity = find_entity_by_name(entity_name=entity_name)
    if entity is not None:
        return entity
    id = str(uuid.uuid1().int)
    entity = CampaignEntity(entity_name, id)
    client.index(EntityIndex, body=entity.to_json_dict(), headers=headers)
    return entity


def find_entity(id: str) -> CampaignEntity:
    '''
    输入: 活动实体的id
    输出: CampaignEntity , es内部的_id
    '''
    query_josn = {
        "query": {"bool": {"must": [
            {"match": {"id": id}},
        ]}},
        "sort": {"edit_date": {"order": "desc"}}
    }
    answer = client.search(index=EntityIndex, body=query_josn, headers=headers)
    if (answer['hits']['total']['value'] == 0):
        return None
    item = CampaignEntity.from_es(answer['hits']['hits'][0])
    _id = answer['hits']['hits'][0]['_id']
    return item, _id


def find_all_entity(_size=1000, _from=0) -> Dict[str, CampaignEntity]:
    '''
    输入分页参数
    返回 id->item 的字典
    '''
    query = {
        "query": {"bool": {"must": [{"match_all": {}}]}},
        "sort": {"edit_date": {"order": "desc"}}
    }
    answer = client.search(index=EntityIndex, body=query,
                           size=_size, from_=_from, headers=headers)
    if (answer['hits']['total']['value'] == 0):
        return None
    answer = [CampaignEntity.from_es(i) for i in answer['hits']['hits']]
    dict_ans = {i.id: i for i in answer}
    return dict_ans


def batch_find_entity(id_list: List[str]) -> Dict[str, CampaignEntity]:
    '''
    返回 id->item 的字典
    '''
    query = {
        "query": {"bool": {"must": [{"terms": {"id": id_list}}]}},
    }
    answer = client.search(index=EntityIndex, body=query, headers=headers)
    if (answer['hits']['total']['value'] == 0):
        return None
    answer = [CampaignEntity.from_es(i) for i in answer['hits']['hits']]
    dict_ans = {i.id: i for i in answer}
    return dict_ans


def update_entity(entity: CampaignEntity):
    _, _id = find_entity(entity.id)
    body = {
        "doc": entity.to_json_dict()
    }
    client.update(index=EntityIndex, id=_id, body=body, headers=headers)


def find_entity_by_name(entity_name: str) -> CampaignEntity:
    query_josn = {
        "query": {"bool": {"must": [
            {"match": {"entity_name": entity_name}},
        ]}},
        "sort": {"edit_date": {"order": "desc"}}
    }
    answer = client.search(index=EntityIndex, body=query_josn, headers=headers)
    if (answer['hits']['total']['value'] == 0):
        return None
    item = CampaignEntity.from_es(answer['hits']['hits'][0])
    return item


if __name__ == '__main__':
    id = '16982863419360555052648395762653204770'
    entity = CampaignEntity('闲时立减', id)
    client.index(EntityIndex, body=entity.to_json_dict(), headers=headers)
