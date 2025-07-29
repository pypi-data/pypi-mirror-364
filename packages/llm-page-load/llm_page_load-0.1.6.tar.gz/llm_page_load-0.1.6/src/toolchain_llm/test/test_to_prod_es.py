from llmcore_sdk.data_connection.es_client import LLMElasticsearchClient
import configparser
import os
from tqdm import tqdm
from service.coe_analysis.llm_sdk_importer import (COE_ANALYSIS_DETAIL, COE_ANALYSIS_EXPERIENCE,  # noqa
                                                   COE_ANALYSIS_TASK, COE_SYNC_DATA)
from service.file_config_reader import read_lion_file_config  # noqa

ES_ENV = os.getenv('ES_ENV', 'default')
config = read_lion_file_config('es_client.conf')


aim_tasks = ['50760893964828434448794430300997292322', '282622674248073297008693909207285888994', '3212451634903037826704876472522248482', '72647669748284547755302006952713785634', '118182783104075848789461928370239443234', '135466354620276601608175835433368817954', '301101088849564132410126092342629765410', '47249954195004195456016221558062190882', '305004994916303559208714008424154665250',   # noqa
             '283254323475733967199661061239048894434', '50552224618097420794184511002862024674', '82767128024693786802851375834452064226', '157543257572084255548869920876105431010', '168117857076819690310111547551002261474',  # noqa
             '14641756662665557502118919957528311778', '61189730623420916925979046876388128738', '172277232291932626729440512393527818210', '53815782204436451594691372850820282338', '216092551819681562554857027437110622178', '252980936305801145946502862524392011746',  # noqa
             '83897689674063982777135103072478296034', '236506680629594266128833448674870032354', '93860728402473110259651707270412498914', '97843530825926671615953497943322261474', '80443552060288810896331832026324137954', '50552224618097420794184511002862024674', '151610925648794138264478605916342974434', '258746321373604914176717968981035972578', '244001834672276267948978301671672510434', '205143130086674760941570526801912264674', '135777740048871239948448963033443989474', '86794010640340758069518310478908356578']  # noqa


def get_es_client(env):
    accesskey = config[env]['accesskey']
    appkey = config[env]['appkey']
    is_online_env = config[env]['isOnlineEnv'] == 'true'
    es_util = LLMElasticsearchClient(
        accesskey=accesskey, appkey=appkey, is_online_env=is_online_env)
    return es_util


es_prod_client = get_es_client('deploy')
es_test_client = get_es_client('default')


def bulk_(sources, index, client: LLMElasticsearchClient):
    actions = []
    batch_size = 128
    total_records = len(sources)
    for i in range(0, total_records, batch_size):
        batch_sources = sources[i:i+batch_size]
        actions = []
        for source in batch_sources:
            if 'id' in source:
                ans = client.search(index=index, query={"query": {
                    "bool": {
                        "must": [
                            {"term": {"id": source['id']}}
                        ]
                    }
                }})
                if len(ans) != 0:
                    actions.append({'update': {"_index": index, "_id": ans[0]['_id']}})
                    actions.append({'doc': source})
                    continue
            actions.append({"index": {"_index": index}})
            actions.append(source)
        # 执行上传操作
        client.client.bulk(body=actions)


def bulk_prod(sources, index):
    return bulk_(sources, index, es_prod_client)


def bulk_test(sources, index):
    return bulk_(sources, index, es_test_client)


def unmark_experience():
    body = {
        "script": {
            "source": "ctx._source.is_marked = false",
            "lang": "painless"
        },
        "query": {
            "bool": {
                "must": [
                    {"term": {"is_marked": True}}
                ]
            }
        }
    }
    rest = es_prod_client.client.update_by_query(index=COE_ANALYSIS_EXPERIENCE,
                                                 body=body)
    print(rest)


def update_exp(task_id):
    query = {"query": {'bool': {'must': [
        {'term': {"task_id": task_id}},
    ]}}, "size": 10000}
    rest = es_test_client.search(index=COE_ANALYSIS_EXPERIENCE,
                                 query=query)
    sources = [i['_source'] for i in rest]
    print(len(sources))
    # task_id_set = set()
    # for source in sources:
    #     task_ids = source['task_id']
    #     if isinstance(task_ids, list):
    #         for _id in task_ids:
    #             task_id_set.add(_id)
    #     elif isinstance(task_ids, str):
    #         task_id_set.add(task_ids)
    # task_id_set = list(task_id_set)
    # print(task_id_set)
    bulk_prod(sources=sources, index=COE_ANALYSIS_EXPERIENCE)
    return


def update_task(task_id):
    query = {"query": {'bool': {'must': [
        {'term': {"id": task_id}},
    ]}}, "size": 10000}
    task = es_test_client.search(index=COE_ANALYSIS_TASK, query=query)
    task = task[0]['_source']
    query = {"query": {'bool': {'must': [
        {'term': {"task_id": task_id}},
    ]}}, "size": 10000}
    details = es_test_client.search(index=COE_ANALYSIS_DETAIL, query=query)
    details = [i['_source'] for i in details]
    exps = es_test_client.search(index=COE_ANALYSIS_EXPERIENCE, query=query)
    exps = [i['_source'] for i in exps]
    bulk_prod([task], COE_ANALYSIS_TASK)
    bulk_prod(details, COE_ANALYSIS_DETAIL)
    bulk_prod(exps, COE_ANALYSIS_EXPERIENCE)


def main():
    for i in tqdm(aim_tasks):
        update_task(i)


if __name__ == '__main__':
    # es_prod_client.index('evals-llmeval-recorder', body={'data': {'correct': True, "id": 1, 'result': 1}})
    pass
