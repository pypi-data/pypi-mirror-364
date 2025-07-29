from typing import List, Tuple
from service.coe_analysis.coe_experience_service import find_experience
from service.coe_analysis.config_reader import COE_ACCESS_HEADER, COE_API_HOST
from service.coe_analysis.llm_sdk_importer import COE_SYNC_DATA, TASK_TYPES, es_util, COE_ANALYSIS_DETAIL
from service.coe_analysis.crawler.getDoc import get_template, getCoeJson, get_6to2notto
from service.coe_analysis.data_structure import COEStoreageData, Experience, MutiTag, Tag, FundTag, COEResult
import json
from service.coe_analysis.result_analysis import get_result_to_show
from utils import logger, timestring_to_TZ
import requests
from service.lang_chain_utils.embedding import embed
import time
from service.coe_analysis.crawler.getDoc import CATEGORY_DICT


def search_coe_result_item_list(coe_id=None, type=None, task_id=None):
    '''会按照edit_time倒序排序'''
    inner = []
    if coe_id:
        inner.append({"term": {"coe_id": coe_id}})
    if type:
        inner.append({"term": {"type": type}})
    if task_id:
        inner.append({"term": {"task_id": task_id}})
    query_josn = {
        "query": {"bool": {"must": inner}},
        "sort": [{"edit_time": {"order": "desc"}}],
        "size": 20
    }
    answer = es_util.search(index=COE_ANALYSIS_DETAIL, query=query_josn)
    coe_result_items = [COEResult.from_es(i) for i in answer]
    _ids = [i['_id'] for i in answer]
    return coe_result_items, _ids


def _tree_find_node(children, target_value):
    '''
    children结构是外层list，内层children,label,value
    返回值是list里的某一个元素
    '''
    if children is None:
        return
    # 遍历树的每个节点
    for node in children:
        # 如果当前节点的值等于目标值，则返回该节点
        if str(node['value']) == str(target_value):
            return node
        # 如果当前节点有子节点，则递归调用find_node函数在子节点中查找目标值
        if 'children' in node:
            result = _tree_find_node(node['children'], target_value)
            # 如果在子节点中找到了目标值，则返回结果
            if result is not None:
                return result
    # 如果在整个树中都没有找到目标值，则返回None
    return None


def _tree_get_all_values(node):
    if node is None:
        return []
    values = [str(node['value'])]
    if 'children' in node:
        for child in node['children']:
            values.extend(_tree_get_all_values(child))
    return values


def extend_ref_orgs(orgs: List[str]):
    url = f'{COE_API_HOST}/orgs?category=tree'
    res = requests.get(url=url, timeout=25, headers=COE_ACCESS_HEADER)
    responseReportJson = json.loads(res.content)
    root_children = responseReportJson['orgs']
    values = []
    for org in orgs:
        node = _tree_find_node(root_children, org)
        values.extend(_tree_get_all_values(node))
    return values


def list_coe(
        create_begin, create_end, size, _from, orgs=None, levels: List[str] = None, template_ids: List[str] = None,
        brief_search=None, cause_search=None, experience_search=None, filterfund=False, is_exclude_deleted=True,
        filter6to2not: List[str] = False, other_must_inner=[], filter6to2not_reviewed=None,
        is_exclude_light_template=False, diff6to2not=False, *arg, **kargs) -> Tuple[List[COEStoreageData], int]:
    must_inner = [
        {"range": {"create_at.date":  {"gte": create_begin, "lte": create_end}}},
        *other_must_inner
    ]
    mustnot_inner = []
    should_inner = []
    sort = [{"create_at.date": {"order": "desc"}}]
    if is_exclude_light_template:
        mustnot_inner.append({"term": {"coe_template_id": 30}})

    if template_ids:
        if '无模板' not in template_ids:
            must_inner.append({"terms": {"coe_template_id": template_ids}})
        else:
            _should_inner = []
            for template_id in template_ids:
                if template_id != '无模板' and template_id is not None:
                    _should_inner.append({"term": {"coe_template_id": template_id}})
                elif template_id == '无模板':
                    _should_inner.append({"bool": {"must_not": [{"exists": {"field": "coe_template_id"}}]}})
            must_inner.append({"bool": {"should": _should_inner}})
    if orgs:
        extended_orgs = extend_ref_orgs(orgs=orgs)
        must_inner.append({"terms": {"org_id.keyword": extended_orgs}})
    if levels:
        if '未定级' not in levels:
            must_inner.append({"terms": {"level.keyword": levels}})
        else:
            _should_inner = []
            for level in levels:
                if level != '未定级' and level is not None:
                    _should_inner.append({"term": {"level": level}})
                elif level == '未定级':
                    _should_inner.append({"bool": {"must_not": [{"exists": {"field": "level"}}]}})
            must_inner.append({"bool": {"should": _should_inner}})
    # 或者不存在 is_deleted，或者 is_deleted = false
    if is_exclude_deleted:
        must_inner.append({
            "bool": {"should": [
                {"bool": {"must_not": [{"exists": {"field": "is_deleted"}}]}},
                {"bool": {"must": [{"term": {"is_deleted": False}}]}}
            ]}
        })
    # 或逻辑应该是在且逻辑之内，先且后或
    if filterfund:
        should_inner.append({"terms": {"fund_safety.is_fund_danger.analysis_result.keyword": [
            "是", "缺少内容无法确认，倾向于认为有资金安全风险", '否', '虽无明确金额损失或者财务差异, 但是建议关注其资金风险情况'
        ]}})
    if diff6to2not:
        _tmp_should_inner = []
        for type in ['to_test', 'to_claim', 'to_check', 'to_grey', 'to_inspect',
                     'to_rollback', 'not_to_delay', 'not_to_illagle_change_data']:
            _tmp_should_inner.append({"bool": {"must": [
                {"terms": {f"{type}.analysis_result.keyword": ["没违反", "不违反", "不涉及", "否"]}},
                {"terms": {f"{type}.analysis_result_raw.keyword": ["违反", "无法确定", "涉及"]}}
            ]}})
        must_inner.append({'bool': {'should': _tmp_should_inner}})
    if filter6to2not:
        for type in ['to_test', 'to_claim', 'to_check', 'to_grey', 'to_inspect',
                     'to_rollback', 'not_to_delay', 'not_to_illagle_change_data']:
            if type not in filter6to2not:
                continue
            should_inner.append({"terms": {f"{type}.analysis_result_raw.keyword": ["违反", "无法确定"]}})
            should_inner.append({"terms": {f"{type}.rd_result.keyword": ["违反", "无法确定", "涉及"]}})
    if filter6to2not_reviewed:
        for type in ['to_test', 'to_claim', 'to_check', 'to_grey', 'to_inspect',
                     'to_rollback', 'not_to_delay', 'not_to_illagle_change_data']:
            if type not in filter6to2not_reviewed:
                continue
            should_inner.append({"terms": {f"{type}.analysis_result.keyword": ["违反", "无法确定", "涉及"]}})

    must_inner.append({'bool': {'should': should_inner}})
    # 组装embedding
    body = None
    if brief_search or cause_search or experience_search:
        if brief_search:
            field = 'brief_embedding'
            query_vector = embed.embed_query(brief_search)
        elif cause_search:
            field = 'cause_embedding'
            query_vector = embed.embed_query(cause_search)
        elif experience_search:
            field = 'experience_embedding'
            query_vector = embed.embed_query(experience_search)
        must_inner.append({"exists": {"field": field}})
        script = {
            "source": f"cosineSimilarity(params.query_vector, '{field}') + 1.0",
            "params": {"query_vector": query_vector},
        }
        body = {
            "query": {
                "script_score": {
                    "query": {"bool": {"must": must_inner, "must_not": mustnot_inner}},
                    "script": script
                }
            },
            "from": _from,
            "size": size
        }
    else:
        body = {
            "query": {"bool": {
                "must": must_inner,
                "must_not": mustnot_inner
            }},
            "from": _from,
            "size": size,
            "sort": sort
        }

    res = es_util.search_with_total(index=COE_SYNC_DATA, query=body)
    hits = res['hits']
    hits = [COEStoreageData.from_es(hit) for hit in hits]
    total = res['total']
    return hits, total


def search_coe(coe_id) -> Tuple[COEStoreageData, str]:
    try:
        query_josn = {
            "_source": {"excludes": ['brief_embedding', 'cause_embedding',
                                     'content_embedding', 'experience_embedding']},
            "query": {"bool": {"must": [
                {"match": {"coe_id": coe_id}},
            ]}}
        }
        answer = es_util.search(index=COE_SYNC_DATA, query=query_josn)
        item = COEStoreageData.from_es(answer[0])
        _id = answer[0]['_id']
        return item, _id
    except Exception:
        return None, None


def batch_search_coe_storage(coe_ids: List[str], size: int = 1000) -> Tuple[List[COEStoreageData], List[str]]:
    try:
        query_josn = {
            "_source": {"excludes": ['brief_embedding', 'cause_embedding', 'content_embedding',
                                     'experience_embedding', 'all_tags_as_string']},
            "query": {"bool": {"must": [
                {"terms": {"coe_id": coe_ids}}
            ]}},
            "size": size
        }
        answer = es_util.search(index=COE_SYNC_DATA, query=query_josn)
        items = [COEStoreageData.from_es(i) for i in answer]
        _ids = [i['_id'] for i in answer]
        return items, _ids
    except Exception:
        return None, None


def mole_first_level_tag_compute(category: str):
    ans = '后台&系统通道'
    if category in ['大数据事故']:
        ans = '大数据&算法通道'
    elif category in ['大前端故障']:
        ans = '前台通道'
    return ans


def get_tag_instance(coe_id):
    try:
        tag_json = getCoeJson('custom', coe_id)
        item = {}
        instances = {}
        for instance in tag_json['custom']['instances']:
            key = instance['custom_template']['label']
            value = instance['value']
            item[key] = value
            instances[key] = instance
        return item, instances
    except Exception:
        logger.info(f'coe-{coe_id},没有分类信息')
        return {}, {}


# 暂时不同步COE内容
def sync_once(coe_id: str):
    '''在此处注册写入的字段'''
    incident: dict = getCoeJson('', coe_id)['incident']
    tags, tag_instances = get_tag_instance(coe_id)
    try:
        tonotto = get_6to2notto(coe_id)
    except Exception:
        tonotto = []
    # logger.info('获取brief_embedding')
    # brief_embedding = embed.embed_query(incident['brief'])
    brief_embedding = None
    template, template_id = get_template(coe_id)
    category = incident.get('category', '')
    category = CATEGORY_DICT.get(category, category)

    coe = COEStoreageData(
        coe_id=coe_id,
        level=incident['level'],
        brief=incident['brief'],
        org_id=str(incident['org_id']),
        org_path=incident['org_path'],
        create_at=timestring_to_TZ(incident['create_at']),
        create_by=incident['create_by'],
        update_at=timestring_to_TZ(incident['update_at']),
        coe_template_id=template_id,
        coe_template_name=template,
        all_tags_as_string=json.dumps(tags),
        brief_embedding=brief_embedding,
        category=category
    )
    # if 'experience' in incident and isinstance(incident['experience'], str) and len(incident['experience']) != 0:
    #     logger.info('experience_embedding')
    #     experience = incident['experience']
    #     experience_embedding = embed.embed_query(experience)
    #     coe.experience = experience
    #     coe.experience_embedding = experience_embedding
    for type in ['to_test', 'to_claim', 'to_check', 'to_grey', 'to_rollback', 'to_inspect',
                 'not_to_illagle_change_data', 'not_to_delay']:
        coe.__setattr__(type, Tag(type=type, rd_result=None, rd_reason='None'))
    for phase, judge, desc in tonotto:
        if phase == '要测试':
            coe.to_test = Tag(type='to_test', rd_result=judge, rd_reason=str(desc))
        elif phase == '要周知':
            coe.to_claim = Tag(type='to_claim', rd_result=judge, rd_reason=str(desc))
        elif phase == '要审核':
            coe.to_check = Tag(type='to_check', rd_result=judge, rd_reason=str(desc))
        elif phase == '要灰度':
            coe.to_grey = Tag(type='to_grey', rd_result=judge, rd_reason=str(desc))
        elif phase == '要可回滚':
            coe.to_rollback = Tag(type='to_rollback', rd_result=judge, rd_reason=str(desc))
        elif phase == '要观测':
            coe.to_inspect = Tag(type='to_inspect', rd_result=judge, rd_reason=str(desc))
        elif phase == '不要违规变更数据':
            coe.not_to_illagle_change_data = Tag(type='not_to_illagle_change_data',
                                                 rd_result=judge, rd_reason=str(desc))
        elif phase in ['不要瞒报故障', '不要延报故障']:
            coe.not_to_delay = Tag(type='not_to_delay', rd_result=judge, rd_reason=str(desc))
    # 线上问题原因分类
    trigger_fill_accepted = tag_instances.get('线上问题原因分类', {}).get('trigger_fill_accepted', None)
    coe.cause_analysis = Tag(type='cause_analysis', rd_result=tags.get('线上问题原因分类', 'None'),
                             trigger_fill_accepted=trigger_fill_accepted)
    coe.fund_safety = FundTag(
        type='fund_tag',
        deal_loss_amount=tags.get('订单损失量', ''),
        involved_amount=tags.get('涉及金额（元）', ''),
        actual_loss_amount=tags.get('实际资损金额（元）', ''),
        financial_diff_amount=tags.get('财务差异金额（元）', ''),
        mole_first_level_tag=mole_first_level_tag_compute(category)
    )
    coe.trigger_method = Tag(type='trigger_condition', rd_result=tags.get('线上问题触发条件', 'None'))
    try:
        # 更新COE
        logger.info(f'更新COE: {coe_id}')
        coe_old, _id = search_coe(coe_id)
        body = {
            "doc": coe.to_json_dict()
        }
        es_util.update(index=COE_SYNC_DATA, id=_id, body=body)
    except Exception as e:
        logger.warn(f'新建COE: {coe_id}\n{e.args}')
        es_util.index(index=COE_SYNC_DATA, id=coe_id, body=coe.to_json_dict())


def _get_result_(result_item: COEResult, k=0):
    try:
        if len(result_item.answer_message) <= k:
            return None
        first_saved_exp_id = result_item.answer_message[k].exp_id
        exp, _ = find_experience(first_saved_exp_id)
        result_to_show = get_result_to_show(result_item=result_item, first_saved_exp=exp)
        return result_to_show
    except Exception:
        return None


def _get_raw_result_(result_item: COEResult, k=0):
    try:
        messages = result_item.message
        ms = []
        for i in messages:
            if '[S9校验]' in i.content:
                ms = [i]
                break
            ms.append(i)
        exp = Experience(data=ms, task_id=result_item.task_id,
                         coe_id=result_item.coe_id, type=result_item.type)
        result_to_show = get_result_to_show(result_item=result_item, first_saved_exp=exp)
        return result_to_show
    except Exception:
        return None


def _get_muti_results(result_item: COEResult):
    try:
        result_to_show_list = []
        for ans in result_item.answer_message:
            exp_id = ans.exp_id
            exp, _ = find_experience(exp_id)
            result_to_show = get_result_to_show(result_item=result_item, first_saved_exp=exp)
            result_to_show_list.append(result_to_show)
        return result_to_show_list
    except Exception:
        return None


def get_coe_result_(coe_store_data: COEStoreageData, coe_id: str, type: str, task_id: str = None):
    '''在此处注册同步的字段'''
    if task_id:
        # 如果传入了task_id，就是指定了某个task的结果为应有结果
        result_list, _ids = search_coe_result_item_list(coe_id=coe_id, type=type, task_id=task_id)
    else:
        result_list, _ids = search_coe_result_item_list(coe_id=coe_id, type=type)
    if len(result_list) == 0:
        return coe_store_data
    ref_result = result_list[0]  # 最新的一个
    for result in result_list[::-1]:
        ans = _get_result_(result)
        if result.is_done and ans is not None:
            ref_result = result

    for result in result_list:  # reviewed 过的优先，取最新review的
        if result.is_reviewed:
            ref_result = result
    # 分发到字段
    if type in ['to_test', 'to_claim', 'to_check', 'to_grey', 'to_inspect',
                'to_rollback', 'not_to_delay', 'not_to_illagle_change_data']:
        tag = getattr(coe_store_data, type)
        tag.analysis_result_id = ref_result.id
        tag.analysis_result = _get_result_(ref_result)
        tag.update_time = ref_result.edit_time
        tag.analysis_task_id = ref_result.task_id
        tag.analysis_result_raw = _get_raw_result_(ref_result)
    elif type == 'fund_judgement':
        coe_store_data.fund_safety.is_fund_danger = Tag(
            type='fund_judgement',
            analysis_task_id=ref_result.task_id,
            analysis_result=_get_result_(ref_result),
            analysis_result_id=ref_result.id,
            update_time=ref_result.edit_time,
            analysis_result_raw=_get_raw_result_(ref_result)
        )
    elif type == 'cause':
        if coe_store_data.cause_analysis is None:
            res = _get_result_(ref_result)
            if res != '无法判断':
                coe_store_data.cause_analysis = Tag(
                    type='cause',
                    analysis_result_id=ref_result.id,
                    analysis_result=res,
                    update_time=ref_result.edit_time,
                    analysis_task_id=ref_result.task_id,
                    analysis_result_raw=_get_raw_result_(ref_result)
                )
        coe_store_data.cause_analysis.analysis_result_id = ref_result.id
        coe_store_data.cause_analysis.analysis_result = _get_result_(ref_result)
        coe_store_data.cause_embedding = ref_result.search_vector
        coe_store_data.cause_analysis.update_time = ref_result.edit_time
        coe_store_data.cause_analysis.analysis_task_id = ref_result.task_id
    elif type == 'fund_aggr_classify':
        coe_store_data.fund_safety.fund_aggr_classify = MutiTag(
            type='fund_judgement',
            analysis_task_id=ref_result.task_id,
            analysis_result=_get_muti_results(ref_result),
            analysis_result_id=ref_result.id,
            update_time=ref_result.edit_time
        )
    return coe_store_data


def sync_coe_result(coe_id: str, type: str, task_id: str = None):
    coe_store_data, _id = search_coe(coe_id)
    coe_store_data = get_coe_result_(coe_store_data, coe_id, type, task_id)
    # 存入
    body = {
        "doc": coe_store_data.to_json_dict()
    }
    es_util.update(index=COE_SYNC_DATA, id=_id, body=body)


def batch_sync_coe_result(coe_id_list: list, type_list: list):
    for coe_id in coe_id_list:
        try:
            coe_store_data, _id = search_coe(coe_id)
            coe_store_data.coe_id = str(coe_store_data.coe_id)
            for type in type_list:
                logger.info(f'开始同步 coeid={coe_id} type={type} 的结果')
                coe_store_data = get_coe_result_(coe_store_data, coe_id, type)
            body = {
                "doc": coe_store_data.to_json_dict()
            }
            es_util.update(index=COE_SYNC_DATA, id=_id, body=body)
        except Exception as e:
            logger.exception(f'同步 {coe_id} 的结果失败' + str(e))


def batch_sync_coe_storage(coe_id_list: List[str], type_list=None):
    for coe_id in coe_id_list:
        try:
            logger.info(f'开始同步 {coe_id}')
            sync_once(coe_id)
        except Exception as e:
            logger.exception(f'{coe_id}同步失败' + str(e))
    time.sleep(1)
    if type_list is None:
        type_list = [i['type'] for i in TASK_TYPES]
    batch_sync_coe_result(coe_id_list=coe_id_list, type_list=type_list)


if __name__ == '__main__':
    # res, _ = list_coe(create_begin='2023-12-01', create_end='2024-02-01', size=10000, _from=0)
    type_list = ['to_test', 'to_claim', 'to_check', 'to_grey', 'to_inspect',
                 'to_rollback', 'not_to_delay', 'not_to_illagle_change_data',
                 'fund_aggr_classify', 'cause', 'fund_judgement']
    # coe_ids = [coe.coe_id for coe in res]
    batch_sync_coe_storage(['267479', '267465'])
