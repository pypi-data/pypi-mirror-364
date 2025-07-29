from typing import Dict, List
import uuid
from service.coe_analysis.coe_chain_service import create_result_info_by_item, update_chain_result
from service.coe_analysis.coe_experience_service import batch_find_experience, bulk_create_exp_by_object
from service.coe_analysis.config_reader import DEFAULT_AGGR_COEID_PLACEHOLDER
from service.coe_analysis.data_structure import Answer, COEResult, COEStoreageData, Experience, MetaMessage
from service.coe_analysis.coe_store_service import batch_search_coe_storage
import json
import time
from service.coe_analysis.result_analysis import get_result_to_show
from service.coe_analysis.search_coe_result_item import search_coe_result_item
from service.lang_chain_utils.embedding import m3embed
from utils import get_now_str, logger
from service.coe_analysis.coe_task_service import search_task, update_task
from service.coe_analysis.llm_sdk_importer import es_util, COE_ANALYSIS_EXPERIENCE, COE_ANALYSIS_DETAIL
from collections import deque
import re


def decode_aggr_to_tree(text: str):
    lines = text.split("\n")
    rootList = []
    total_root = {"label": "root", "children": rootList}
    currentRoot = None
    for line in lines:
        line = line.strip()
        if re.match(r"^[a-z]\.", line, re.IGNORECASE):
            desc = line.split(".")[1].strip()
            desc = re.split(r":|：", desc) if re.search(r":|：", desc) else [desc, ""]
            title = desc[0].strip()
            other = desc[1].strip()
            other = other.replace("包括", "")
            other = other.replace("等。", "")
            other = re.split(r"、|，|,", other)
            tmp_node = {"label": title, "children": [], 'parent': currentRoot}
            children = [{"label": item, 'parent': tmp_node} for item in other]
            tmp_node['children'] = children
            currentRoot["children"].append(tmp_node)
        elif re.match(r"^\d+\.", line):
            desc = line.split(".")[1].strip()
            desc = re.split(r":|：", desc) if re.search(r":|：", desc) else [desc, ""]
            title = desc[0].strip()
            if currentRoot:
                rootList.append(currentRoot)
            currentRoot = {"label": title, "children": [], 'parent': total_root}
    if currentRoot:
        rootList.append(currentRoot)
    total_root['children'] = rootList
    total_root['parent'] = None
    return [total_root]


def find_parents(node):
    ans = []
    while node:
        ans.append(node)
        node = node.get('parent', None)
    return ans


def delete_cause_search_history(query: str, task_id: str, type: str):
    query_josn = {
        "query": {"bool": {"must": [
            {"term": {"type": type}},
            {"term": {"task_id": task_id}}
        ]}},
        "size": 1000
    }
    answer = es_util.search(index=COE_ANALYSIS_DETAIL, query=query_josn)
    result_items = [COEResult.from_es(i) for i in answer]
    result_items = [i for i in result_items if i.brief == query]
    for r in result_items:
        r.brief = ''
        r.error = '已删除'
        update_chain_result(r)


class CauseSearchSimpleRunner():
    TYPE = 'aggr_recall_placeholder'

    def __init__(self, coe_ids: List[str], task_id: str, threshold: float = 0.75) -> None:
        self.coe_ids = coe_ids
        self.threshold = threshold
        task, _id_task = search_task(task_id)
        self.task_id = task_id
        self._id_task = _id_task
        self.task = task
        id = str(uuid.uuid1().int)
        self.result_item = COEResult(task_id=[task_id], coe_id=id, type=self.TYPE,
                                     id=id, brief='', occur_time=get_now_str())
        # 必须在外部创建chain
        # self.result_item = create_result_info_by_item(self.result_item)
        # 初始化上下文的数据，可以在cache里复用
        query_josn = {
            "query": {"bool": {"must": [
                {"term": {"type": self.TYPE}},
                {"term": {"task_id": task_id}}
            ]}},
            "size": 1000
        }
        answer = es_util.search(index=COE_ANALYSIS_DETAIL, query=query_josn)
        result_items = [COEResult.from_es(i) for i in answer]
        self.history_result_items = result_items
        self.cached_exps = {}
        self.coes, _ = batch_search_coe_storage(coe_ids)
        self.coes

    def find_and_update_exp_cache(self, result_item):
        exp_ids = [i.exp_id for i in result_item.answer_message]
        to_update = []
        for exp_id in exp_ids:
            if exp_id not in self.cached_exps:
                to_update.append(exp_id)
        answer_message, ans_dict = batch_find_experience(to_update)
        self.cached_exps.update(ans_dict)
        return [self.cached_exps[i] for i in exp_ids]

    def get_cause_search_history(self, query: str, task_id: str, type: str, threshold: float):
        result_items = self.history_result_items
        result_items = [i for i in result_items if i.brief == query]
        coe_result_item: COEResult = [i for i in result_items if i.error is None][0]
        answer_message = self.find_and_update_exp_cache(coe_result_item)
        score_list = []
        coe_ids = []
        for exp in answer_message:
            q = exp.data[0].content
            a = exp.data[1].content
            q = json.loads(q)
            a = json.loads(a)
            data = {**q, **a}
            score_list.append(data)
            coe_ids.append(data['coe_id'])
        coes = self.coes
        coe_dict = {str(coe.coe_id): coe for coe in coes}
        for ind in range(len(score_list)):
            score_list[ind]['coe'] = coe_dict[str(score_list[ind]['coe_id'])]
        return [i for i in score_list if i['score'] > threshold and i['is_related']], coe_result_item

    def make_result(self, score_list: List[Dict]):
        exps = []
        for ind, item in enumerate(score_list):
            coe: COEStoreageData = item['coe']
            score: str = item['score']
            is_related = item['is_related']
            text: str = item['text']
            q = json.dumps({'coe_id': coe.coe_id, 'brief': coe.brief, 'text': text, 'index': ind}, ensure_ascii=False)
            a = json.dumps({'score': score, 'is_related': is_related}, ensure_ascii=False)
            message = [
                MetaMessage('user', q),
                MetaMessage('assistant', a)
            ]
            exp_id = str(uuid.uuid1().int)
            exp = Experience(
                task_id=self.task_id,
                coe_id=str(uuid.uuid1().int),
                type=self.result_item.type,
                data=message,
                id=exp_id,
                search_text=coe.brief
            )
            exps.append(exp)
        bulk_create_exp_by_object(exps=exps)
        return exps

    def retrive_experience(self, query_vector: List[float]):
        vector_field = 'search_embedding'
        type = 'embedding_storage'
        query = {
            "_source": {"excludes": ['search_embedding']},
            "query": {
                "script_score": {
                    "query": {"bool": {"must": [
                        {"term": {"task_id": self.task_id}},
                        {'term': {'type': type}}
                    ]}},
                    "script": {
                        "source": f"cosineSimilarity(params.query_vector, '{vector_field}')",
                        "params": {"query_vector": query_vector}
                    }
                }
            },
            'size': 1000
        }
        answer = es_util.search(index=COE_ANALYSIS_EXPERIENCE, query=query)
        exp_list = [Experience.from_es(i) for i in answer]
        scores = [i['_score'] for i in answer]
        return exp_list, scores

    def done(self, query: str, exp_list: List[Experience]):
        self.result_item.reason = query
        self.result_item.brief = query
        self.result_item.error = None
        self.result_item.is_done = True
        time.sleep(1)
        if self.TYPE not in self.task.sub_task_type_list:
            self.task.sub_task_type_list.append(self.TYPE)
            update_task(self.task, self._id_task)
        self.result_item.answer_message = [Answer(exp_id=exp.id) for exp in exp_list]
        update_chain_result(self.result_item)

    def simple_search(self, query: str):
        time1 = time.time()
        # coes, _ = batch_search_coe_storage(self.coe_ids)
        coes = self.coes
        time2 = time.time()
        logger.info(f'batch_search_coe_storage 耗时 {time2-time1}s')
        coe_dict = {str(coe.coe_id): coe for coe in coes}
        query_embedding = m3embed.embed_query(query)
        time3 = time.time()
        logger.info(f'embed_query 耗时 {time3-time2}s')
        exp_list, scores = self.retrive_experience(query_vector=query_embedding)
        time4 = time.time()
        logger.info(f'retrive_experience 耗时 {time4-time3}s')
        score_dict = {}
        for exp, score in zip(exp_list, scores):
            prev_item = score_dict.get(exp.coe_id, {'score': -1})
            prev_score = prev_item['score']
            if prev_score < score:
                score_item = {
                    'score': score,
                    'text': exp.search_text
                }
                score_dict[exp.coe_id] = score_item
        score_list = [{"coe": coe_dict[k], "score": v['score'], 'text': v['text'], 'is_related': True}
                      for k, v in score_dict.items()]
        score_list = sorted(score_list, key=lambda x: x["score"], reverse=True)
        time5 = time.time()
        logger.info(f'计算 耗时 {time5-time4}s')
        exps = self.make_result(score_list)
        self.done(query, exps)
        time6 = time.time()
        logger.info(f'make_result 耗时 {time6 - time5}s')
        return [i for i in score_list if i['score'] > self.threshold], self.result_item


def get_simple_cause_search_with_history(query, task_id, threshold, coe_ids,
                                         cached_runner: CauseSearchSimpleRunner = None):
    if cached_runner:
        runner = cached_runner
    else:
        runner = CauseSearchSimpleRunner(coe_ids=coe_ids, task_id=task_id, threshold=threshold)
    try:
        answer, chain = runner.get_cause_search_history(task_id=task_id, query=query,
                                                        type=CauseSearchSimpleRunner.TYPE,
                                                        threshold=threshold)
        logger.info('成功获取历史召回')
        return answer, chain
    except Exception:
        logger.warn('没有找到历史召回,尝试重新召回')

    # 如果没有历史召回的话，创一个chain
    id = str(uuid.uuid1().int)
    runner.result_item = COEResult(task_id=[task_id], coe_id=id, type=runner.TYPE,
                                   id=id, brief='', occur_time=get_now_str())
    runner.result_item = create_result_info_by_item(runner.result_item)
    answer, chain = runner.simple_search(query)
    return answer, chain


class CauseTreeSearchRunner():
    '''不需要重复使用，所以就不存数据库了'''
    TYPE = 'aggr_recall_placeholder'

    def __init__(self, task_id: str) -> None:
        self.coe_list = []
        task, _id_task = search_task(task_id)
        coes = task.choosed_coe_list
        self.coe_ids = [coe.coe_id for coe in coes]
        self.task_id = task_id
        self._id_task = _id_task
        self.task = task
        id = str(uuid.uuid1().int)
        self.result_item = COEResult(task_id=[task_id], coe_id=id, type=self.TYPE,
                                     id=id, brief='', occur_time=get_now_str())
        # self.result_item = create_result_info_by_item(self.result_item)
        cached_runner = CauseSearchSimpleRunner(coe_ids=self.coe_ids, task_id=task_id, threshold=0)
        self.cached_runner = cached_runner
        result_items = cached_runner.history_result_items
        exp_ids = []
        for result_item in result_items:
            exp_ids.extend([i.exp_id for i in result_item.answer_message])
        answer_message, ans_dict = batch_find_experience(exp_ids)
        cached_runner.cached_exps.update(ans_dict)

    def prepare_node(self, node, coe_ids=None):
        query = node['label']
        if coe_ids is None:
            coe_ids = self.coe_ids
        answer, chain = get_simple_cause_search_with_history(query=query, task_id=self.task_id,
                                                             threshold=0, coe_ids=coe_ids,
                                                             cached_runner=self.cached_runner)
        return answer, chain, query

    def make_result(self, score_list: List[Dict]):
        exps = []
        # for ind, item in enumerate(score_list):
        #     coe: COEStoreageData = item['coe']
        #     score: str = item['score']
        #     is_related = item['is_related']
        #     text: str = item['text']
        #     q_dict = {'coe_id': coe.coe_id, 'brief': coe.brief, 'text': text, 'index': ind,
        #               'query': item['query']}
        #     a_dict = {'score': score, 'is_related': is_related, 'parent_list': item['parent_list']}
        #     a_dict.update(q_dict)
        #     q = json.dumps(q_dict, ensure_ascii=False)
        #     a = json.dumps(a_dict, ensure_ascii=False)
        #     message = [
        #         MetaMessage('user', q),
        #         MetaMessage('assistant', a)
        #     ]
        #     exp_id = str(uuid.uuid1().int)
        #     exp = Experience(
        #         task_id=self.task_id,
        #         coe_id=str(uuid.uuid1().int),
        #         type=self.result_item.type,
        #         data=message,
        #         id=exp_id,
        #         search_text=coe.brief
        #     )
        #     exps.append(exp)
        # bulk_create_exp_by_object(exps=exps)
        return exps

    def done(self, exp_list: List[Experience]):
        desc = f'下钻 - {get_now_str()}'
        self.result_item.brief = desc
        self.result_item.error = None
        self.result_item.is_done = True
        # time.sleep(1)
        if self.TYPE not in self.task.sub_task_type_list:
            self.task.sub_task_type_list.append(self.TYPE)
            # update_task(self.task, self._id_task)
        self.result_item.answer_message = [Answer(exp_id=exp.id) for exp in exp_list]
        # update_chain_result(self.result_item)

    def decode_aggr_to_tree(self):
        chain, _id = search_coe_result_item(coe_id=DEFAULT_AGGR_COEID_PLACEHOLDER,
                                            type='aggr_simple', task_id=self.task_id)
        answer_message, _ = batch_find_experience([i.exp_id for i in chain.answer_message])
        text = get_result_to_show(chain, answer_message[0])
        self.result_item.reason = text
        return decode_aggr_to_tree(text)

    def bfs_search(self):
        '''通过bfs遍历每一个节点'''
        rootList = self.decode_aggr_to_tree()
        result = {}
        queue = deque([(node, 0) for node in rootList])
        max_level = 0
        while queue:
            node, level = queue.popleft()
            if level > max_level:
                max_level = level
            if int(level) not in result:
                result[int(level)] = []
            result[int(level)].append(node)
            children = node.get("children", [])
            for child in children:
                queue.append((child, level + 1))
        return result, max_level, rootList

    def tree_search(self):
        result, max_level, rootList = self.bfs_search()
        node_list = result[max_level-1]
        results = {}
        for node in node_list:
            answer, chain, query = self.prepare_node(node)
            parents = find_parents(node)
            parents = [node['label'] for node in parents]
            for item in answer:
                coe: COEStoreageData = item['coe']
                score = item['score']
                item['query'] = query
                item['parent_list'] = parents
                coe_id = str(coe.coe_id)
                if coe_id not in results:
                    results[coe_id] = item
                elif results[coe_id]['score'] < score:
                    results[coe_id] = item
        items = []
        for coe_id, item in results.items():
            items.append(item)
        exps = self.make_result(items)
        for node in node_list:
            if 'coes' not in node:
                node['coes'] = []
            for item in items:
                if node['label'] in item['query']:
                    node['coes'].append({"coe_id": item['coe'].coe_id,
                                         "brief": item['coe'].brief})
            del node['children']
            for p in find_parents(node):
                if 'value' not in p:
                    p['value'] = 0
                if 'rate' not in p:
                    p['rate'] = 0
                p['value'] += len(node['coes'])
                p['rate'] += len(node['coes'])/len(results)*100
        for level, nodes in result.items():
            for node in nodes:
                node['name'] = node['label']
                del node['parent']
        self.done(exp_list=exps)
        return items, self.result_item, rootList


if __name__ == '__main__':
    search_runner = CauseTreeSearchRunner(task_id='255835733938051764877617239564342006050')
    items, result_item, rootList = search_runner.tree_search()
    print(rootList)
