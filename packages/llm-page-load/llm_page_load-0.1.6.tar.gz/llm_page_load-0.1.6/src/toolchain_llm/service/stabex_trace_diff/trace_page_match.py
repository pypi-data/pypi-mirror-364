from service.app_traversal.es_client import client, headers
from service.stabex_trace_diff.trace_diff import get_trace_origin_info
from llmcore_sdk.models import FridayVision
import traceback
import re
import pandas as pd
import glob
import os
import json
import requests

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

def parse_json_response(response_str):
    """
    清理和解析带有```json包裹的json字符串，返回解析后的对象。
    解析失败时抛出异常。
    """
    cleaned_response = response_str
    if cleaned_response.startswith("```json"):
        cleaned_response = cleaned_response[len("```json"):].lstrip()
    if cleaned_response.endswith("```"):
        cleaned_response = cleaned_response[:-len("```")].rstrip()
    cleaned_response = cleaned_response.strip()
    
    # Handle escaped quotes by replacing \\" with \"
    cleaned_response = cleaned_response.replace('\\"', '"')
    
    return json.loads(cleaned_response)

def page_match(task_id, case_name, action_index):
    """
    Predict the action description for a given task_id, case_name and action_index.
    
    Args:
        task_id (str): The task ID
        case_name (str): The case name
        action_index (int): The index of the action to analyze (1-based)
        
    Returns:
        dict: The predicted action description in JSON format
    """
    try:
        # Initialize the LLM model
        mllm_api = FridayVision(
            model="gpt-4.1",
            max_tokens=4096,
            temperature=0.01,
            direction="trace_page_match"
        )
        
        res = get_trace_origin_info(task_id, case_name)
        
        if res['hits']['total']['value'] == 0:
            return {"success": False, "error": "No matching case found"}
            
        # Get the selected action
        process_action_info = res['hits']['hits'][0]['_source'].get('process_action_info', [])
        if not 1 <= action_index <= len(process_action_info):
            return {"success": False, "error": f"Invalid action_index. Must be between 1 and {len(process_action_info)}"}
            
        selected_action = process_action_info[action_index-1]
        
        # Prepare messages for LLM
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
            'role': 'user',
            'content': summary_prompt,
            'image_url': None
        })
        
        # Get prediction from LLM
        chat_response = mllm_api.complex_chat(
            messages, 
            response_format={"type": "json_object"}, 
            max_tokens=4096, 
            use_s3_image=True, 
            timeout=240
        )
        
        if chat_response is None or chat_response == "":
            return {"success": False, "error": "Failed to get response from LLM"}

        # 进行匹配
        trace_pages_info = get_trace_pages_info(case_name)
        
        if not trace_pages_info or trace_pages_info.get('hits', {}).get('total', {}).get('value', 0) == 0:
            return {"success": False, "error": "no reference pages to match against"} # No reference pages to match against or error in fetching

        hits = trace_pages_info.get('hits', {}).get('hits', [])
        if not hits:
            return {"success": False, "error": "no hits found"} # No hits found


        all_pages = ""
        for hit in hits:
            source = hit.get('_source', {})
            action_summary_str = source.get('action_summary')
            match_page_name = source.get('match_page_name')
            all_pages += f"### match_page_name: \n {match_page_name} ###\n"
            all_pages += f"### action_summary: \n {action_summary_str} ###\n"
        match_prompt = (
            f"""
你是一个页面操作匹配助手。你的任务是分析当前操作与历史记录中的页面操作是否匹配。

输入信息：
1. 当前操作的action_summary:
{json.dumps(chat_response, ensure_ascii=False, indent=2)}

2. 历史记录中的页面操作列表:
{all_pages}

任务要求：
1. 将当前操作的action_summary与历史记录中的每个action_summary进行详细对比
2. 判断是否有匹配的页面操作
3. 如果找到匹配，返回最相关的一个match_page_name
4. 如果没有匹配，返回"No"

输出要求：
你必须且只能返回以下两种JSON格式之一：
1. 找到匹配时：
{{
    "match_page_name": "具体的页面名称"
}}

2. 未找到匹配时：
{{
    "match_page_name": "No"
}}

重要说明：
1. 店铺和商品可能不同，我们关注的是页面操作类型和页面类型
2. 页面内容不需要完全一致
3. 你的回复必须且只能是上述JSON格式，不能包含任何其他内容
4. 确保输出的JSON格式完全正确，可以被json.loads()解析
"""
        )
        messages = []
        messages.append({
            'role': 'user',
            'content': match_prompt,
            'image_url': None
        })
        chat_response = mllm_api.complex_chat(
            messages, 
            response_format={"type": "json_object"},
            max_tokens=4096, 
            use_s3_image=True, 
            timeout=240
        )
        if chat_response is None or chat_response == "":
            return {"error": "Failed to get response from LLM"}
        print(chat_response)
        # 使用parse_json_response解析LLM返回
        try:
            match_result = parse_json_response(chat_response)
        except Exception as e:
            return {"success": False, "error": f"LLM返回内容解析失败: {str(e)}", "raw_response": chat_response}
        return {"success": True, "match_page_name": match_result.get("match_page_name", "")}
        
    except Exception as e:
        return {"success": False, "error": f"Error occurred: {str(e)}", "traceback": traceback.format_exc()}


if __name__ == "__main__":
    # page_match("693190", "团购下单链路（特团场景）", 1)

    # 读取JSON文件而不是Excel文件
    json_file = "./marked_data_224_full_1.json"
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data_list = json.load(f)
        
        for j, item in enumerate(data_list):
            case_name = item.get('case_name')
            video_action_data = item.get('video_action_data')
            
            if not case_name or not video_action_data:
                print(f"数据项缺少case_name或video_action_data")
                continue
            
            # 如果video_action_data是字符串，尝试解析为JSON
            if isinstance(video_action_data, str):
                try:
                    video_action_data = json.loads(video_action_data)
                except json.JSONDecodeError:
                    print(f"无法解析video_action_data为JSON：{video_action_data[:100]}...")
                    continue
            
            storage_path = video_action_data.get("storage_path", "")
            action_list = video_action_data.get("action_list", [])
            
            # 从storage_path提取task_id
            match = re.search(r'task_(\d+)', storage_path)
            if match:
                task_id = match.group(1)
                print(f"处理任务: {task_id}, 场景: {case_name}")
                
                for index, action in enumerate(action_list):
                    if action.get('marked_end_time', "") == "":
                        continue
                    # 调用API获取page_match的结果
                    try:
                        payload = {
                            "task_id": task_id,
                            "case_name": case_name,
                            "action_index": index+1
                        }
                        headers = {"Content-Type": "application/json"}
                        response = requests.post(
                            'http://localhost:8002/trace_compare/page_match',
                            json=payload,
                            headers=headers
                        )
                        if response.status_code == 200:
                            match_result = response.json()
                            # 将结果添加到action中，字段名称为page_name
                            try:
                                action['page_name'] = match_result.get("result", {}).get('match_page_name', "")
                            except Exception as e:
                                print(f"解析match_page_name时出错: {e}, 原始内容: {match_result}")
                                action['page_name'] = ""
                            print(f"第{index+1}个动作匹配结果: {action['page_name']}")
                        else:
                            print(f"API调用失败: {response.status_code}, {response.text}")
                    except Exception as e:
                        print(f"API调用出错: {e}")
                
                # 将修改后的数据写回JSON文件
                with open(json_file, 'w', encoding='utf-8') as f:
                    json.dump(data_list, f, ensure_ascii=False, indent=2)
            else:
                print(f"未能从storage_path提取task_id: {storage_path}")
    except Exception as e:
        print(f"处理JSON文件时出错: {e}")