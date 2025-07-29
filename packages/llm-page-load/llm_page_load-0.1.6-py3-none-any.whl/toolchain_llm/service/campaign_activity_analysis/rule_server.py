import uuid
from service.campaign_activity_analysis.es_client \
    import client, headers, ActivityRuleIndex
from typing import List, Dict
from service.campaign_activity_analysis.datastruct \
    import CampaignEntity, CampaignRule
from utils import get_now_str


def create_rule(rule: str, entity_item_list: List[CampaignEntity], **kargs)\
        -> CampaignRule:
    '''根据可变参数，创建一个rule，必须有rule和实体'''
    _must_inner = [
        {"match": {"rule": rule}},  # 模糊匹配
        {"term": {"is_deleted": False}}
    ]
    for item in entity_item_list:
        _must_inner.append({"term": {"entity_id_list": item.id}})
    query_josn = {
        "query": {"bool": {"must": _must_inner}},
        "size": 10
    }
    entity_id_list = [i.id for i in entity_item_list]
    answer = client.search(index=ActivityRuleIndex,
                           body=query_josn, headers=headers)
    if (answer['hits']['total']['value'] != 0):
        items = [CampaignRule.from_es(i) for i in answer['hits']['hits']]
        for item in items:
            if item.rule != rule:
                # 精确匹配
                continue
            if set(item.entity_id_list) == set(entity_id_list):
                return item

    id = str(uuid.uuid1().int)
    rule = CampaignRule(entity_id_list=entity_id_list,
                        id=id, rule=rule, **kargs)
    client.index(ActivityRuleIndex, body=rule.to_json_dict(), headers=headers)
    return rule


def find_rule(id: str) -> CampaignRule:
    query_josn = {
        "query": {"bool": {"must": [
            {"term": {"id": id}},
            {"term": {"is_deleted": False}}
        ]}}
    }
    answer = client.search(index=ActivityRuleIndex,
                           body=query_josn, headers=headers)
    result_item = CampaignRule.from_es(answer['hits']['hits'][0])
    return result_item


def find_rule_by_entities(entity_item_list: List[CampaignEntity]) -> List[CampaignRule]:
    '''
    根据实体查询叠加规则，但是这里没有type进行区分，所以对于佣金等没法支持
    查询方式是且逻辑
    '''
    _must_inner = [{"term": {"is_deleted": False}}]
    entity_id_list = [i.id for i in entity_item_list]
    for _id in entity_id_list:
        _must_inner.append({"term": {"entity_id_list": _id}})
    query_josn = {
        "query": {"bool": {"must": _must_inner}}
    }
    answer = client.search(index=ActivityRuleIndex,
                           body=query_josn, headers=headers)
    if (answer['hits']['total']['value'] != 0):
        items = [CampaignRule.from_es(i) for i in answer['hits']['hits']]
        return items
    return []


def find_rule_by_or_entities(entity_item_list: List[CampaignEntity]) -> List[CampaignRule]:
    '''
    根据实体查询叠加规则，但是这里没有type进行区分，所以对于佣金等没法支持
    或逻辑
    '''
    entity_id_list = [i.id for i in entity_item_list]
    _must_inner = [
        {"term": {"is_deleted": False}},
        {"terms": {"entity_id_list": entity_id_list}}
    ]
    query_josn = {
        "query": {"bool": {"must": _must_inner}}
    }
    answer = client.search(index=ActivityRuleIndex,
                           body=query_josn, headers=headers)
    if (answer['hits']['total']['value'] != 0):
        items = [CampaignRule.from_es(i) for i in answer['hits']['hits']]
        return items
    return []


def batch_find_rule(id_list: List[str]) -> Dict[str, CampaignRule]:
    '''
    返回字典
    '''
    query = {
        "query": {"bool": {"must": [
            {"terms": {"id": id_list}},
            {"term": {"is_deleted": False}}
        ]}},
    }
    answer = client.search(index=ActivityRuleIndex,
                           body=query, headers=headers)
    answer = [CampaignRule.from_es(i) for i in answer['hits']['hits']]
    dict_ans = {i.id: i for i in answer}
    return dict_ans


def update_rule_field(rule: CampaignRule, fields: List[str]):
    '''暂时未使用，根据字段选择性更新内容'''
    painless_ = []
    rule = rule.to_json_dict()
    for field in fields:
        if field not in rule:
            continue
        elif isinstance(rule[field], list) or isinstance(rule[field], dict):
            continue
        elif isinstance(rule[field], bool):
            painless_.append(f"ctx._source.{field}={str(rule[field]).lower()}")
        else:
            painless_.append(f"ctx._source.{field}={rule[field]}")
    painless_ = ';'.join(painless_)
    query_json = {
        "script": {
            "source": painless_,
            "lang": "painless"
        },
        "query": {"bool": {"must": [{"term": {"id": rule.id}}]}},
    }
    client.update_by_query(index=ActivityRuleIndex,
                           body=query_json, headers=headers)


def find_all_rule(_size=1000, _from=0) -> List[CampaignRule]:
    query = {
        "query": {"bool": {"must": [{"term": {"is_deleted": False}}]}},
        "sort": {"edit_date": {"order": "desc"}}
    }
    answer = client.search(index=ActivityRuleIndex,
                           body=query, size=_size,
                           from_=_from, headers=headers)
    if (answer['hits']['total']['value'] == 0):
        return None
    answer = [CampaignRule.from_es(i) for i in answer['hits']['hits']]
    return answer


def update_rule_info(rule: CampaignRule):
    '''更新一条rule，由id检索'''
    query_josn = {
        "query": {"bool": {"must": [
            {"term": {"id": rule.id}},
        ]}}
    }
    answer = client.search(index=ActivityRuleIndex,
                           body=query_josn, headers=headers)
    _id = answer['hits']['hits'][0]['_id']
    rule.edit_date = get_now_str()
    body = {
        'doc': rule.to_json_dict()
    }
    client.update(index=ActivityRuleIndex, id=_id, body=body, headers=headers)
    return


if __name__ == '__main__':
    rules = find_all_rule()
    for rule in rules:
        rule.is_deleted = False
        update_rule_info(rule)
