from service.app_traversal.es_client import client, headers
from utils import logger
import json



def label_node(task_id, index, labeled_result, labeled_reason):
    content = search_experience_by_taskid_index(task_id, index)
    if len(content) > 0:
        if labeled_result == '交互无响应':
            content[0]['_source']['result']['result_class'] = 1
            content[0]['_source']['result']['result_reason'] = '交互无响应'
        elif labeled_result == '交互符合预期':
            content[0]['_source']['result']['result_class'] = 0
            content[0]['_source']['result']['result_reason'] = '交互符合预期'
            content[0]['_source']['result']['result_detail_info'] = labeled_reason
        elif labeled_result == '交互不符合预期':
            content[0]['_source']['result']['result_class'] = 2
            content[0]['_source']['result']['result_reason'] = '交互不符合预期'
            content[0]['_source']['result']['result_detail_info'] = labeled_reason
        result = update_experience_as_labled(content[0])
        return result


def update_experience_as_labled(body):
    id = body['_id']
    updated_body = body['_source']
    updated_body['labeled'] = True
    updated_body = {
        'doc': updated_body
    }
    return client.update(index='traversal', id=id, body=updated_body, headers=headers)
    

def search_experience_by_taskid_index(task_id, index):
    body = {
        "query": {
            "bool": {
            "must": [
                {
                "term": {
                    "task_id": task_id
                }
                },
                {
                "term": {
                    "case_index": index
                }
                }
            ],
            "must_not": [],
            "should": [],
            "filter": []
            }
        },
        "from": 0,
        "size": "100",
        "sort": [],
        "profile": True
    }
    res = client.search(index='traversal', body=body, headers=headers)
    content = res['hits']['hits']
    return content
