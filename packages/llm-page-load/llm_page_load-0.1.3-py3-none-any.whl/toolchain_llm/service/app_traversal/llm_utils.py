import requests
from utils import logger
import time
import configparser

config = configparser.ConfigParser()
config.read('config/coe_server.conf', encoding='utf-8')
appkey = config['model']['OPENAI_API_KEY']

def claude_instant(prompt, temperature):
    '''
    写在这里防止其他组件使用4v
    '''
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {appkey}"
    }
    prompt = f'Human:{prompt} \n\nAssistant:'
    payload = {
        "model": "anthropic.claude-instant-v1",
        "temperature": temperature,
        "prompt": prompt,
        "max_tokens_to_sample": 1000
    }
    logger.info(f'开始执行claude_instant: {payload}')
    for _ in range(3):
        try:
            response = requests.post(
                "https://aigc.sankuai.com/v1/claude/aws/v1/complete",
                headers=headers,
                json=payload,
                timeout=180,
            )
            if response.status_code == 200:
                return response.json()['completion']
            elif response.status_code == 429:
                # 429为大模型接口达到调用频次上限，等待60s再次调用
                logger.info(f"HTTP {response.status_code}: {response.reason}")
                time.sleep(60)
            else:
                logger.info(f"HTTP {response.status_code}: {response.reason}")
                time.sleep(5)
        except Exception as e:
            logger.info(f"claude_instant请求出错")
            logger.info(f"Exception: {type(e)} {e}")
            time.sleep(5)
    return None

def get_node_description_by_llm(before_page_info, node_id, node_info):
    template = f"""
我将为你提供APP页面中的“页面文本信息”，其中是页面中每个节点的ID和文字。同时也会给你需要交互的“节点信息”，包括节点的ID和节点的文字。请根据“页面文本信息”，“节点信息”，结合上下文分析这个节点在页面上所有可能的UI交互含义。

---- “页面文本信息” ----
{before_page_info}
---- “节点信息” ----
ID: {node_id} Text: {node_info}

在做出预测时，你可以考虑页面元素的上下文/周边信息的关联。
请尽可能多地推测节点的UI功能。
"""
    chat_resp = claude_instant(template, 0.05)
    return chat_resp

def judging_rationality(node_description, page_description):
    template = f"""
你现在是一名专业的质量保证工程师。我需要你检查在APP页面上执行的交互操作结果是否满足预期。我将为你提供以下两条信息：
1.交互节点的交互预期可能性(当前被点击或交互的节点)
2.交互后页面的信息(点击或交互1所描述的节点后，页面显示的内容，内容为每个节点的type和text信息)
请判断交互后的页面显示内容是否符合交互节点本身的交互预期？注意，内容不需要满足全部的交互可能预期，只要满足其中的一种，我们便认为符合预期。

---- 交互节点的交互预期可能性 ----
{node_description}

---- 交互后页面的文字 ----
{page_description}

请一步步判断交互后的页面显示内容是否符合交互节点本身的交互预期？并将理由写在下方格式规定中的reason当中。注意，内容不需要满足全部的交互可能预期，只要满足其中的一种，我们便认为符合预期。
请返回一个可以被python的json.loads函数解析的JSON，按照以下格式：
'result': true(符合预期)/false(不符合预期), 'reason': '在这里提供一步步判断的原因，并确保使用中文。'
"""
    chat_resp = claude_instant(template, 0.01)
    return chat_resp