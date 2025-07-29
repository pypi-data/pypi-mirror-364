from service.stabex_trace_diff.trace_diff import compare_trace, set_trace_as_ground_truth
from service.app_traversal.es_client import client, headers
from llmcore_sdk.models import Friday, FridayVision
import json
import requests
import os
import traceback
import time
from PIL import Image
import io

# 团购下单链路（频道页翻页）✅
# 团购下单链路（列表页场景）✅
# 团购下单链路（特团场景） ✅
# 团购下单链路（垂搜场景）✅
# 团购下单链路（频道页跳团购）✅
# 预订浮层链路（ktv预订场景）✅
# 团购下单链路（频道页场景）✅
# 预付商品下单链路（预付下单）✅
# 泛商品下单链路（泛商品场景）✅





# taskid: 691708 691704
# jobid: 352885


def get_trace_pages_info(case_name):
    query = {
        "query": {
            "bool": {
                "must": [
                    {
                        "term": {
                            "match_case_name.keyword": case_name
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

def get_page_match_info(match_case_name, match_page_name):
    """
    通过match_case_name和match_page_name查询stabex_trace_stable_reference索引中是否有此记录。
    返回ES原始结果。
    """
    query = {
        "query": {
            "bool": {
                "must": [
                    {"term": {"match_case_name.keyword": match_case_name}},
                    {"term": {"match_page_name.keyword": match_page_name}}
                ],
                "must_not": [],
                "should": [],
                "filter": []
            }
        }
    }
    res = client.search(index="stabex_trace_stable_reference", body=query, headers=headers)
    return res


def get_trace_origin_info(task_id, case_name):
    print("当前taskid与casename: ", task_id, case_name)
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


if __name__ == "__main__":
    # res = get_trace_pages_info("团购下单链路（频道页选中神券）")
    # print(res)
    # exit()
    mllm_api = FridayVision(
        model="gemini-2.5-pro-preview-03-25",
        max_tokens=4096,
        temperature=0.01,
        direction="trace_page_match"
    )
    case_names = [
        "团购下单链路（频道页跳团购）",
        "预订浮层链路（ktv预订场景）",
        "团购下单链路（频道页选中神券）",
        "泛商品下单链路（泛商品场景）",
        "团购下单链路（频道页场景）",
        "预付商品下单链路（预付下单）",
        "团购下单链路（频道页翻页）",
        "团购下单链路（列表页场景）",
        "团购下单链路（特团场景）",
        "团购下单链路（垂搜场景）"
    ]    
    task_id = input("请输入task_id: ")
    print("请选择case_name:")
    for i, case in enumerate(case_names, 1):
        print(f"{i}. {case}")
    
    # 获取用户选择
    while True:
        try:
            choice = int(input("请输入选项编号(1-10): "))
            if 1 <= choice <= len(case_names):
                case_name = case_names[choice-1]
                break
            else:
                print(f"请输入1到{len(case_names)}之间的数字")
        except ValueError:
            print("请输入有效的数字")
    res = get_trace_origin_info(task_id, case_name)
    if res['hits']['total']['value'] == 0:
        print('未匹配到此case')
    else:
        # 将trace的每个截图summary进行存储
        process_action_info = res['hits']['hits'][0]['_source'].get('process_action_info', [])
        print("\n可用的操作步骤:")
        for i, action in enumerate(process_action_info, 1):
            print(f"{i}. {action['action_info']}")
            print(f"   页面描述: {action['page_description']}\n")
        
        while True:
            try:
                action_choice = int(input("请选择要查看的操作步骤(1-{}): ".format(len(process_action_info))))
                if 1 <= action_choice <= len(process_action_info):
                    selected_action = process_action_info[action_choice-1]
                    print("\n选中的操作:")
                    print(f"操作信息: {selected_action['action_info']}")
                    print(f"页面描述: {selected_action['page_description']}")
                    print(f"操作图片: {selected_action['action_image']}")
                    print(f"结果图片: {selected_action['result_image']}")
                    break
                else:
                    print(f"请输入1到{len(process_action_info)}之间的数字")
            except ValueError:
                print("请输入有效的数字")

        # 根据信息生成前后描述
        messages = []
        for i in range(2):
            messages.append({
                'role': 'user',
                'content': f'{i+1}th image',
                'image_url': selected_action['action_image'] if i == 0 else selected_action['result_image']
            })
            
        summary_prompt = f"""
You are a helpful assistant that analyzes user interactions with web pages. Given the following information:
1. The page screenshot before interaction (pre_page)
2. The page screenshot after interaction (post_page) 
3. The action taken (action):
{selected_action['action_info']}

Please provide a summary in the following JSON format:

{{
    "initial_page": {{
        "description": "Description of the page before interaction",
        "key_elements": ["List of important elements present"]
    }},
    "action": {{
        "type": "Type of action taken",
        "target": "Element that was interacted with",
        "details": "Additional details about the action"
    }},
    "resulting_page": {{
        "description": "Description of the page after interaction",
        "key_changes": ["List of significant changes"],
        "new_state": "Description of the new state"
    }},
    "purpose": "Explanation of the overall intent and outcome"
}}

Focus on capturing the key changes and user intent. Be specific but concise in your descriptions.
"""
        messages.append({
            'role':'user',
            'content': summary_prompt,
            'image_url': None
        })
        try:
            chat_response = mllm_api.complex_chat(messages, response_format={"type": "json_object"}, max_tokens=4096, use_s3_image=True, timeout=240)
            if chat_response is not None and chat_response != "":
                print(chat_response)
                page_name = input("请输入当前页面名称：")
                # 进行落库
                page_match_info = {
                    "match_case_name": case_name,
                    "match_page_name": page_name,
                    "action_summary": chat_response,
                    "origin_selected_action": {
                        "task_id": task_id,
                        "case_name": case_name,
                        "action": selected_action
                    }
                }
                # same_record = get_page_match_info(case_name, page_name)
                # if same_record['hits']['total']['value'] == 0:
                #     print('未匹配到此case')
                #     client.index(index="stabex_trace_stable_reference", body=page_match_info)
                # else:
                #     print('已存在此case记录，更新存储信息')
                #     body = {
                #         'doc': page_match_info
                #     }
                #     client.update(index="stabex_trace_stable_reference", id=same_record['hits']['hits'][0]['_id'], body=body)
                client.index(index="stabex_trace_stable_reference", body=page_match_info)
            else:
                print(f"大模型请求: 请求大模型失败, 回复是 {chat_response}" )
        except Exception as e:
            print(traceback.print_exc())
        
