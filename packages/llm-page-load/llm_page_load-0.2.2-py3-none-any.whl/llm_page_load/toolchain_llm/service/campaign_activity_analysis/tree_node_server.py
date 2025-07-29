import uuid
import re
import json
from service.campaign_activity_analysis.es_client import client, headers,\
    TreeNodeIndex, es_client
from typing import List, Dict
from service.lang_chain_utils.embedding import embed
from service.campaign_activity_analysis.config_reader import get_lion_config
from service.campaign_activity_analysis.datastruct import ChangeLog, TestCaseTreeNode
from utils import get_now_str
from typing import Tuple


def create_node(type: str, content: str, need_embedding=False, **kargs)\
        -> TestCaseTreeNode:
    id = str(uuid.uuid1().int)
    if need_embedding:
        embedding = embed.embed_query(content)
        kargs['embedding'] = embedding
    node = TestCaseTreeNode(id, type=type, content=content, **kargs)
    node.edit_date = get_now_str()
    client.index(TreeNodeIndex, body=node.to_json_dict(), headers=headers)
    return node


def create_node_by_instance(node: TestCaseTreeNode, need_embedding=False):
    if need_embedding:
        node.embedding = embed.embed_query(node.content.replace('\u200b', ' '))
    node.edit_date = get_now_str()
    client.index(TreeNodeIndex, body=node.to_json_dict(), headers=headers)
    return node


def find_node(id: str) -> Tuple[TestCaseTreeNode, str]:
    query_josn = {
        "query": {"bool": {"must": [
            {"match": {"id": id}},
        ]}}
    }
    answer = client.search(index=TreeNodeIndex,
                           body=query_josn, headers=headers)
    item = TestCaseTreeNode.from_es(answer['hits']['hits'][0])
    _id = answer['hits']['hits'][0]['_id']
    return item, _id


def batch_find_node(id_list: List[str]) -> Dict[str, TestCaseTreeNode]:
    if (id_list is None or len(id_list) == 0):
        return {}
    query = {
        "query": {"bool": {"must": [{"terms": {"id": id_list}}]}},
    }
    answer = client.search(index=TreeNodeIndex, body=query, headers=headers)
    answer = [TestCaseTreeNode.from_es(i) for i in answer['hits']['hits']]
    dict_ans = {i.id: i for i in answer}
    return dict_ans


def update_node(node: TestCaseTreeNode, changelog: ChangeLog = None):
    _, _id = find_node(node.id)
    node.edit_date = get_now_str()
    if changelog:
        node.change_log.append(changelog)
    data = {
        "doc": node.to_json_dict()
    }
    client.update(TreeNodeIndex, id=_id, body=data, headers=headers)


def node_similarity_search(query: str, rule_type: str = None, k=2) -> List[TestCaseTreeNode]:
    '''进行经验知识搜索，但是这里只能搜到提问，回答需要再度拼装'''
    threshold = float(get_lion_config('threshold.few_shoot'))
    query_vector = embed.get_embedding(query)
    vector_field = 'embedding'
    must_inner = [
        {"term": {"is_marked": 'true'}},
        {"term": {"type": 'query'}},
        {"exists": {"field": 'children_id'}},
        {"exists": {"field": 'embedding'}},
    ]
    if rule_type is not None:
        must_inner.append({"term": {"rule_type": rule_type}})
    body = {
        "script_score": {
            "query": {"bool": {"must": must_inner}},
            "script": {
                "source": f"cosineSimilarity(params.query_vector, '{vector_field}') + 1.0",
                "params": {"query_vector": query_vector}}}
    }
    query = {'query': body, 'size': k}
    response = client.search(body=query, index=TreeNodeIndex, headers=headers)
    return [TestCaseTreeNode.from_es(i) for i in response['hits']['hits']
            if float(i['_score']) > threshold]


def get_node_with_exp_message(nodes: List[TestCaseTreeNode])\
        -> List[TestCaseTreeNode]:
    '''将query节点后面的回答节点全部拼装到一起形成字符串'''
    result = []
    for node in nodes:
        if (node.children_id is not None and len(node.children_id) != 0):
            # 一般情况下是都会存在子节点的，但是在数据同步的过程中可能会出现没有创建子节点的情况，那么就会默认用原始的
            answer: List[str] = []
            for id, child in batch_find_node(node.children_id).items():
                answer.append(child.content)
                node.type

            if (len(answer) > 1):
                answer = '['+','.join(answer)+']'
            else:
                text = answer[0].strip()
                if text.startswith('{') and text.endswith('}'):
                    answer = '['+text+']'
                else:
                    answer = answer[0]
            node.answer_message = answer
        result.append(node)
    return result


def search_all_marked(_size=1000, _from=0):
    '''不是所有is_marked都能取，必须要有children_id才有exp_message，必须要有embedding才能search'''
    body = {
        "query": {"bool": {"must": [
            {"term": {"is_marked": 'true'}},
            {"term": {"type": 'query'}},
            {"exists": {"field": 'children_id'}},
            {"exists": {"field": 'embedding'}},
        ]}}}
    response = client.search(
        body=body, index=TreeNodeIndex, size=_size, from_=_from,
        headers=headers)
    parents = [TestCaseTreeNode.from_es(i) for i in response['hits']['hits']]
    nodes = get_node_with_exp_message(parents)
    return nodes


def get_query_thought_list(text):
    '''从回答中获取json列表并进行拆分的函数'''
    pattern = r'\[\s*(\{.*?\})\s*\]'
    match = re.search(pattern, text, re.DOTALL)
    if match:
        json_list_str = match.group(0)
        json_list_str = json_list_str.replace('，', ',')
        return json.loads(json_list_str)
    else:
        return None


def node_weight(node: TestCaseTreeNode):
    weight = 1
    if node.type == 'query':
        # 提问阶段不算权重
        weight = 0
    node_dict = batch_find_node(node.children_id)
    for child in node.children_id:
        if child not in node_dict:
            child_node = find_node(child)
        else:
            child_node = node_dict.get(child)
        weight += node_weight(child_node)
    return weight


def remove_node_from_tree(node_id: str):
    '''从树中排除节点，但是知识删引用，不会真的删除实体'''
    node, _id = find_node(node_id)
    parent, p_id = find_node(node.parent_id)
    new_children = []
    old_children = parent.children_id
    for id in parent.children_id:
        if id == node.id:
            continue
        new_children.append(id)
    changelog = ChangeLog(
        type='REMOVE_CHILDREN',
        ref_node_id=parent.id,
        weight=node_weight(node),
        old_children=old_children,
        new_children=new_children
    )
    parent.change_log.append(changelog)
    parent.children_id = new_children
    data = {
        "doc": parent.to_json_dict()
    }
    client.update(TreeNodeIndex, id=p_id, body=data, headers=headers)
    es_client.refresh(TreeNodeIndex)
    return parent, changelog


def mark_node(node_id: str, is_marked=True):
    node, _id = find_node(node_id)
    changelog = ChangeLog(
        type='MARK_NODE',
        ref_node_id=node.parent_id,
        weight=1,
        new_content=is_marked,
        old_content=node.is_marked
    )
    node.is_marked = is_marked
    node.change_log.append(changelog)
    data = {
        "doc": node.to_json_dict()
    }
    client.update(TreeNodeIndex, id=_id, body=data, headers=headers)
    return node, changelog

def trans_to_utf8(content):
    try:
        content = json.loads(content)
        return json.dumps(content, ensure_ascii=False, indent=4)
    except Exception as e:
        print(e.args)
        return content


def get_node_deep(nd_id: str, nd_dict: Dict[str, TestCaseTreeNode] = {}):
    '''递归形成树，并且拼装返回值，使用batch_find_node更快获取es查询结果'''
    nd = nd_dict.get(nd_id, find_node(nd_id)[0])
    if (nd.children_id is None or len(nd.children_id) == 0):
        return {'id': nd.id, 'label': trans_to_utf8(nd.content),
                'short_name': nd.short_name, 'type': nd.type, 'data': nd}
    nd_dict = batch_find_node(nd.children_id)
    return {'id': nd.id, 'label': trans_to_utf8(nd.content),
            'short_name': nd.short_name, 'type': nd.type, 'data': nd,
            'children': [get_node_deep(i, nd_dict=nd_dict)
                         for i in nd.children_id]}
