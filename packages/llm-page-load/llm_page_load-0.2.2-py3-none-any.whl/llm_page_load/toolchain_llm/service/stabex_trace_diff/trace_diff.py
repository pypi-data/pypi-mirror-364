from service.app_traversal.es_client import client, headers
from llmcore_sdk.models import Friday, FridayVision
import json

def set_trace_as_ground_truth(task_id, case_name):
    res = get_trace_origin_info(task_id, case_name)
    if res['hits']['total']['value'] == 0:
        return False, '未匹配到此case'
    else:
        # 将trace的每个截图summary进行存储
        process_action_info = res['hits']['hits'][0]['_source'].get('process_action_info', [])
        trace_gt_info = {
            'case_name': case_name,
            'origin_trace_info': res['hits']['hits'][0]['_source']
        }
        if not process_action_info:
            return False, '此case并不存在执行记录'
        else:
            image_summary = [{'page_description': info.get('page_description', ''), 'action_info': info.get('action_info', '')} for info in process_action_info]
            trace_gt_info['pages_summary'] = image_summary
        # 到groundtruth库中寻找此case_name的记录
        gt_info = get_trace_ground_truth_info(case_name)
        if gt_info['hits']['total']['value'] == 0:
            client.index(index="stabex_trace_stable_reference", body=trace_gt_info)
            return True, '不存在此case记录，直接存储'
        else:
            body = {
                'doc': trace_gt_info
            }
            client.update(index="stabex_trace_stable_reference", id=gt_info['hits']['hits'][0]['_id'], body=body)
            return True, '存在此case记录，更新存储信息'

def compare_trace(task_id, case_name, mode='soft'):
    # 获取到被对比的执行trace
    res = get_trace_origin_info(task_id, case_name)
    if res['hits']['total']['value'] == 0:
        return False, '被对比case不存在'
    else:
        # 获取整体的执行过程
        process_action_info = res['hits']['hits'][0]['_source'].get('process_action_info', [])
        scheme_case_info = res['hits']['hits'][0]['_source'].get('scheme_case_info', '')
        # 到groundtruth库中寻找此case_name的记录
        gt_info = get_trace_ground_truth_info(case_name)
        if gt_info['hits']['total']['value'] == 0:
            return False, '不存在此case记录，无法进行对比'
        else:
            # 找到gt库中的记录，开始对比
            new_trace_info = ""
            for index, action_info in enumerate(process_action_info):
                new_trace_info += f"第{index+1}步action为：{action_info.get('action_info', '')}\n"
                new_trace_info += f"第{index+1}步后页面summary：{action_info.get('page_description', '')}\n"
            ground_truth_info = ""
            for index, summary in enumerate(gt_info['hits']['hits'][0]['_source']['pages_summary']):
                ground_truth_info += f"第{index+1}步后action为：{summary.get('action_info', '')}\n"
                ground_truth_info += f"第{index+1}步后页面summary：{summary.get('page_description', '')}\n"
            model = Friday('gpt-4.1', max_tokens=4096, temperature=0.01, direction='stabex_compare_trace')
            if mode == 'hard':
                prompt = f"""
                你是一个专业的测试开发工程师，现在有一个新执行的trace可一个已经标注过的ground truth trace，我希望你看一下新执行的trace是否也完成了类似的操作路径，筛出明显未完成或错误的操作路径。

                以下是新执行的trace信息：
                {new_trace_info}
                以下是ground truth的trace信息：
                {ground_truth_info}

                注意：
                1.因为是线上环境，商铺与数据是并不固定的，我们的目标不是查看数据是否一致，而是查看操作路径是否类似。
                2.输出你判断的置信度，1表示判断非常确定，0表示判断非常不确定，0.5表示判断一般。
                返回格式：
                {{
                    "same": true/false,
                    "reason": "think step by step and write your reason here. Use the Chinese.",
                    "confidence": 0-1
                }}
                注意：请严格按照上方json格式进行返回！并且不要携带类似于markdown的格式注明！
                """
            else:
                prompt = f"""
                现在有一个新执行的trace和一个交互task描述，我希望你看一下新执行的trace是否完成了交互task目标。

                以下是新执行的trace信息：
                {new_trace_info}
                以下是交互task描述信息：
                {scheme_case_info}

                注意：
                1.输出你判断的置信度，1表示判断非常确定，0表示判断非常不确定，0.5表示判断一般。
                返回格式：
                {{
                    "same": true/false,
                    "reason": "think step by step and write your reason here. Use the Chinese.",
                    "confidence": 0-1
                }}
                注意：请严格按照上方json格式进行返回！并且不要携带类似于markdown的格式注明！
                """
            ans = model([{"role": "user", "content": prompt}])
            try:
                ans = json.loads(ans)
                if ans.get('same', False):
                    return True, ans.get('reason', ''), ans.get('confidence', 0.5)
                else:
                    return False, ans.get('reason', ''), ans.get('confidence', 0.5)
            except Exception as e:
                return False, str(e), 0.5

def get_trace_origin_info(task_id, case_name):
    query = {
        "query": {
            "bool": {
                "must": [
                    {
                        "term": {
                            "autotest_info.task_id": task_id
                        }
                    },
                    {
                        "term": {
                            "autotest_info.case_name.keyword": case_name
                        }
                    }
                ],
                "must_not": [],
                "should": [],
                "filter": []
            }
        }
    }
    
    res = client.search(index="mtrekker", body=query, headers=headers)
    return res

def get_trace_ground_truth_info(case_name):
    query = {
        "query": {
            "bool": {
                "must": [
                    {
                        "term": {
                            "case_name.keyword": case_name
                        }
                    }
                ],
                "must_not": [],
                "should": [],
                "filter": []
            }
        }
    }
    
    res = client.search(index="stabex_trace_stable_reference", body=query, headers=headers)
    return res