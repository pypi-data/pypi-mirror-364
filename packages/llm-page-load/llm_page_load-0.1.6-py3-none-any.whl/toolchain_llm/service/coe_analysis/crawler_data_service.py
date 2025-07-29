from typing import List
from service.coe_analysis.crawler.crawler_data import CrawlerData
from service.coe_analysis.crawler.getDoc import get_6to2notto, getBriefText, getCausesText, getTimeLineText
from service.coe_analysis.data_structure import COECrawlerData
from service.coe_analysis.llm_sdk_importer import COE_CRAWLER_DATA, es_util
from utils import get_now_str, logger


def find_crawler_data(coe_id, **karg):
    must_inner = [{"term": {"coe_id": coe_id}}]
    for k, v in karg.items():
        must_inner.append({"term": {k: v}})
    query = {
        "query": {"bool": {"must": must_inner}},
        "sort": [{"sync_time": {"order": "desc"}}],
        "size": 1000
    }
    answer = es_util.search(index=COE_CRAWLER_DATA, query=query)
    _ids = [i['_id'] for i in answer]
    items = [COECrawlerData.from_es(i) for i in answer]
    return items, _ids


def get_table(coe_id):
    table = get_6to2notto(coe_id)
    return table


def delete_passed(coe_id):
    query = {
        "query": {"bool": {"must": [
            {"term": {"coe_id": coe_id}}
        ]}},
        "sort": [{"sync_time": {"order": "desc"}}],
        "size": 1000
    }
    es_util.client.delete_by_query(index=COE_CRAWLER_DATA, body=query, headers=es_util.headers)
    es_util.refresh(COE_CRAWLER_DATA)


def dispatch_item_to_type(data: CrawlerData):
    type = []
    if data.desc in ['[时间线信息]', '[标题]', '[现象]', '[发生时间]', '[研发自证]', '[经验教训]']:
        return ["to_test", "to_claim", "to_check", "to_grey", "to_inspect", "to_rollback",
                "not_to_delay", "not_to_illagle_change_data"]
    elif data.desc in ['[原因分析信息]'] and data.category in ["分析测试流程", "分析规避方案", "分析故障发现", "分析Code Review流程", '分析故障根因']:
        type.append('to_test')
        if data.category in ["分析变更流程"]:
            type.append('to_claim')
        if data.category in ["其他", "分析变更流程"]:
            type.append('to_check')
        if data.category in ["其他", "分析测试流程", "分析故障定位", "分析处理流程"]:
            type.append('to_grey')
        if data.category in ["其他", "分析故障发现", "分析故障响应", "分析故障定位"]:
            type.append('to_inspect')
        if data.category in ["其他", "分析应急预案", "分析变更流程", "分析故障响应", "分析处理流程"]:
            type.append('to_rollback')
        if data.category in ["其他", "分析应急预案", "分析故障响应", "分析故障发现", "分析处理流程"]:
            type.append('not_to_delay')
        if data.category in ["分析故障根因", "分析变更流程", "分析故障响应", "分析处理流程", "分析故障定位", "分析故障发现"]:
            type.append('not_to_illagle_change_data')
    return type


def sync_crawler_data(coe_id):
    phase_dict = {
        "要测试": "to_test",
        "要周知": "to_claim",
        "要审核": "to_check",
        "要灰度": "to_grey",
        "要观测": "to_inspect",
        "要可回滚": "to_rollback",
        "不要延报故障": "not_to_delay",
        "不要瞒报故障": "not_to_delay",
        "不要违规变更数据": "not_to_illagle_change_data"
    }

    sync_time = get_now_str()
    logger.info('获取 briefText')
    briefText = getBriefText(coe_id)
    logger.info('获取 timeLineText')
    timeLineText = getTimeLineText(coe_id)
    logger.info('获取 causesText')
    causesText = getCausesText(coe_id)
    lst = briefText+timeLineText+causesText
    to_save: List[COECrawlerData] = []
    for item in lst:
        if item.desc not in ['[时间线信息]', '[标题]', '[现象]', '[发生时间]', '[研发自证]', '[经验教训]', '[原因分析信息]']:
            continue
        data = COECrawlerData.from_crawler_data(coe_id=coe_id, sync_time=sync_time,
                                                crawler_data=item, need_embedding=True)
        data.type = dispatch_item_to_type(item)
        logger.info(f'进行 embedding: {item.get_text()}')
        to_save.append(data)
    # 获取六要两不要的 table
    logger.info('获取 table')
    table = get_table(coe_id)
    if table is not None:
        for item in table:
            phase = item[0]
            tmp = item[2]['text'].strip()
            if len(tmp) == 0:
                continue
            txt = f'研发人员自我陈述:{tmp}\n是否违反{phase}原则:{item[1]}\n'
            lnk = item[2]['link']
            img = item[2]['image']
            if len(lnk) != 0:
                txt += f'相关链接:{lnk}\n'
            data = CrawlerData(
                data=txt,
                image_list=img,
                link_list=lnk,
                desc="[研发自证]",
            )
            if phase in phase_dict:
                type = [phase_dict[phase]]
            else:
                type = ["to_test", "to_claim", "to_check", "to_grey", "to_inspect", "to_rollback",
                        "not_to_delay", "not_to_illagle_change_data"]
            logger.info(f'进行 embedding: {txt}')
            data = COECrawlerData.from_crawler_data(coe_id=coe_id, sync_time=sync_time,
                                                    crawler_data=data, need_embedding=True)
            data.type = type
            to_save.append(data)
    bulk = []
    for item in to_save:
        bulk.append({"index": {"_index": COE_CRAWLER_DATA}})
        bulk.append(item.to_json_dict())
    answer = es_util.client.bulk(body=bulk, headers=es_util.headers)
    logger.info('bulk answer = %s', answer)
    es_util.refresh(COE_CRAWLER_DATA)


def dispatch_type(coe_id):
    query = {
        "query": {"bool": {"must": [
            {"term": {"coe_id": coe_id}}
        ]}},
        "sort": [{"sync_time": {"order": "desc"}}],
        "size": 10000
    }
    answers = es_util.search(index=COE_CRAWLER_DATA, query=query)
    datas = [COECrawlerData.from_es(i) for i in answers]
    ids_ = [i['_id'] for i in answers]
    for _id, data in zip(ids_, datas):
        if data.desc in ['[时间线信息]', '[标题]', '[现象]', '[发生时间]', '[研发自证]', '[经验教训]']:
            data.type = ["to_test", "to_claim", "to_check", "to_grey", "to_inspect", "to_rollback",
                         "not_to_delay", "not_to_illagle_change_data"]
        elif data.desc in ['[原因分析信息]']:
            data.type = []
            if data.category in ["分析测试流程", "分析规避方案", "分析故障发现", "分析Code Review流程", '分析故障根因']:
                data.type.append('to_test')
            if data.category in ["分析变更流程"]:
                data.type.append('to_claim')
            if data.category in ["其他", "分析变更流程"]:
                data.type.append('to_check')
            if data.category in ["其他", "分析测试流程", "分析故障定位", "分析处理流程"]:
                data.type.append('to_grey')
            if data.category in ["其他", "分析故障发现", "分析故障响应", "分析故障定位"]:
                data.type.append('to_inspect')
            if data.category in ["其他", "分析应急预案", "分析变更流程", "分析故障响应", "分析处理流程"]:
                data.type.append('to_rollback')
            if data.category in ["其他", "分析应急预案", "分析故障响应", "分析故障发现", "分析处理流程"]:
                data.type.append('not_to_delay')
            if data.category in ["分析故障根因", "分析变更流程", "分析故障响应", "分析处理流程", "分析故障定位", "分析故障发现"]:
                data.type.append('not_to_illagle_change_data')
        else:
            data.type = []
        body = {'doc': data.to_json_dict()}
        es_util.update(index=COE_CRAWLER_DATA, id=_id, body=body)
        es_util.refresh(COE_CRAWLER_DATA)
