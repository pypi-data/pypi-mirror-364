from service.coe_analysis.crawler.getDoc import getCoeAsItemDict, getCoeJson, getLatestId
from service.coe_analysis.coe_store_service import sync_once
from service.coe_analysis.crawler_data_service import sync_crawler_data
import time
from utils import logger
import json
from service.lang_chain_utils.lion_client import client as lion
from service.coe_analysis.llm_sdk_importer import COE_SYNC_DATA
from service.coe_analysis.llm_sdk_importer import es_util
from service.coe_analysis.coe_store_service import search_coe, list_coe


def get_deleted(create_start, create_end):
    # 获取可能是最近删除的COE
    coe_ids, coe_item_dict = getCoeAsItemDict(create_start=create_start, create_end=create_end, level='')
    already_in_codes, _ = list_coe(create_begin=create_start, create_end=create_end, size=1000, _from=0)
    deleted = []
    for coe in already_in_codes:
        coe_id = coe.coe_id
        if coe_id not in coe_item_dict:
            deleted.append(coe_id)

    answer = []
    for coe_id in deleted:
        try:
            history = getCoeJson('history', coe_id)
            history = history['history']
            delete_flg = False
            for h in history:
                if h.get('new', '') == "已删除":
                    delete_flg = True
                    break
            if delete_flg:
                answer.append(coe_id)
        except Exception as e:
            logger.exception(f"无法获取 {coe_id}" + str(e))

    return answer


def mark_delete_once(coe_id):
    coe_store_data, _id = search_coe(coe_id)
    coe_store_data.is_deleted = True
    # 存入
    body = {
        "doc": coe_store_data.to_json_dict()
    }
    es_util.update(index=COE_SYNC_DATA, id=_id, body=body)


def mark_deleted():
    time_stamp = time.time()
    lion.fetch_config()
    delay_conf = json.loads(lion.config.get(f'{lion.app_name}.coe.sync_data_delay_day'))
    create_start = int(time_stamp - 86400*delay_conf['create_start'])  # 拉10天的COE，其中昨天有修改的都要重新算
    create_end = time.strftime("%Y-%m-%d", time.localtime(time_stamp))
    create_start = time.strftime("%Y-%m-%d", time.localtime(create_start))
    ids = get_deleted(create_start=create_start, create_end=create_end)
    for id in ids:
        mark_delete_once(coe_id=id)


def coe_sync_auto():
    time_stamp = time.time()
    lion.fetch_config()
    delay_conf = json.loads(lion.config.get(f'{lion.app_name}.coe.sync_data_delay_day'))
    tenday_stamp = int(time_stamp - 86400*delay_conf['create_start'])  # 拉10天的COE，其中昨天有修改的都要重新算
    yesterday_stamp = int(time_stamp - 86400*delay_conf['update_start'])
    now = time.strftime("%Y-%m-%d", time.localtime(time_stamp))
    yesterday = time.strftime("%Y-%m-%d", time.localtime(yesterday_stamp))
    tenday = time.strftime("%Y-%m-%d", time.localtime(tenday_stamp))
    logger.info(f'coe同步任务开始，搜寻 {yesterday} ~ {now} 存在更新的 coe')
    coe_ids, coe_item_dict = getLatestId(update_start=yesterday, create_start=tenday,
                                         create_end=now, level='')
    for coe_id in coe_ids:
        try:
            sync_once(coe_id)
        except Exception as e:
            logger.exception(f'{coe_id}同步失败' + str(e))
    logger.info(f'同步 {coe_ids} 完成 len={len(coe_ids)}')
    logger.info('开始同步删除的 coe')
    ids = get_deleted(create_start=tenday, create_end=now)
    for coe_id in ids:
        try:
            mark_delete_once(coe_id)
        except Exception as e:
            logger.exception(f'{coe_id}同步失败' + str(e))
    logger.info(f'同步删除的 {ids} 完成')
    # logger.info('开始同步 crawler 内容')
    # for coe_id in coe_ids:
    #     try:
    #         sync_crawler_data(coe_id)
    #     except Exception as e:
    #         logger.exception(f'{coe_id} 同步失败' + str(e))
    # logger.info(f'crawler data 同步完成 {coe_ids}')


if __name__ == '__main__':
    # 定时任务执行方法
    # cd /opt/meituan/tool/compatibility; PYTHONPATH=. ES_ENV=default Env=test
    # venv/bin/python crane/coe_sync_task.py
    # > /data/applogs/inf/com.sankuai.toolchain.coverage.agent/crane-coe_sync_task.log 2>&1
    coe_sync_auto()
