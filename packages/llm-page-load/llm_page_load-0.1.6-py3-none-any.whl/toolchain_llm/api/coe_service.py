import datetime
from flask import jsonify, Response
from flask import request
from flask import Blueprint
from crane.cause_analysis import cause_analysis_task
from crane.coe_sync_task import coe_sync_auto
from crane.mole_tag_analysis import mole_tag_task, mole_tag_task_inner
from crane.tonotto_analysis_task import tnt_task
from service.coe_analysis.aggr_task_service import aggr_task_create
from service.coe_analysis.coe_store_service import batch_search_coe_storage, get_tag_instance, list_coe, search_coe, search_coe_result_item_list, sync_coe_result, batch_sync_coe_storage, sync_once  # noqa
from service.coe_analysis.coe_task_service import create_task, create_task_by_base_coe_data, create_task_sync, get_all_task, search_task
from service.coe_analysis.coe_chain_service \
    import batch_search_chain_by_id_with_experience_as_json, bulk_create_result_info, chain_result_get, run_chain, \
    chain_result_save
from service.coe_analysis.coe_experience_service \
    import experience_mark_update, get_experience, save_experience
from service.coe_analysis.coe_task_service \
    import get_single_task, rerun_task, topic_analysis
from service.coe_analysis.coe_thread_executor import coe_executor
from service.coe_analysis.crawler.getDoc import getLatestId, put_custom_instance
from service.coe_analysis.data_structure import BaseCoeData, COEResult, ChangeLog, Experience, AutoFillRequest, Tag  # noqa
from service.coe_analysis.crawler_data_service import sync_crawler_data, delete_passed
from service.coe_analysis.metrics_service \
    import compare_task_with_base_task, metrics_task
from service.coe_analysis.result_analysis import get_result_to_show
from service.coe_analysis.runners.cause import COESummaryRunner
from service.coe_analysis.runners.coe_cause_search import CauseTreeSearchRunner
from service.coe_analysis.search_coe_result_item import search_coe_result_item_with_experience
from utils import diff_time_string, get_now_str, logger
import requests
import re
import json
from time import time, sleep
from service.coe_analysis.config_reader import get_config, get_kms
import urllib.parse
from service.coe_analysis.llm_sdk_importer import COE_SYNC_DATA, RESULT_FILTER_WHITE_LIST, TASK_TYPES, NameSpace, es_util  # noqa
from crane.fund_judgement import fund_judgement_job
from service.coe_analysis.llm_sdk_importer import is_online_env
from llmcore_sdk.utils.dx_helper import send_dx_message_to_person

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


@coe.before_request
def before():
    try:
        if (request.method not in ['GET', 'POST']):
            return
        info = request.environ.get('HTTP_USERINFO')
        info = urllib.parse.unquote(info)
        user_info = json.loads(info)
        logger.info(f'[登陆信息] {user_info}')
        ssoid = user_info['ssoId']
        if ssoid is None or len(ssoid) == 0:
            logger.info('[无效登陆信息]')
            return jsonify({'error': '无效登陆信息'})
        else:
            request.environ.update({'HTTP_USERINFO': user_info})
            pass
    except Exception as e:
        logger.exception(e.args)
        return Response(response=e.args, status=401)


@coe.route('/query/incidents', methods=['POST'])
def query_incidents():
    '''
    获取coe列表接口
    '''
    try:
        logger.info(f'[coe/query/incidents] request={request.json}')
        url = f'{COE_API_HOST}/query/incidents'
        payload = request.json
        exclude_light_template = payload.pop('excludeLightTemplate')
        res = requests.post(url=url, timeout=25, json=payload, headers=headers)
        response_report_json = json.loads(res.content)
        length = len(response_report_json['incidents'])
        logger.info(f'[coe/query/incidents] incidents.length = {length}')

        if (exclude_light_template):
            # payload['page_size'] = 1000
            # payload['page'] = 1
            # payload['coe_template_id'] = 30
            # res_exclude = requests.post(
            #     url=url, timeout=25, json=payload, headers=headers)
            # report_json = json.loads(res_exclude.content)
            # total_exclude = int(report_json['total_count'])

            new_incidents = []
            for incident in response_report_json['incidents']:
                coe_template = incident.pop('coe_template', {})
                if (coe_template is None):
                    new_incidents.append(incident)
                    continue
                coe_template_id = coe_template.pop('coe_template_id', 0)
                _id = incident['_id']
                if (coe_template_id == 30):
                    logger.info(f'[coe/query/incidents] 排除轻量级模版 {_id}')
                    continue
                new_incidents.append(incident)
            response_report_json['incidents'] = new_incidents
            # response_report_json['total_count'] -= total_exclude   # 总量里面排除会造成分页不全的问题
            # logger.info(f'[coe/query/incidents] 轻量模板数量 {total_exclude}')
        return jsonify(response_report_json)
    except Exception as e:
        logger.exception('[coe/query/incidents]失败' + str(e))
        return Response(response=e.args, status=401)


@coe.route('/orgs', methods=['GET'])
def get_orgs():
    '''
    获取组织架构接口
    '''
    try:
        logger.info('[coe/orgs] start')
        logger.info(request.environ.get('HTTP_USERINFO')['userLogin'])
        url = f'{COE_API_HOST}/orgs?category=tree'
        res = requests.get(url=url, timeout=25, headers=headers)
        logger.info('[coe/orgs] end')
        responseReportJson = json.loads(res.content)
        return jsonify(responseReportJson)
    except Exception as e:
        logger.exception('[coe/orgs]失败' + str(e))
        return Response(response=e.args, status=401)


@coe.route('/task/start', methods=['POST'])
def start_task():
    '''
    创建任务并开始分析
    payload={
        coe_list:[],
        type_list:[],
        name:'',
        source:'',
    }
    return={
        data:{id:id}
    }
    '''
    try:
        logger.info(f'[coe/task/start] 开始分析任务 request={request.json}')
        payload = request.json
        coe_list = payload.get('coe_list', None)
        extral_args = payload.get('extral_args', [])
        type_list = payload['type_list']
        name = payload['name']
        source = payload['source']
        submitter = request.environ.get('HTTP_USERINFO')['userLogin']
        ssoId = request.environ.get('HTTP_USERINFO').get('ssoId', None)
        mis_id = None
        if ssoId is not None:
            logger.info(f'{submitter} 已经登陆')
            mis_id = submitter
        if coe_list is None:
            # 从 coe_store 里面开启任务
            storage_config = payload.get('storage_config', {})
            assert storage_config is not None, '请给出 coe_list 或者 查询条件'
            coe_list, total = coe_store_show_inner(storage_config)
            coe_list = [BaseCoeData(coe_id=i.coe_id, brief=i.brief, level=i.level) for i in coe_list]
            id = create_task_by_base_coe_data(coe_list, name, source, type_list, submitter, extral_args=extral_args,
                                              mis_id=mis_id)
        else:
            # 从选中的 coe_list 里面开启任务
            id = create_task(coe_list=coe_list, name=name, source=source, mis_id=mis_id,
                             type_list=type_list, submitter=submitter, extra_args=[])
        return jsonify({"id": id})
    except Exception as e:
        logger.exception('[coe/task/start] 分析任务失败' + str(e))
        return Response(response=e.args, status=406)


@coe.route('/task/aggr/start', methods=['POST'])
def start_aggr_task():
    try:
        logger.info(f'[coe/task/aggr/start] 开始分析任务 request={request.json}')
        payload = request.json
        create_begin = payload['begin_time']
        create_end = payload['end_time']
        type = payload['type']
        k = int(payload.get('k', 0))
        cause = payload.get('cause_search', None)
        if cause and len(cause) == 0:
            cause = None
        name = payload['name']
        source = payload['source']
        submitter = request.environ.get('HTTP_USERINFO')['userLogin']
        id = aggr_task_create(name=name, submitter=submitter, source=source, cause=cause,
                              create_begin=create_begin, create_end=create_end, k=k, type=type)
        return jsonify({"id": id})
    except Exception as e:
        logger.exception('[coe/task/aggr/start] 分析任务失败' + str(e))
        return Response(response=e.args, status=406)


@coe.route('/task/show', methods=['GET'])
def show_task():
    '''
    查看任务列表
    begin_time:2023-05-21
    end_time:2023-06-26
    size:每页任务数
    from_:分页开始的index
    task_id_match
    task_name_match: 用通配符进行匹配
    '''
    try:
        begin_time = request.args.get('begin_time')
        end_time = request.args.get('end_time')
        size = request.args.get('size')
        from_ = request.args.get('from_')
        task_id_match = request.args.get('task_id_match', '')
        task_name_match = request.args.get('task_name_match', '')
        other_must_inner = []
        if len(task_name_match) != 0:
            other_must_inner.append(
                {"wildcard": {"name": f"*{task_name_match}*"}})
        if len(task_id_match) != 0:
            other_must_inner.append({"term": {"id": task_id_match}})
        if len(other_must_inner) == 0:
            other_must_inner.append(
                {"range": {"start_date": {"gte": begin_time, "lte": end_time}}})
        logger.info(
            f'[coe/task/show] 获取 task :: {begin_time}~~{end_time}, ' +
            f'size={size}, from_={from_}')
        task_list, total = get_all_task(
            size, from_, other_must_inner=other_must_inner)
        logger.info(f'[coe/task/show] 获取 task 结果，总数{total}')
        return jsonify({"task_list": [i.to_json_dict() for i in task_list],
                        "total": total})
    except Exception as e:
        logger.exception(
            f'[coe/task/show] 获取 task 失败:: {begin_time}~~{end_time}, ' +
            f'size={size}, from_={from_}' + str(e))
        return Response(response=e.args, status=404)


@coe.route('/task/find', methods=['GET'])
def _find_task():
    try:
        task_id = request.args.get('task_id')
        logger.info(f'[coe/task/find] 获取 task :: {task_id}')
        task = get_single_task(task_id)
        logger.info(f'[coe/task/find] 获取 task 结果 {task_id}')
        return jsonify({"task": task.to_json_dict()})
    except Exception as e:
        logger.exception(f'[coe/task/show] 获取 task 失败:: {task_id}' + str(e))
        return Response(response=e.args, status=404)


@coe.route('/result/detail', methods=['GET'])
def get_result_detail():
    '''
    获取任务的单个子任务信息
    会通过 task_id,coe_id,type查询 子任务 和 experience , 因为子任务结果放在 experience 表
    子任务放在result, 结构为 COEResult
    历史相似case放在similiar_case_list结构为List[Experience]
    回答结果放在answer_message结构为List[Experience]
    '''
    try:
        task_id = request.args.get('task_id')
        coe_id = request.args.get('coe_id')
        type = request.args.get('type')
        result, _id, similiar_case_list, answer_message =\
            search_coe_result_item_with_experience(
                task_id=task_id, coe_id=coe_id, type=type)
        return jsonify({'result': result,
                        'similiar_case_list': similiar_case_list,
                        'answer_message': answer_message})
    except Exception as e:
        logger.exception('[coe/result/detail] 获取 result 失败' + str(e))
        return Response(response=e.args, status=404)


@coe.route('/result/list', methods=['GET'])
def get_result_list():
    '''
    获取任务列表
    会计算云图以及echarts饼状图的统计结果aggrs
    '''
    try:
        task_id = request.args.get('task_id')
        size = request.args.get('size')
        from_ = request.args.get('from_')
        logger.info(
            f'[coe/result/list] 获取 result { task_id } :: ' +
            f'size={size}, from_={from_}')
        time0 = time()
        result_dict, total, aggrs, cloud = chain_result_get(
            size, from_, task_id)
        time1 = time()
        metrics = metrics_task(task_id=task_id)
        time2 = time()
        logger.info('chain_result_get总耗时 {}s'.format(time1-time0))
        logger.info('metrics_task总耗时 {}s'.format(time2-time1))
        logger.info(f'[coe/result/list] 获取 result 结果，总数{total}')
        return jsonify({"result_list": [v for k, v in result_dict.items()],
                        "total": total, "aggrs": aggrs, "cloud": cloud,
                        'metrics': metrics})
    except Exception as e:
        logger.exception('[coe/result/list] 获取 result 失败' + str(e))
        return Response(response=e.args, status=404)


@coe.route('/task/restart', methods=['GET'])
def restart_task():
    '''
    重新开始任务
    '''
    try:
        task_id = request.args.get('task_id')
        logger.info(f'[coe/task/restart] 开始分析任务 task_id={task_id}')
        rerun_task(task_id)
        return jsonify({"message": "ok"})
    except Exception as e:
        logger.exception('[coe/task/restart] 分析任务失败' + str(e))
        return Response(response=e.args, status=406)


@coe.route('/topic/analysis', methods=['POST'])
def analysis_topic():
    '''
    进行主题分析，会输出相关COE列表以及COE任务
    payload={
        task_id:
        topic:
    }
    result={data:{
        answer:"",
        result_list=List[COEResult]
    }}
    '''
    try:
        logger.info(f'[coe/topic/analysis] 开始分析任务 request={request.json}')
        payload = request.json
        task_id = payload['task_id']
        topic = payload['topic']
        answer, result_list = topic_analysis(topic=topic, task_id=task_id)
        logger.info('[coe/topic/analysis] 分析结束')
        return jsonify({"answer": answer, "result_list": result_list})
    except Exception as e:
        logger.exception('[coe/task/start] 分析任务失败' + str(e))
        return Response(response=e.args, status=406)


@coe.route('/result/save', methods=['POST'])
def result_save():
    '''
    这个方法会根据 coe_result 搜索到数据库中的内容
    然后根据changeLog进行修改
    最后存入数据库
    payload={
        coe_result:COEResult,
        change_log:ChangeLog
    }
    '''
    try:
        logger.info('[coe/result/save] 开始保存')
        payload = request.json
        coe_result = payload['coe_result']
        to_sync_coe_result = payload.get('to_sync_coe_result', True)
        change_log = ChangeLog.from_json(payload['change_log'])
        submitter = request.environ.get('HTTP_USERINFO')['userLogin']
        submitter = payload.get('submitter', submitter)
        change_log.submitter = submitter
        chain_result_save(coe_result, change_log)
        # 同步coe维度
        coe_id = coe_result['coe_id']
        type = coe_result['type']
        if to_sync_coe_result:
            try:
                sync_coe_result(coe_id, type)
            except Exception as e:
                logger.exception("同步storage失败" + e)
        logger.info('[coe/result/save] 结束')
        return jsonify({"message": 'ok'})
    except Exception as e:
        logger.exception('[coe/result/save] 保存失败' + str(e))
        return Response(response=e.args, status=406)


@coe.route('/experience/save', methods=['POST'])
def experience_save():
    '''
    payload=Experience
    这个是直接保存经验知识，如果没有，就重建
    仅用于经验知识页面，保存经验知识，或者接口调用
    '''
    try:
        logger.info('[coe/experience/save] 开始保存')
        payload = request.json
        experience = Experience.from_json(payload)
        id = save_experience(experience)
        # 同步coe维度
        sync_coe_result(experience.coe_id, experience.type)
        logger.info(f'[coe/experience/save] 结束 id = {id}')
        return jsonify({"message": 'ok', 'id': id})
    except Exception as e:
        logger.exception('[coe/experience/save] 保存失败' + str(e))
        return Response(response=e.args, status=406)


@coe.route('/experience/mark', methods=['POST'])
def experience_mark():
    '''
    将某个id代表的经验知识进行标记，标记为标准的分析
    '''
    try:
        logger.info('[coe/experience/mark] 开始')
        payload = request.json
        id = payload['id']
        experience_mark_update(id, is_marked=True)
        logger.info(f'[coe/experience/mark] 结束 id = {id}')
        return jsonify({"message": 'ok'})
    except Exception as e:
        logger.exception('[coe/experience/mark] 保存失败' + str(e))
        return Response(response=e.args, status=406)


@coe.route('/experience/list', methods=['GET'])
def get_experience_list():
    '''
    获取收藏了的经验知识的列表，按type划分
    '''
    try:
        type = request.args.get('type')
        size = request.args.get('size')
        from_ = request.args.get('from_')
        logger.info(
            f'[coe/experience/list] 获取 result {type} :: ' +
            f'size={size}, from_={from_}')
        result_list, total = get_experience(size=size, from_=from_, type=type)
        logger.info(f'[coe/experience/list] 获取 result 结果，总数{total}')
        return jsonify({"experience_list": result_list, "total": total})
    except Exception as e:
        logger.exception('[coe/experience/list] 获取 result 失败' + str(e))
        return Response(response=e.args, status=404)


@coe.route('/experience/delete', methods=['DELETE', 'POST'])
def experience_del():
    '''
    取消收藏某条经验知识
    '''
    try:
        id = request.args.get('id')
        experience_mark_update(id=id, is_marked=False)
        return jsonify({'message': 'ok'})
    except Exception as e:
        logger.exception('[coe/result/detail] 获取 result 失败' + str(e))
        return Response(response=e.args, status=406)


@coe.route('/task/type/list', methods=['GET'])
def get_type_list_config():
    task_types = TASK_TYPES
    try:
        return jsonify({'task_types': task_types})
    except Exception as e:
        logger.exception('[/task/type/list] 获取 result 失败' + str(e))
        return Response(response=e.args, status=404)


@coe.route('/task/compare', methods=['GET'])
def compare_task():
    '''
    对比两个task，需要传入task_id和base_task_id
    '''
    try:
        task_id = request.args.get('task_id')
        base_task_id = request.args.get('base_task_id')
        logger.info(
            f'[coe/task/compare] task_id={task_id} \n ' +
            f'base_task_id={base_task_id}')
        answer = compare_task_with_base_task(
            task_id=task_id, base_task_id=base_task_id)
        return jsonify({'result': answer})
    except Exception as e:
        logger.exception('[coe/task/compare] 获取 result 失败' + str(e))
        return Response(response=e.args, status=406)


@coe.route('/task/metrics', methods=['GET'])
def calculate_task_metrics():
    '''
    计算一个task的接受情况
    '''
    try:
        task_id = request.args.get('task_id')
        logger.info(f'[coe/task/metric] task_id={task_id} \n')
        answer = metrics_task(task_id=task_id)
        return jsonify({'result': answer})
    except Exception as e:
        logger.exception('[coe/task/metrics] 获取 result 失败' + str(e))
        return Response(response=e.args, status=406)


@coe.route('/crawler/data/sync', methods=['GET'])
def crawler_data_sync_():
    try:
        coe_id = request.args.get('coe_id')
        logger.info(f'[coe/crawler/data/sync] coe_id={coe_id} \n')
        delete_passed(coe_id=coe_id)
        answer = sync_crawler_data(coe_id=coe_id)
        return jsonify({'result': answer})
    except Exception as e:
        logger.exception('[coe/crawler/data/sync] 失败' + str(e))
        return Response(response=e.args, status=406)


@coe.route('/crane/fund_judgement', methods=['GET'])
def fund_judgement_job_run():
    try:
        logger.info('[coe/crane/fund_judgement]')
        fund_judgement_job()
        return jsonify({'result': 'ok'})
    except Exception as e:
        logger.exception('[coe/crane/fund_judgement] 失败' + str(e))
        return Response(response=e.args, status=406)


@coe.route('/crane/tonotto', methods=['GET'])
def tonotto_job_run():
    '''curl -X GET -H 'userinfo: {"ssoId":"crane","userLogin":"crane"}' http://localhost:8002/coe/crane/tonotto -H "Accept: application/json" -H "Content-type: application/json" > /data/applogs/inf/com.sankuai.toolchain.coverage.agent/crane-tonotto.log'''  # noqa
    try:
        precheck = request.args.get('precheck')
        precheck = precheck.lower() == 'true'
        logger.info(f'[coe/crane/tonotto] precheck = {precheck}')
        coe_executor.submit(tnt_task, precheck)
        return jsonify({'result': 'ok'})
    except Exception as e:
        logger.exception('[coe/crane/tonotto] 失败' + str(e))
        return Response(response=e.args, status=406)


@coe.route('/crane/cause', methods=['GET'])
def cause_job_run():
    '''curl -X GET -H 'userinfo: {"ssoId":"crane","userLogin":"crane"}' http://localhost:8002/coe/crane/cause -H "Accept: application/json" -H "Content-type: application/json" > /data/applogs/inf/com.sankuai.toolchain.coverage.agent/crane-cause.log'''  # noqa
    try:
        logger.info('[coe/crane/cause]')
        coe_executor.submit(cause_analysis_task)
        return jsonify({'result': 'ok'})
    except Exception as e:
        logger.exception('[coe/crane/cause] 失败' + str(e))
        return Response(response=e.args, status=406)


@coe.route('/crane/data_sync', methods=['GET'])
def crane_coe_sync_auto():
    '''curl -X GET -H 'userinfo: {"ssoId":"crane","userLogin":"crane"}' http://localhost:8002/coe/crane/data_sync -H "Accept: application/json" -H "Content-type: application/json" > /data/applogs/inf/com.sankuai.toolchain.coverage.agent/crane-coe_sync_task.log'''  # noqa
    try:
        logger.info('[coe/data_sync]')
        coe_sync_auto()
        return jsonify({'result': 'ok'})
    except Exception as e:
        logger.exception('[coe/data_sync] 失败' + str(e))
        return Response(response=e.args, status=406)


@coe.route('/crane/mole_tag_analysis', methods=['POST'])
def _mole_gat_analysis_auto():
    logger.info('[coe/crane/mole_tag_analysis]')
    try:
        payload = request.json
    except Exception:
        payload = {}
    try:
        if 'coe_ids' in payload and 'task_name' in payload:
            coe_ids = payload['coe_ids']
            task_name = payload['task_name']
            assert isinstance(coe_ids, list)
            assert isinstance(task_name, str)
            coe_executor.submit(mole_tag_task_inner, coe_ids, task_name)
        else:
            coe_executor.submit(mole_tag_task)
        return jsonify({'result': 'ok'})
    except Exception as e:
        logger.exception('[coe/crane/mole_tag_analysis] 失败' + str(e))
        return Response(response=e.args, status=406)


@coe.route('/coestore/coe_sync', methods=['POST'])
def coe_sync_():
    '''today=$(date -d "now" +%Y-%m-%d);before=$(date -d"10 day ago" +%Y-%m-%d);data="{\"create_start\":\"${before}\",\"create_end\":\"${today}\"}";curl -X POST -d $data -H 'userinfo: {"ssoId":"crane","userLogin":"crane"}' http://localhost:8002/coe/coestore/coe_sync -H "Accept: application/json" -H "Content-type: application/json" > /data/applogs/inf/com.sankuai.toolchain.coverage.agent/crane-coe_sync_task.log'''  # noqa
    try:
        logger.info('[coe/crane/coe_sync]')
        payload = request.json
        create_start = payload.get('create_start')
        update_start = payload.get('update_start', create_start)  # 默认是 create_start
        create_end = payload.get('create_end')
        logger.info(f'coe同步任务开始，搜寻 {create_start} ~ {create_end} 存在更新的 coe')
        coe_ids, coe_item_dict = getLatestId(update_start=update_start, create_start=create_start,
                                             create_end=create_end, level='')
        coe_executor.submit(batch_sync_coe_storage, coe_ids)
        return jsonify({'result': 'ok'})
    except Exception as e:
        logger.exception('[coe/crane/coe_sync] 失败' + str(e))
        return Response(response=e.args, status=406)


def coe_store_show_inner(payload: dict):
    begin_time = payload.get('begin_time')
    end_time = payload.get('end_time')
    levels = payload.get('levels', None)
    orgs = payload.get('orgs', None)
    size = payload.get('size')
    from_ = payload.get('from')
    filter6to2not = payload.get('filter6to2not', False)
    filterfund = payload.get('filterfund', False)
    is_exclude_light_template = payload.get('is_exclude_light_template', False)
    brief_search = payload.get('brief_search', None)
    cause_search = payload.get('cause_search', None)
    cause_match = payload.get('cause_match', None)
    brief_match = payload.get('brief_match', None)
    template_ids = payload.get('template_ids', None)
    diff6to2not = payload.get('diff6to2not', False)
    filter6to2not_reviewed = payload.get('filter6to2not_reviewed', None)
    logger.info(
        f'[coe/coestore/show] 获取 task :: {begin_time}~~{end_time}, ' +
        f'size={size}, from_={from_}, levels={levels}, orgs={orgs}')
    other_must_inner = []
    if cause_match:
        _should_inner = [
            {"terms": {"cause_analysis.rd_result.keyword": cause_match}},
            {"terms": {"cause_analysis.analysis_result.keyword": cause_match}}
        ]
        other_must_inner = [{"bool": {"should": _should_inner}}]
    if brief_match:
        other_must_inner.append({
            "wildcard": {"brief.keyword": f"*{brief_match}*"}
        })
    coe_list, total = list_coe(begin_time, end_time, size, from_, orgs=orgs, filterfund=filterfund, levels=levels,
                               is_exclude_light_template=is_exclude_light_template,  template_ids=template_ids,
                               other_must_inner=other_must_inner, brief_search=brief_search,
                               cause_search=cause_search, filter6to2not=filter6to2not,
                               diff6to2not=diff6to2not, filter6to2not_reviewed=filter6to2not_reviewed)
    return coe_list, total


@coe.route('/coestore/show', methods=['POST'])
def coestore_show():
    '''
    查看COE列表
    begin_time:2023-05-21
    end_time:2023-06-26
    levels
    orgs
    brief_search
    cause_search
    filterfund
    filter6to2not
    size:每页任务数
    from_:分页开始的index
    '''
    try:
        payload: dict = request.json
        coe_list, total = coe_store_show_inner(payload)
        logger.info(f'[coe/coestore/show] 获取 task 结果，总数{total}')
        return jsonify({"coe_list": [i.to_json_dict() for i in coe_list], "total": total})
    except Exception as e:
        logger.exception(f'[coe/coestore/show] 获取 task 失败: {payload}, ' + repr(e))
        return Response(response=e.args, status=404)


@coe.route('/result/filter/white_list')
def get_result_filter_white_list_():
    try:
        logger.info('[coe/result/filter/white_list]')
        return jsonify({"white_list": RESULT_FILTER_WHITE_LIST})
    except Exception as e:
        logger.exception('[coe/result/filter/white_list] 获取失败' + str(e))
        return Response(response=e.args, status=404)


@coe.route('/coestore/result_update', methods=['GET'])
def coestore_result_update_():
    try:
        logger.info('[coe/coestore/result_update]')
        coe_id = request.args.get('coe_id')
        default_type_list = [item['type'] for item in TASK_TYPES]
        type_list = request.args.get('type_list', default=default_type_list)
        try:
            batch_sync_coe_storage([coe_id], type_list=type_list)
            sleep(1)
        except Exception:
            logger.warn(f'同步 {coe_id} {type} 的结果失败')
        return jsonify({"result": 'ok'})
    except Exception as e:
        logger.exception('[coe/coestore/result_update] 获取失败' + str(e))
        return Response(response=e.args, status=404)


@coe.route('/task/aggr/recall', methods=['GET'])
def _task_aggr_recall():
    try:
        logger.info('[coe/task/aggr/recall]')
        task_id = request.args.get('task_id')
        task, _id = search_task(task_id)
        tree_runner = CauseTreeSearchRunner(task_id=task_id)
        items, chain, rootList = tree_runner.tree_search()
        rootList = rootList[0]['children']
        return jsonify({"result": items, "coe_ids": task.choosed_coe_list,
                        'chain': chain.to_json_dict(), "rootList": rootList})
    except Exception as e:
        logger.exception('[coe/task/aggr/recall] 获取失败' + str(e))
        return Response(response=e.args, status=404)


@coe.route('/coestore/fund_tag/batch', methods=['POST'])
def _batch_get_fund_tag():
    try:
        logger.info('[coe/coestore/fund_tag/batch]')
        payload: dict = request.json
        coe_ids = payload['coe_ids']
        size = int(payload.get('size', 1000))
        # to_show_detail = payload.get('to_show_detail', 'false').lower() == 'true'
        coes, _ = batch_search_coe_storage(coe_ids=coe_ids, size=size)
        chain_ids = []
        not_find_list = []
        for coe in coes:
            coe_id = coe.coe_id
            category = coe.category
            fund_safety = coe.fund_safety
            if fund_safety is None:
                not_find_list.append({'brief': coe.brief,
                                      'coe_id': coe_id,
                                      'category': category})
                continue
            fund_aggr_classify = fund_safety.fund_aggr_classify
            if fund_aggr_classify is None:
                not_find_list.append({'brief': coe.brief,
                                      'coe_id': coe_id,
                                      'category': category})
                continue
            chain_ids.append(fund_aggr_classify.analysis_result_id)
        searched_coe_ids = [str(coe.coe_id) for coe in coes]
        for coe_id in coe_ids:
            try:
                coe_id = int(coe_id)
                assert coe_id > 0
                coe_id = str(coe_id)
                if coe_id not in searched_coe_ids:
                    not_find_list.append({'brief': None, 'coe_id': coe_id, 'category': None})
            except Exception as e:
                logger.info(f'coe_id:{coe_id} 非法 + {str(e)}')
        item_dict = batch_search_chain_by_id_with_experience_as_json(chain_id_list=chain_ids)
        answers = []
        for coe in coes:
            coe_id = coe.coe_id
            category = coe.category
            if coe_id not in item_dict:
                continue
            item = item_dict[coe_id]
            sub_tags = []
            mole_first_level_tag = None
            link = None
            task_id = None
            if coe.fund_safety:
                mole_first_level_tag = coe.fund_safety.mole_first_level_tag
                if coe.fund_safety.fund_aggr_classify:
                    task_id = coe.fund_safety.fund_aggr_classify.analysis_task_id
                    if isinstance(task_id, list):
                        task_id = task_id[0]
                    type = 'fund_aggr_classify'
                    coe_id = coe.coe_id
                    link = f'https://qa.sankuai.com/coe/result_tab/task_id/{task_id}' + \
                        f'?coe_id={coe_id}&type={type}'
            try:
                sub_tags = item['answer_message'][0]['data'][-1]['content']
                if isinstance(sub_tags, str):
                    sub_tags = re.split(r',\s*|，\s*|、\s*', sub_tags)
            except Exception:
                logger.warn("没有 item['answer_message'][0]['data'][-1]['content']")
            ans = {
                'brief': coe.brief,
                'coe_id': coe_id,
                'category': category,
                'first_tag': mole_first_level_tag,
                'sub_tags': sub_tags,
                'is_reviewed': item['is_reviewed'],
                'review_link': link,
                'task_id': task_id
            }
            # if to_show_detail:
            #     ans['detail'] = item
            answers.append(ans)
        return jsonify({"data": answers, "not_find": not_find_list})
    except Exception as e:
        logger.exception('[coe/coestore/fund_tag/batch] 获取失败' + str(e))
        return Response(response=e.args, status=404)


def callback_to_coe_api(coe_id, template_name, fill_value, value_hover_html):
    tag, tag_incidents = get_tag_instance(coe_id=coe_id)
    for field_name, tag_incident in tag_incidents.items():
        if field_name == template_name:
            put_custom_instance(_id=tag_incident['_id'],
                                value=tag_incident['value'],
                                fill_value=fill_value,
                                value_hover_html=value_hover_html,
                                trigger_fill_accepted=False)
            return


def auto_fill_warpper(coe_info_dict, submitter, type, tag_name, template_name,
                      task_id, force=False, result_list=None):
    coe_id = coe_info_dict['_id']
    brief = coe_info_dict['brief']
    lnk = f'https://qa.sankuai.com/coe/result_tab/task_id/{task_id}?coe_id={coe_id}&type={type}'
    coe_lnk = f'https://coe.mws.sankuai.com/detail/{coe_id}'
    if not is_online_env:
        lnk += '#test'
    if submitter:
        send_dx_message_to_person(mis=submitter, message=f'线上问题：[{brief}|{coe_lnk}]\n分析中：[分析链接|{lnk}]')
    sleep(1)
    items = run_chain(task_id, force, result_list)
    runner: COESummaryRunner = items[0]
    try:
        analysis_reason = runner.exps[0].data[-1].content
        # analysis_reason_tmp = f'{analysis_reason}'
        analysis_result = get_result_to_show(runner.result_item, runner.exps[0])
        analysis_reason = analysis_reason.replace('\n', '<br/>')
        fill_value = analysis_result
        value_hover_html = f"<p>{analysis_reason}</p><p><a href='{lnk}'>相关链接</a></p>"
        callback_to_coe_api(coe_id=coe_id, template_name=template_name,
                            fill_value=fill_value, value_hover_html=value_hover_html)
        if submitter:
            send_dx_message_to_person(
                mis=submitter,
                message=f'【COE原因分析】\n线上问题：[{brief}|{coe_lnk}]\n分析结果：[{analysis_result}|{lnk}]')
    except Exception as e:
        logger.error(f'线上问题：[{brief}|{coe_lnk}]\n分析失败：[分析链接|{lnk}]', e)
        if submitter:
            send_dx_message_to_person(mis=submitter,
                                      message=f'线上问题：[{brief}|{coe_lnk}]\n分析失败：[分析链接|{lnk}]')
        return


@coe.route('/api/auto/fill', methods=["POST"])
def _coe_fill_api():
    logger.info('[/coe/api/auto/fill] 自动调用')
    mock = request.args.get('mock', False)
    if mock:
        return jsonify({
            "error": None,
            "data": {
                "fill_value": '测试测试',
                "value_hover_html": "<p>mock测试</p><p><a href='https://km.sankuai.com/collabpage/2003709184'>链接测试</a></p>"  # noqa
            }
        })
    auto_fill_req = AutoFillRequest.from_json(request.json)
    coe_id = str(auto_fill_req.incident_id)
    label = auto_fill_req.custom_template.label
    if label == '线上问题原因分类':
        _type = 'cause'
        _tag = 'cause_analysis'
        _template_name = '线上问题原因分类'
    else:
        raise NotImplementedError(f'没有实现对 {label} 的自动分析')
    # 同步 COE 信息到数据库
    coe_result_items, _ids = search_coe_result_item_list(coe_id=coe_id, type=_type)
    # 优先查询是否已经分析过了
    coe_store, _stg_id = search_coe(coe_id=coe_id)
    if coe_store is None:
        logger.info(f'没有 {coe_id} 的信息，尝试寻找')
        sync_once(coe_id)
        coe_store, _ = search_coe(coe_id=coe_id)
        if coe_store is None:
            logger.info(f'确实没有找到 {coe_id} 的信息')
            return jsonify({'error': f'没有找到 {coe_id} 的信息', 'data': None})
    # 获取 tag 标签信息
    tag = getattr(coe_store, _tag, None)
    # 如果有 tag 信息，那么要设置 trigger_by_coe 作为记录
    if tag is not None and isinstance(tag, Tag):
        tag.trigger_by_coe = True
        es_util.update(index=COE_SYNC_DATA, id=_stg_id, body={"doc": coe_store.to_json_dict()})
    # 开始判断是否存在实际能用的 tag
    fund_tag = False
    # 判断是否正在进行中的任务，如果有正在进行中的任务，且时间不超过 1min 之前，那么就会要求等待消息
    if len(coe_result_items) != 0:
        now = get_now_str()
        diff = diff_time_string(now, coe_result_items[0].edit_time)
        if diff.total_seconds() > 60:
            logger.info(f'没有找到 60s 以内的数据: {coe_id} 的 {_type}')
        elif not coe_result_items[0].is_done:
            logger.info(f'找到了正在执行中的 {coe_id} 的 {_type} 分析记录，请稍后')
            task_id = coe_result_items[0].task_id
            if isinstance(task_id, list) and len(task_id) > 0:
                task_id = task_id[0]
            return jsonify({
                "error": None,
                "data": {
                    "fill_value": '分析中',
                    "value_hover_html": f"请等待1分钟左右，会收到消息通知，结果出来以后，COE平台会自动同步最新结果，请刷新页面<br/><a href='https://qa.sankuai.com/coe/result_tab/task_id/{task_id}?coe_id={coe_id}&type={_type}'>最近一次任务链接</a></p>"  # noqa
                }
            })
        elif tag is not None and isinstance(tag, Tag) and tag.analysis_result is not None:
            logger.info(f'找到了 60s 以内的数据: {coe_id} 的 {_type}')
            if tag.analysis_result != '无法判断':  # 结果如果不是无法判断，那么优先用之前的结果
                fund_tag = True
        else:
            logger.info(f'找到了正在执行中的 {coe_id} 的 {_type} 分析记录，请稍后')
            fund_tag = True
            task_id = coe_result_items[0].task_id
            if isinstance(task_id, list) and len(task_id) > 0:
                task_id = task_id[0]
            return jsonify({
                "error": None,
                "data": {
                    "fill_value": '分析中',
                    "value_hover_html": f"请等待1分钟左右，会收到消息通知，结果出来以后，COE平台会自动同步最新结果，请刷新页面<br/><a href='https://qa.sankuai.com/coe/result_tab/task_id/{task_id}?coe_id={coe_id}&type={_type}'>最近一次任务链接</a></p>"  # noqa
                }
            })
    # 如果没有执行中，切没有历史的可以判断的结果，那么需要进行分析
    if not fund_tag:
        logger.info(f'没有找到 {coe_id} 的 {_type} 分析记录, 尝试发起调度')
        submitter = auto_fill_req.submitter
        coe = {"_id": coe_id, "brief": coe_store.brief, "level": coe_store.level}
        # 同步创建任务并刷新coe
        task_id = create_task_sync(coe_list=[coe], name=[f'{coe_id}-单独触发'], source='coe-平台触发',
                                   type_list=[_type], submitter=submitter, to_submit_task=False,
                                   to_sync_coe_storage=False)
        # 建立子任务
        result_list = bulk_create_result_info([coe_id], [_type], task_id)
        # 异步开启 task
        coe_executor.submit(auto_fill_warpper,
                            coe, submitter, _type, _tag, _template_name,
                            task_id, False, result_list)
        return jsonify({
            "error": None,
            "data": {
                "fill_value": '分析中',
                "value_hover_html": f"请等待1分钟左右，会收到消息通知，结果出来以后，COE平台会自动同步最新结果，请刷新页面<br/><a href='https://qa.sankuai.com/coe/result_tab/task_id/{task_id}?coe_id={coe_id}&type={_type}'>最近一次任务链接</a></p>"  # noqa
            }
        })
    # 如果找到了有效的分析记录，尝试拼装返回值
    if tag is not None and isinstance(tag, Tag):
        analysis_result = tag.analysis_result
        task_id = tag.analysis_task_id[0]
        ref_url = f'https://qa.sankuai.com/coe/result_tab/task_id/{task_id}?coe_id={coe_id}&type={_type}'
        if not is_online_env:
            ref_url += '#test'
        result, _id, similiar_case_list, answer_message =\
            search_coe_result_item_with_experience(
                task_id=task_id, coe_id=coe_id, type=_type)
        analysis_reason = answer_message[0].data[-1].content
        analysis_reason = analysis_reason.replace('\n', '<br/>')
        return jsonify({
            "error": None,
            "data": {
                "fill_value": analysis_result,
                "value_hover_html": f"<p>{analysis_reason}</p><p><a href='{ref_url}'>相关链接</a></p>"
            }
        })
    else:
        return jsonify({'error': '没有成功执行智能分析', 'data': None})
