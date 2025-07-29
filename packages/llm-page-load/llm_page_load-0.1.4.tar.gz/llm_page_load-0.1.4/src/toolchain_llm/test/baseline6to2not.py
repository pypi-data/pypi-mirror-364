from typing import List
from crane.cause_analysis import filter_update
from service.coe_analysis.coe_chain_service import \
    bulk_create_result_info, run_chain_once, search_task, update_chain_result, update_task
from service.coe_analysis.coe_experience_service import create_experience, get_experience
from service.coe_analysis.coe_store_service import batch_sync_coe_storage, list_coe, sync_coe_result
from service.coe_analysis.coe_task_service import create_task
from service.coe_analysis.config_reader import OPENAI_API_BASE, OPENAI_API_KEY
from service.coe_analysis.crawler.getDoc import getLatestId
from service.coe_analysis.crawler_data_service import sync_crawler_data, delete_passed, find_crawler_data
from service.coe_analysis.runners import get_runner_by_type
from service.coe_analysis.runners.tonotto import COE6to2notRunner
from service.coe_analysis.search_coe_result_item import search_all_chain, search_coe_result_item
from utils import logger, read_json, write_json, write_io
from service.coe_analysis.llm_sdk_importer import es_util
from service.coe_analysis.data_structure import Answer, BaseCoeData, COEResult, Experience, MetaMessage
import re
import time
from concurrent.futures import ThreadPoolExecutor, Future, wait
from sklearn.metrics import roc_auc_score
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, AIMessage
import service.coe_analysis.coe_chain_service as chain_service


coe_executor = ThreadPoolExecutor(max_workers=2)


def match_result(answer, pattern):
    match = pattern.findall(answer)
    if (len(match) > 0):
        return str(match[0])


def get_prechecked_answer(result_item: COEResult):
    answer = None
    pattern = re.compile(r'判断结果[:：]\s*([\u4e00-\u9fa5]+)')
    for message in result_item.message:
        if ('[预校验(不涉及大模型问答)]' in message.content):
            answer = match_result(message.content, pattern)
        elif ('[S9校验]' in message.content):
            answer = match_result(message.content, pattern)
    return answer


def get_passchecked_answer(result_item: COEResult):
    answer = None
    pattern = re.compile(r'判断结果[:：]\s*([\u4e00-\u9fa5]+)')
    message = result_item.message[-1]
    answer = match_result(message.content, pattern)
    # 大模型倾向于在 str 的前面写出是否违反
    if answer is None:
        return '无法确定'
    if answer.startswith('没违反'):
        answer = '没违反'
    if answer.startswith('未违反'):
        answer = '没违反'
    if answer.startswith('违反'):
        answer = '违反'
    if answer not in ['无法确定', '没违反', '违反']:
        answer = '无法确定'
    return answer


def get_total_answer(result_item: COEResult):
    # if result_item.type == 'not_to_delay' and result_item.level in ['S9','S4','S3','S2','S1']:
    # return '没违反'
    # answer = get_prechecked_answer(result_item)
    # if answer is None or answer in ['无法判断']:
    answer = get_passchecked_answer(result_item)
    return answer


def get_self_prove_answer(result_item: COEResult):
    answer = None
    pattern = re.compile(r'是否违反了要灰度的原则[:：]\s*([\u4e00-\u9fa5]+)')
    nex = False
    for message in result_item.message:
        if ('[声明]' in message.content):
            nex = True
        elif nex:
            answer = match_result(message.content, pattern)
            nex = False
    if answer is None:
        return '无法确定'
    if answer.startswith('没违反'):
        answer = '没违反'
    if answer.startswith('未违反'):
        answer = '没违反'
    if answer.startswith('没有违反'):
        answer = '没违反'
    if answer.startswith('违反'):
        answer = '违反'
    if answer not in ['无法确定', '没违反', '违反']:
        answer = '无法确定'
    return answer


def create_in_all(data, name, type_list=['to_test']):
    coe_id_list = [i['coe_id'] for i in data]
    coe_list = [BaseCoeData.from_json(i).to_json_dict() for i in data]
    task_id = create_task(coe_list, name=name, source='自动触发', type_list=type_list, submitter='lyl',
                          to_create_task=False)
    logger.info(f'task id = {task_id}')
    bulk_create_result_info(coe_id_list=coe_id_list, type_list=type_list, task_id=task_id)
    # task, _id = search_task(task_id)
    # task.is_active = True
    # update_task(task=task, _id=_id)
    return task_id


def create_with_type(task_id, type):
    task, _id = search_task(task_id)
    coe_list = task.choosed_coe_list
    coe_id_list = [i.coe_id for i in coe_list]
    bulk_create_result_info(coe_id_list=coe_id_list, type_list=[type], task_id=task_id)
    time.sleep(1)


def read_by_task(task_id, file_name='test/data/baseline_6to2not_6month.json'):
    task, _id = search_task(task_id)
    coe_list = task.to_json_dict()['choosed_coe_list']
    write_json(file_name, coe_list)


type_dict = {
    "to_test": "要测试",
    "to_claim": "要周知",
    "to_check": "要审核",
    "to_grey": "要灰度",
    "to_inspect": "要观测",
    "to_rollback": "要可回滚",
    "not_to_delay": "不要延报故障",
    "not_to_illagle_change_data": "不要违规变更数据",
    'null_check': '异常字段'
}


def write_to_xlsx(task_id, type, filename):
    result_list, _ = search_all_chain(task_id, from_=0, size=10000)
    items = []
    for data in result_list:
        if data.type != type:
            continue
        content = data.reason
        ans = data.message[-1].content
        item = {
            'coe_id': data.coe_id,
            'content': content,
            'ans': ans
        }
        items.append(item)
    write_io(f'test/data/{filename}', items)


def calculate_acc(task_id, data, type, need_declare=True):
    TP = {'prechecked': 0, 'passchecked': 0, 'total': 0, 'selfprove': 0}  # 确实违规
    FP = {'prechecked': 0, 'passchecked': 0, 'total': 0, 'selfprove': 0}  # 判断为违规，实际没违规
    FN = {'prechecked': 0, 'passchecked': 0, 'total': 0, 'selfprove': 0}  # 判断为非违规，实际违规
    TN = {'prechecked': 0, 'passchecked': 0, 'total': 0, 'selfprove': 0}  # 确实没违规
    # result_dict, _, _, _ = chain_result_get(size=1000, from_=0, task_id=task_id)
    task, _ = search_task(task_id)
    result_list, _ = search_all_chain(task_id, from_=0, size=10000)
    result_dict = {str(item.coe_id): item for item in result_list if item.type == type and len(item.message) != 0}
    total = len(data)
    yes = 0
    labels_pred = {'prechecked': [], 'passchecked': [], 'total': [], 'selfprove': []}
    labels_true = {'prechecked': [], 'passchecked': [], 'total': [], 'selfprove': []}
    for phase in ['prechecked', 'passchecked', 'total', 'selfprove']:
        func = {
            'prechecked': get_prechecked_answer,
            'passchecked': get_passchecked_answer,
            'total': get_total_answer,
            'selfprove': get_self_prove_answer
        }
        for d in data:
            coe_id = d['coe_id']
            positive = type_dict[type] in d.get('labels', [])
            if str(coe_id) not in result_dict:
                continue
            coe_result = result_dict[str(coe_id)]
            if coe_result.brief == 'test':
                continue
            if type != coe_result.type:
                continue
            has_declare = False
            for message in coe_result.message:
                if '[研发人员自己声明]' in message.content:
                    has_declare = True
            if not has_declare and need_declare:
                logger.info('[没有研发自己声明]')
                continue
            # if coe_result.is_reviewed:
                # continue
            chain_result = func[phase](coe_result)
            if (phase == 'total'):
                yes += 1
            pos_lbs = ['违反', '可能违反', '无法确定']
            neg_lbs = ['没违反']
            # pos_lbs = ['违反', '可能违反']
            # neg_lbs = ['没违反', '无法确定']
            if type == 'not_to_illagle_change_data':
                pos_lbs = ['违反', '可能违反']
                neg_lbs = ['没违反', '无法确定']

            if (chain_result in pos_lbs and positive):
                TP[phase] += 1
            elif (chain_result in pos_lbs and not positive):
                FP[phase] += 1
            elif chain_result in neg_lbs and positive:
                FN[phase] += 1
            elif chain_result in neg_lbs and not positive:
                TN[phase] += 1

            if chain_result in pos_lbs:
                labels_pred[phase].append(1)
            else:
                labels_pred[phase].append(0)

            if positive:
                labels_true[phase].append(1)
            else:
                labels_true[phase].append(0)

    print(f'=========  {task.name} {type} vaild_rate = {yes}/{total}  =========')
    # for type in ['prechecked', 'passchecked', 'total', 'selfprove']:
    for type in ['total']:
        print(f'---{type}---')
        print('\t\t 预测')
        print('\t\t 违反\t 没违反')
        print(f'实际\t违反\t {TP[type]}\t {FN[type]}')
        print(f'\t没违反\t {FP[type]}\t {TN[type]}')
        if (type in ['total', 'selfprove']):
            TPR = TP[type]/(TP[type]+FN[type]) if (TP[type]+FN[type]) > 0 else None
            FPR = FP[type]/(FP[type]+TN[type]) if (FP[type]+TN[type]) > 0 else None
            recall = TPR
            precision = TP[type]/(FP[type]+TP[type]) if (FP[type]+TP[type]) > 0 else None
            F1 = 2*precision*recall/(recall+precision) \
                if recall is not None and precision is not None and (precision+recall) > 0 else None

            ACC = (TP[type]+TN[type])/(FP[type]+TN[type]+TP[type]+FN[type]) \
                if (FP[type]+TN[type]+TP[type]+FN[type]) > 0 else 0
            try:
                auc = roc_auc_score(labels_true[type], labels_pred[type])
            except Exception as e:
                logger.info(e.args)
                auc = None
            print(f'TPR=recall={TPR}\nFPR={FPR}\nACC={ACC}\nAUC={auc}\nprecision={precision}\nF1={F1}')


def calculate_recall_rate(task_id, type_list, data):
    true_set = {str(i['coe_id']) for i in data if len(i.get('labels', [])) != 0}
    print(true_set)
    task, _ = search_task(task_id)
    result_list, _ = search_all_chain(task_id, from_=0, size=10000)
    result_dict = {str(item.coe_id): 0 for item in result_list}
    out_sider = []
    in_sider = []
    total = 0
    recall = 0
    type_dict = {}
    for data in result_list:
        if data.brief == 'test':
            continue
        type = data.type
        if type not in type_list:
            continue
        if (type not in type_dict):
            type_dict[type] = 0
        pos_lbs = ['违反', '可能违反', '无法确定']
        # if type in ['to_rollback', 'to_test', 'to_inspect', 'not_to_illagle_change_data']:
        if type in ['not_to_illagle_change_data']:
            pos_lbs = ['违反', '可能违反']
        if get_total_answer(data) in pos_lbs:
            result_dict[data.coe_id] += 1
            type_dict[type] += 1
    for k, v in result_dict.items():
        total += 1
        if v != 0:
            recall += 1
            if str(k) in true_set:
                in_sider.append(k)
        elif str(k) in true_set:
            out_sider.append(k)

    print(f'=========  {task.name} recall_rate = {recall}/{total} = {recall/total} 漏召回 {len(out_sider)} 个 =========')
    TP = len(in_sider)
    FN = len(out_sider)
    FP = recall - TP
    TN = total - TP - FN - FP
    print('\t\t 预测')
    print('\t\t 违反\t 没违反')
    print(f'实际\t违反\t {TP}\t {FN}')
    print(f'\t没违反\t {FP}\t {TN}')
    for k, v in type_dict.items():
        print(f'type:{k}\t{v}/{total}={v/total}')
    return recall, total, recall/total


def link_to_father_task(child, father):
    chains, _ = search_all_chain(task_id=child, from_=0, size=10000)
    chains_fa, _ = search_all_chain(task_id=child, from_=0, size=10000)
    for chain in chains:
        for chain_fa in chains_fa:
            if chain_fa.coe_id == chain.coe_id and chain_fa.type == chain.type and chain_fa.is_reviewed is False:
                chain.task_id.append(father)
                delete_chain(coe_id=chain.coe_id, task_id=father, type=chain.type)
                update_chain_result(chain)


def delete_chains(task_id, type):
    chains, _ = search_all_chain(task_id=task_id)
    for chain in chains:
        if (chain.type != type):
            continue
        if len(chain.message) == 0:
            index = 'coe_analysis_detail'
            query_josn = {
                "query": {"bool": {"must": [
                    {"term": {"id": chain.id}},
                    {"term": {"type": type}}
                ]}}
            }
            answer = es_util.search(index=index, query=query_josn)
            _id = answer[0]['_id']
            es_util.client.delete(index='coe_analysis_detail', id=_id, headers=es_util.headers)
    pass


def delete_chain(coe_id, task_id, type):
    index = 'coe_analysis_detail'
    query_josn = {
        "query": {"bool": {"must": [
            {"term": {"task_id": task_id}},
            {"term": {"coe_id": coe_id}},
            {"term": {"type": type}}
        ]}}
    }
    answer = es_util.search(index=index, query=query_josn)
    _id = answer[0]['_id']
    chain = COEResult.from_es(answer[0])
    chain.task_id.remove(task_id)
    if len(chain.task_id) == 0:
        es_util.client.delete(index=index, id=_id, headers=es_util.headers)
    else:
        update_chain_result(chain=chain)


def count_prechecked(task_id):
    result_list, _ = search_all_chain(task_id, from_=0, size=10000)
    count = 0
    prec_pass = 0
    for data in result_list:
        count += 1
        if data.pre_checked_passed:
            prec_pass += 1

    print(f'{prec_pass}/{count}={prec_pass/count}')


def get_precheck_table(coe_id_list: List[str], type: str):
    datas = []
    desc = None
    for coe_id in coe_id_list:
        try:
            content = []
            for desc in ['[标题]', '[发生时间]', '[研发自证]']:
                data_list, _ = find_crawler_data(coe_id=coe_id, desc=desc, type=type)
                data = data_list[0].get_text().strip()
                content.append(data)
            content = '\n\n'.join(content)
            output_data = {
                "coe_id": coe_id,
                "content": content,
                "analysis": ""
            }
            datas.append(output_data)
        except Exception as e:
            logger.exception(f'\n发生问题时的状态: coe_id={coe_id}, type={type}, desc={desc}, e.args={e.args}')
    return datas


def test_gpt4():
    model_name = 'gpt-4'
    llm = ChatOpenAI(model_name=model_name,
                     openai_api_base=OPENAI_API_BASE,
                     openai_api_key=OPENAI_API_KEY,
                     max_retries=6)
    aimessage = '''
对于要测试的判定，以往的经验如下：
------经验开始-----
- 由于组件没有测试能力，无法测试
- 回答: 没有测试能力被判定为"没违反"

- 由于其他理由没有测试，或者没理由
- 回答: 判定为"无法确定"

- 提到了代码覆盖率、测试覆盖率，或者写了某些测试不全面、覆盖率不够
- 回答: 虽然也有问题，但是这暗示了研发人员已经进行过测试，所以判定为"没违反"

- 明确了对什么进行测试，或者明确了测试方法，或者明确了测试阶段
- 回答: 这是测试的具体信息作证，判定为"没违反"

- 只提到处理线上问题的过程中进行了测试
- 回答: 处理过程中进行了测试，并不能代表线上变更之前进行了测试，不能据此进行推断，所以判定为"无法确定"

- 不涉及系统开发、功能开发、新增变更、上线、RD变更、回滚测试
- 回答: 不是新变更引发的，所以判定为"没违反"

- 没有新代码上线
- 回答：由于没有新代码上线，这是一个历史遗留问题，所以判定为"没违反"

- 由于配置变更而认为不需要测试，这是不对的
- 回答: 配置变更需要测试，判定为"违反"

- 仅回答"已测试"或者"已自测"，类似这样的描述是不够具体的
- 回答：答案不够具体，所以判定为"无法确定"
-----经验结束-----
'''
    human = '''线上问题的描述如下：
-------描述开始------
[发生时间]
2023-02-09 10:36:00

[研发自证]
研发人员自我陈述:已自测
是否违反要测试原则:
-------描述结束------

请推测这个线上问题是否违反了"要测试"的原则。
请按照以下格式输出：
推测结果：违反或者没违反或者无法确定
原因：'''
    answer = llm([AIMessage(content=aimessage), HumanMessage(content=human)]).content
    print(answer)


task_ids = [
    "20666815788559305551884252609956024610",  # 1-4月的违反的COE，加一些2月没违反的，经验少
    "118182783104075848789461928370239443234",  # 5月
    '77298450503078144795567768412075594018',  # 1-4月的违反的COE，加一些2月没违反的，加经验
    '197731332107153124624519935938592248098',  # 1-4月的违反的COE，全type，经验少
    '305004994916303559208714008424154665250',  # 5月，全type
    '168562364425160653519715372794835374370',  # 1-4月的违反的COE，全type，加经验
    '172466035503268758238505820454958907248',  # 6月，6要两不要,
    '91016628897204321074216687986209963888',  # 7月，6要2不要
    '339276979142744355247658396310329889058',  # 1-4月，问卷版
    '201566527554963053196289209777229140258',  # 7月A,
    '77085820975281124829702385607437717794',  # 7月B
    '118061168038196205684655073574783029538',  # 5月新
    '168678232923449297541463152205729495010',  # 5月新34条，gpt-4，要测试、不要延报故障、要观测
    '173438344909805339380369200589779767586',  # 7月cyy
    '70358933714751564473397028073532035362',  # 7月cyy填好后
]


def get_finetune_data_by_task(task_id: str):
    chains, total = search_all_chain(task_id=task_id)
    data = []
    for chain in chains:
        item = {
            'user': '',
            'assistant': ''
        }
        for message in chain.message:
            if '预校验' in message.content:
                continue
            if message.role in ['user']:
                item['user'] = message.content
            elif message.role in ['assistant']:
                item['assistant'] = message.content
                data.append(item)
    return data


def get_fine_tune_data_by_type(type: str):
    exps, total = get_experience(type=type, size=100, from_=0)
    data = []
    for exp in exps:
        item = {
            'user': '',
            'assistant': ''
        }
        for message in exp.data:
            if message.role in ['user']:
                item['user'] = message.content
            elif message.role in ['assistant']:
                item['assistant'] = message.content
                data.append(item)
    return data


def exp_del():
    index = 'coe_analysis_experience'
    query_json = {
        "query": {"bool": {"must": [
            {"term": {"is_marked": True}}
        ]}},
        "sort": [{"id": {"order": "desc"}}]
    }
    answer = es_util.client.search(
        body=query_json, index=index, from_=0, size=1000,
        headers=es_util.headers)
    _ids = [i['_id'] for i in answer['hits']['hits']]
    result_list = [Experience.from_es(i) for i in answer['hits']['hits']]
    for res, _id in zip(result_list, _ids):
        if '判断依据:由于当前的COE是  级别的，所以跳过判定' in res.data[-1].content:
            res.is_marked = False
            body = {
                "doc": res.to_json_dict()
            }
            es_util.update(index=index, id=_id, body=body)
    return


def filter_edited(data):
    id_list, item_dict = getLatestId(create_start='2023-08-01', create_end='2023-08-31',
                                     update_start='2023-09-01', level='')
    res = []
    for d in data:
        coe_id = d['coe_id']
        if coe_id not in id_list:
            res.append(d)
    return res


def filter_E(task_id):
    task, _id = search_task(task_id=task_id)
    coes = task.choosed_coe_list
    coe_ids = []
    type = 'not_to_delay'
    for coe in coes:
        print(f"{coe.brief} {coe.level}")
        if coe.level == 'E':
            coe_ids.append(coe.coe_id)
    for coe_id in coe_ids:
        result_item, _id = search_coe_result_item(coe_id=coe_id, type=type, task_id=task_id)
        message = [
            MetaMessage('user', f'线上问题顶级: {coe.level}'),
            MetaMessage('assistant', f'- 判断依据: 由于线上问题的定级为{coe.level},所以不算延报\n- 判断结果: 没违反')
        ]
        exp = create_experience(type=result_item.type,
                                coe_id=coe_id,
                                task_id=task_id,
                                message_list=message)
        result_item.answer_message.insert(0, Answer(exp_id=exp.id))
        body = {
            "doc": result_item.to_json_dict()
        }
        es_util.client.update('coe_analysis_detail', id=_id,
                              body=body, headers=es_util.headers)
        time.sleep(1)
        sync_coe_result(coe_id, type)


def make_coe_tail(task_id):
    type_list = ["to_test", "to_claim", "to_check", "to_grey",
                 "to_inspect", "to_rollback", "not_to_delay",
                 "not_to_illagle_change_data"]
    task, _id = search_task(task_id=task_id)
    coes = task.choosed_coe_list
    # batch_sync_coe_storage(coe_id_list=[coe.coe_id for coe in coes])
    for type in type_list:
        for coe in coes:
            r, _id = search_coe_result_item(coe_id=coe.coe_id, type=type, task_id=task_id)
            if r.error == 'transfer_existing_answer() takes 1 positional argument but 2 were given':
                runner = get_runner_by_type(r, _id, type=type)
                assert isinstance(runner, COE6to2notRunner)
                print(coe.coe_id)
                existing_answer = r.reason
                res = r.message[-1].content
                message = [
                    MetaMessage('user', runner.transfer_existing_answer(existing_answer)),
                    MetaMessage('assistant', res)
                ]
                exp = create_experience(type=type, coe_id=coe.coe_id,
                                        task_id=task_id,
                                        message_list=message)
                # 进行头插，将大模型的判断结果作为最终结果。
                runner.result_item.answer_message.insert(0, Answer(exp_id=exp.id))
                runner.done()
                print(type + 'done ' + coe.brief)


if __name__ == '__main__':
    # task = create_task(coe_list=[{
    #     "_id": coe_id
    # }], name='test', source='手动触发', type_list=[_type], submitter='liyilun02', to_submit_task=False)
    task_id = '88321968027063208588645755288725927947'
    results,_ = search_all_chain(task_id=task_id)
    for result in results:
        run_chain_once(coe_id=result.coe_id, type='to_check', task_id=task_id)
    # for _type in ["to_test"]:
    #     all_chain, _total = search_all_chain(task_id=task)
    #     for chain in all_chain:
    #         if chain.error is not None:
    #             print(chain.brief)
    #             run_chain_once(coe_id=chain.coe_id, type=_type, task_id=task)
    exit()
    # train = []
    # valid = []
    # test  = []
    # for task_id in ['282622674248073297008693909207285888994',
    #                 '173438344909805339380369200589779767586',
    #                 '118061168038196205684655073574783029538',
    #                 ]:
    #     tmp_data = get_finetune_data_by_task(task_id=task_id)
    #     train.extend(tmp_data[:12])
    #     valid.extend(tmp_data[:5])
    #     test.extend(tmp_data[5:10])

    # for type in type_list:
    #     tmp_data = get_fine_tune_data_by_type(type)
    #     train.extend(tmp_data[:12])
    #     valid.extend(tmp_data[:5])
    #     test.extend(tmp_data[5:10])
    # write_json('test/data/train.json',train)
    # write_json('test/data/test.json',test)
    # write_json('test/data/valid.json',valid)
    # read_by_task(task_id='157543257572084255548869920876105431010', file_name='test/data/baseline_6to2not_10month')
    # exit()

    cur_type = 'not_to_delay'
    # data = read_json('test/data/baseline_6to2not.json')
    # data = read_json('test/data/baseline_6to2not_9month.json')
    # data = read_json('test/data/baseline_6to2not_6month.json')
    # data = read_json('test/data/baseline_6to2not_7month.json')
    # data = read_json('test/data/baseline_6to2not_7month_cyy.json')
    # task_id = create_in_all(data=[], name='5月-gpt4', type_list=type_list)
    # print('task_id=' + task_id)
    # link_to_father_task('303506467747721574839116725706423275810', task_id)
    # link_to_father_task('47249954195004195456016221558062190882', task_id)
    # task_id = '168562364425160653519715372794835374370'
    # task_id = '197731332107153124624519935938592248098'
    # task_id = '305004994916303559208714008424154665250'
    # task_id = '339276979142744355247658396310329889058'
    # task_id = '91016628897204321074216687986209963888'
    # task_id = '118061168038196205684655073574783029538'
    # task_id = '173438344909805339380369200589779767586'
    # task_id = '70358933714751564473397028073532035362'
    # task_id = '157543257572084255548869920876105431010'
    # task_id = '82767128024693786802851375834452064226'
    task_id = '168117857076819690310111547551002261474'
    # filter_E(task_id)

    # coe_id_list = [(d['coe_id'], d) for d in data if d['coe_id']]

    # for coe_id in coe_id_list:
    #     print(coe_id)
    #     delete_passed(coe_id)
    #     sync_crawler_data(coe_id)
    # data_list = get_precheck_table(coe_id_list, type=cur_type)
    # write_io('test/data/baseline_6to2not_5month-precheck.xlsx', data_list)

    features: List[Future] = []
    coe_id_list = [('262159', {})]
    for coe_id, item in coe_id_list:
        print(coe_id)
        # delete_passed(coe_id)
        # sync_crawler_data(coe_id)
        # no_self_prove = item.get('no_self_prove', False)
        no_self_prove = False
        try:
            # feature = coe_executor.submit(run_chain_once, coe_id, cur_type, task_id, True, no_self_prove)
            # features.append(feature)
            # for cur_type in type_list:
            #     run_chain_once(coe_id=coe_id, type=cur_type, force=True, task_id=task_id, no_self_prove=no_self_prove)

            cur_type = 'not_to_delay'
            chain_service.run_chain_once(coe_id=coe_id,
                                         type=cur_type,
                                         task_id=task_id,
                                         force=True)
        except Exception as e:
            logger.exception(e.args)

    # wait(features)
    # calculate_acc(task_id=task_id, data=data, type=cur_type)

    # write_to_xlsx(task_id, cur_type, 'baseline_6to2not-ans-gpt4-old.xlsx')

    # for cur_type in type_list:
    #     data = read_json('test/data/baseline_6to2not.json')
    #     # calculate_acc('197731332107153124624519935938592248098', data, cur_type)
    #     calculate_acc('168562364425160653519715372794835374370', data, cur_type)
    #     data = read_json('test/data/baseline_6to2not_5month.json')
    #     calculate_acc('305004994916303559208714008424154665250', data, cur_type)

    # data = read_json('test/data/baseline_6to2not_10month.json')
    # # data = filter_edited(data=data)
    # type_list = ["to_test", "to_claim", "to_check", "to_grey", "to_inspect",
    #              "to_rollback", "not_to_illagle_change_data", "not_to_delay"]
    # calculate_recall_rate('157543257572084255548869920876105431010', type_list=type_list, data=data)
    # for type in type_list:
    #     calculate_acc('157543257572084255548869920876105431010', data=data, type=type, need_declare=True)

    # task_id = '91016628897204321074216687986209963888'
    # calculate_recall_rate(task_id, type_list)
    # type_list = ['to_test', 'to_rollback', 'to_inspect']
    # calculate_recall_rate(task_id, type_list)
    # type_list = ["to_claim", "to_check", "to_grey", "not_to_delay", 'not_to_illagle_change_data']
    # calculate_recall_rate(task_id, type_list)

    # count_prechecked('31804782498513329675505968099908129058')
