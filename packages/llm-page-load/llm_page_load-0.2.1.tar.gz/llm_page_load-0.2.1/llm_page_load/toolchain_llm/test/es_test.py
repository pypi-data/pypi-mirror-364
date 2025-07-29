import datetime
import uuid

from service.lang_chain_utils.es_storage import es_client, _default_script_query
from utils import logger


def test_get_texts():
    query1 = {
        "query": {
            "bool":{
                "filter":{
                    "term":{
                        "id":"171477531537222791542056816258274300194"
                    }

                }
            }
        }
    }
    print(es_client.client_search(index_name='coe_analysis_task',query=query1))
    filter={
        "tags":'标签1'
    }
    logger.info(_default_script_query(query_vector=[],filter=filter,vector_field='vector'))
    logger.info(es_client.get_relevant_docs(index_name='llm_demo',vector_field='vector',text='测试',filter=filter))

def test_add_texts():
    docs=[]
    docs.append({
        "id": str(uuid.uuid1().int),
        "start_date": datetime.datetime.now(),
        "name": "测试测试6.21",
        "source": "测试触发",
        "state": "执行中",
        "progress": "3/3"

    })
    logger.info(es_client.add_texts(index_name='coe_analysis_task',docs=docs,refresh_indices=True))