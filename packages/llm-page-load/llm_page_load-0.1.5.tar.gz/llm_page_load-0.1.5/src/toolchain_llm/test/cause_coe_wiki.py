import json
from typing import Dict, List
from service.coe_analysis.coe_chain_service import \
    bulk_create_result_info, search_task, update_chain_result, update_task, run_chain_serial, \
    run_chain_once, post_xgpt_agent_dict, post_new_open_session, post_open_chat, run_chain
from flask import Blueprint

from service.coe_analysis.coe_result_to_wiki import merge_agent_answer, remove_str
from service.coe_analysis.coe_store_service import batch_search_coe_storage, get_tag_instance, list_coe, search_coe, search_coe_result_item_list, sync_coe_result, batch_sync_coe_storage, sync_once  # noqa
from service.coe_analysis.coe_task_service import create_task
from service.coe_analysis.crawler.getDoc import getCoeJson
from service.coe_analysis.data_structure import BaseCoeData, COEResult, ChangeLog, Experience, AutoFillRequest, Tag  # noqa
from service.coe_analysis.config_reader import get_config, get_kms
from service.coe_analysis.llm_sdk_importer import COE_SYNC_DATA, RESULT_FILTER_WHITE_LIST, TASK_TYPES, NameSpace, es_util  # noqa
from service.coe_analysis.search_coe_result_item import search_all_chain

coe = Blueprint(NameSpace, __name__)


token = get_kms('COE_ACCESS_TOKEN')   # 到店申请的token
# token = get_config('token')
# youxuan_token = get_config('youxuan_token')   # 优选申请的token
agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_0_0) " +\
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36"

headers = {
    "Authorization": "Bearer %s" % token,
    "User-Agent": agent,
}

COE_API_HOST = get_config('COE_API_HOST')


if __name__ == '__main__':

    '''
    获取COE信息调试
    '''
    # coe_info = getCoeJson('', "83413")
    # A = coe_info.get('incident').org_path
    # {'cause_analysis', 'debt_label', 'todo_analysis','monitor_online_analysis','risk_assistant_analysis'}
    '''
    COE输出wiki
    '''
    # COE输出wiki
    # run_chain_serial([], ['cause_analysis', 'debt_label', 'todo_analysis'], 250521731503323266238912013406500430058, 'wangyan229',"到店业务平台研发部COE 列表（2025年5月）wiki")

    '''
    执行单个分析任务测试
    '''
    res = run_chain_once(279325, "new_analysis", 114781689069347553150278765823577432298)
    print(res.result_item.message[3])
    '''
    批量执行分析任务测试
    '''
    # result_list, _ = search_all_chain(321981630678892553049504743320804532458)
    # # i=0
    # for item in result_list:
    #   coe_id = item.coe_id
    #   # if len(item.message)>3:
    #   if item.type == "debt_label":
    #      res = run_chain_once(coe_id, "debt_label", 321981630678892553049504743320804532458)
    #      print(coe_id)
    '''
    创建任务调试
    '''
  #   task_id = create_task(
  #       [
  # {
  #   "_from": "km_auto",
  #   "_id": 50569,
  #   "appearance": "",
  #   "appkey": "com.sankuai.hotel.cbs.priceapi",
  #   "brief": "生单页报价服务升级导致未扣商家自促库存casestudy",
  #   "category": "backend",
  #   "clear_time": "2019-03-21 21:07:00",
  #   "cminuso_time": 1938,
  #   "create_at": "2019-04-17 08:13:46",
  #   "custom_fields": [
  #     {
  #       "label": "线上问题发现方式",
  #       "template_id": 302,
  #     },
  #     {
  #       "label": "线上问题原因分类",
  #       "template_id": 680,
  #     },
  #     {
  #       "label": "线上问题触发条件",
  #       "template_id": 1475,
  #     },
  #     {
  #       "label": "线上问题逃逸原因",
  #       "template_id": 1727,
  #     },
  #     {
  #       "label": "业务线",
  #       "template_id": 603,
  #     },
  #     {
  #       "label": "订单损失量",
  #       "template_id": 610,
  #     },
  #     {
  #       "label": "损失支付间夜/门票消费券",
  #       "template_id": 301,
  #     },
  #     {
  #       "label": "涉及金额（元）",
  #       "template_id": 617,
  #     },
  #     {
  #       "label": "实际资损金额（元）",
  #       "template_id": 1615,
  #     },
  #     {
  #       "label": "财务差异金额（元）",
  #       "template_id": 1622,
  #     },
  #     {
  #       "label": "前期测试未发现原因",
  #       "template_id": 687,
  #     },
  #     {
  #       "label": "是否影响数仓",
  #       "template_id": 887,
  #     },
  #     {
  #       "label": "违反安全生产准则",
  #       "template_id": 1370,
  #     },
  #     {
  #       "label": "测试阶段未发现原因",
  #       "template_id": 1888,
  #     },
  #     {
  #       "label": "灰度阶段未发现原因",
  #       "template_id": 1895,
  #     },
  #     {
  #       "label": "线上监控未发现原因",
  #       "template_id": 1902,
  #     },
  #     {
  #       "label": "归属技术栈",
  #       "template_id": 1930,
  #     },
  #     {
  #       "label": "业务线",
  #       "template_id": 3541,
  #     },
  #     {
  #       "label": "原因下钻",
  #       "template_id": 4475,
  #     },
  #     {
  #       "label": "二级标签",
  #       "template_id": 4862,
  #     },
  #     {
  #       "label": "测试最佳可发现手段",
  #       "template_id": 3520,
  #     },
  #     {
  #       "label": "研发阶段未发现原因",
  #       "template_id": 3534,
  #     },
  #     {
  #       "label": "变更来源系统",
  #       "template_id": 3513,
  #     }
  #   ],
  #   "department": "meituan.hotel",
  #   "done_todo": 1,
  #   "editor_version": "",
  #   "external_org_id": 105435,
  #   "find_detail": {
  #     "business_alarm": 0,
  #     "business_alarm_delay": 0,
  #     "cs_alarm": 0,
  #     "cs_alarm_delay": 0
  #   },
  #   "find_time": "2019-03-21 18:40:00",
  #   "finders": [
  #     "研发人员-PM"
  #   ],
  #   "fminuso_time": 1791,
  #   "handle_time": "2019-03-21 18:41:00",
  #   "handler": [
  #     "liuchao30"
  #   ],
  #   "hminusf_time": 1,
  #   "hminusn_time": 1,
  #   "improvement_orgs": [
  #     {
  #       "_id": 254501,
  #       "head_mis": "shang.gao",
  #       "head_name": "高尚",
  #       "name": "供给优化组",
  #       "org_id": 40013558,
  #       "parent_id": 53207,
  #       "path": "美团/核心本地商业/业务研发平台/酒店旅行技术部/供给优化组"
  #     }
  #   ],
  #   "level": "S4",
  #   "level_comment": "超卖影响订单数: 2463单, 整体订单量无损失",
  #   "level_person": "huguochao",
  #   "level_standard": {},
  #   "level_standard_id": 0,
  #   "level_time": "2019-04-19 11:12:05",
  #   "lminusf_time": 143,
  #   "location_detail": {
  #     "contain_bad_service": 0,
  #     "core_link": "",
  #     "red_dashboard": 0
  #   },
  #   "location_time": "2019-03-21 21:03:00",
  #   "locators": [
  #     "研发定位-业务RD"
  #   ],
  #   "major_type": "业务逻辑",
  #   "minor_type": "偶发BUG",
  #   "module": "住宿度假研发中心",
  #   "nminusf_time": 0,
  #   "notify_time": "2019-03-21 18:40:00",
  #   "occur_time": "2019-03-20 12:49:00",
  #   "org_path": "美团/核心本地商业/业务研发平台/业务系统平台部/供应链商品平台/酒店组",
  #   "orgs": [
  #     {
  #       "_id": 15428,
  #       "head_mis": "chenshuo02",
  #       "head_name": "陈烁",
  #       "name": "酒店组",
  #       "org_id": 105435,
  #       "parent_id": 53221,
  #       "path": "美团/核心本地商业/业务研发平台/业务系统平台部/供应链商品平台/酒店组"
  #     }
  #   ],
  #   "owner": "liuchao30/刘超",
  #   "owners": [
  #     "liuchao30"
  #   ],
  #   "path": "美团/核心本地商业/业务研发平台/业务系统平台部/供应链商品平台/酒店组",
  #   "related_radar_ids": [],
  #   "responsible_orgs": [],
  #   "sminush_time": 146,
  #   "sminuso_time": 1938,
  #   "solved_time": "2019-03-21 21:07:00",
  #   "status": "TRACING",
  #   "team_leader": {
  #     "head_mis": "chenshuo02",
  #     "head_name": "陈烁"
  #   },
  #   "todo_status_count": {
  #     "DONE": 1
  #   },
  #   "total_todo": 1,
  #   "update_at": "2020-07-09 17:21:01",
  #   "wiki": "https://km.sankuai.com/page/47650214"
  # }
  #       ],"测试新类型1111","手动触发",["cause_analysis"],'wangyan229',True,[],'wangyan229' )
  #   print(task_id)