import requests
import json
import logging
import uuid
from typing import Dict, Any, Optional, Union, List
from urllib.parse import urljoin

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class BaseAgent:
    """
    Agent基类，用于与TestGenius API进行交互
    支持创建会话和发送消息
    """
    
    def __init__(self, base_url: str = "https://testgenius.sankuai.com", sub_agent_id:str=None, operator:str="default_user"):
        """
        初始化Agent，自动创建会话
        
        Args:
            base_url: TestGenius API的基础URL
            sub_agent_id: 子Agent ID，如不提供则自动生成
            operator: 操作者名称
        """
        self.base_url = base_url
        self.logger = logging.getLogger(self.__class__.__name__)
        self.session_id = None
        self.sub_agent_id = sub_agent_id or f"agent-{uuid.uuid4().hex[:8]}-0"
        self.operator = operator
        self.headers = {"Token": "3ae05b2965324357a869943d7ec13bcf"}
    
        # 自动创建会话
        self._auto_create_session()

    def _auto_create_session(self) -> None:
        """
        自动创建会话
        """
        session_name = f"Session-{uuid.uuid4().hex[:6]}"
        self.create_session(self.operator, self.sub_agent_id, session_name)

    def create_session(self, operator: str, sub_agent_id: str, name: str) -> Dict[str, Any]:
        """
        创建新的会话
        
        Args:
            operator: 操作者名称
            sub_agent_id: 子Agent ID
            name: 会话名称
            
        Returns:
            API响应的JSON数据
        """
        self.sub_agent_id = sub_agent_id
        url = urljoin(self.base_url, f"/openApi/rpa/newOpenSession?subAgentId={sub_agent_id}")
        
        payload = {
            "operator": operator,
            "subAgentId": sub_agent_id,
            "name": name
        }
        
        self.logger.info(f"Creating session with payload: {payload}")
        
        try:
            response = requests.post(url, json=payload, headers=self.headers)
            response.raise_for_status()
            result = response.json()
            
            if "data" in result and "sessionId" in result["data"]:
                self.session_id = result["data"]["sessionId"]
                self.logger.info(f"Session created successfully with ID: {self.session_id}")
            else:
                self.logger.error(f"Failed to get sessionId from response: {result}")
            
            return result
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error creating session: {str(e)}")
            raise
    
    def send_message(self, 
                    message: str, 
                    operator: str = None,
                    multi_count: int = 3, 
                    stream: bool = False) -> Union[List[Dict[str, Any]], Dict[str, Any]]:
        """
        向已创建的会话发送消息
        
        Args:
            message: 要发送的消息内容
            operator: 操作者名称，如不提供则使用初始化时的operator
            multi_count: 多轮对话数量
            stream: 是否使用流式响应
            
        Returns:
            简化后的响应数据，直接返回choices数组或完整响应
        """
        if not self.session_id or not self.sub_agent_id:
            self._auto_create_session()
        
        operator = operator or self.operator
        url = urljoin(self.base_url, f"/openApi/rpa/openChat?subAgentId={self.sub_agent_id}")
        
        payload = {
            "subAgentId": self.sub_agent_id,
            "sessionId": self.session_id,
            "operator": operator,
            "multiCount": multi_count,
            "stream": stream,
            "message": {
                "role": "user",
                "content": message
            }
        }
        
        self.logger.info(f"Sending message with payload: {payload}")
        
        try:
            response = requests.post(url, json=payload, headers=self.headers)
            response.raise_for_status()
            
            if stream:
                # 处理流式响应
                chunks = []
                for line in response.iter_lines():
                    if line:
                        decoded_line = line.decode('utf-8')
                        if decoded_line.startswith('data: '):
                            data = json.loads(decoded_line[6:])
                            chunks.append(data)
                            self.logger.debug(f"Received stream chunk: {data}")
                return chunks
            else:
                # 处理普通响应
                result = response.json()

                # 简化返回结果，只返回choices数组
                if "data" in result and "choices" in result["data"]:
                    return result["data"]["choices"]
                return result
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error sending message: {str(e)}")
            raise
    
    def close_session(self) -> None:
        """
        关闭当前会话（如果API支持）
        """
        # 如果API支持关闭会话，可以在这里实现
        self.session_id = None
        self.logger.info("Session closed")


# 使用示例
if __name__ == "__main__":
    # 创建Agent实例，会自动创建会话
    agent = BaseAgent(operator="machongjian",sub_agent_id='agent-45e36dda-0')
    
    # 发送消息，直接获取choices数组
    choices = agent.send_message("imeituan://www.meituan.com/gc/mrn?mrn_biz=gcbu&mrn_entry=beauty-handsome-homepage&mrn_component=mrn-gc-handsomebeauty&templateKey=nib.general.beauty_merge&mrn_min_version=0.0.30")
    print(f"Response choices: {choices}")
