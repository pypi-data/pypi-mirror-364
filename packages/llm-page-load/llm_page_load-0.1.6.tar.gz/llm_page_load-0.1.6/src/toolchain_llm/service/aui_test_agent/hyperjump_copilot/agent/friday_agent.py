import logging
import uuid
from typing import Dict, Any, List, Optional, Union, Tuple
from llmcore_sdk.models.friday import Friday
from service.aui_test_agent.hyperjump_copilot.es_storaget import ChatMessage
import json
# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class FridayAgent:
    """
    使用Friday模型的Agent类，统一使用Friday模型调用方式
    """
    
    def __init__(self, model_name: str = 'gpt-4o-2024-08-06', operator: str = "default_user",
                 prompt: str = None, tools: List[Dict[str, Any]] = []):
        """
        初始化FridayAgent
        
        Args:
            model_name: 使用的模型名称
            operator: 操作者名称
            prompt: 系统提示词
            tools: 工具列表
        """
        self.model_name = model_name
        self.operator = operator
        self.logger = logging.getLogger(self.__class__.__name__)
        self.session_id = f"session-{uuid.uuid4().hex[:8]}"
        self.chat_storage = {
            "chat_history": []
        }
        self.prompt = prompt
        self.tools = tools
        
    def send_message(self, 
                    message: str, 
                    role: str = 'user',
                    prompt: str = None,
                    tools: List[Dict[str, Any]] = None,
                    max_tokens: int = 2048) -> Tuple[str, Dict[str, Any]]:
        """
        发送消息到Friday模型
        
        Args:
            message: 要发送的消息内容
            role: 消息角色，默认为'user'
            prompt: 系统提示词，如不提供则使用空字符串
            tools: 工具列表，如不提供则使用None
            max_tokens: 最大生成token数
            
        Returns:
            模型生成的回复内容和完整响应
        """
        # 添加消息到历史记录
        self.chat_storage["chat_history"].append(ChatMessage(role=role, content=message))
        
        # 准备消息列表
        messages = [{'role': 'system', 'content': self.prompt or ""}] + self.get_history_message()
        
        # 初始化Friday模型
        model = Friday(model=self.model_name, max_tokens=max_tokens, functions=self.tools)
        
        self.logger.info(f"Sending message to Friday model: {message[:50]}...")
        
        try:
            # 调用Friday模型
            completion = model(messages)
            response = model.last_response
            
            # 处理模型响应
            if "data" in response:
                assistant_message = response["data"]["result"]
                self.chat_storage["chat_history"].append(ChatMessage(role="assistant", content=assistant_message))
                return assistant_message, response
            else:
                self.logger.error(f"Unexpected response format: {response}")
                return "", response
        except Exception as e:
            self.logger.error(f"Error sending message to Friday model: {str(e)}")
            raise
    
    def get_history_message(self) -> List[Dict[str, Any]]:
        """
        获取历史消息
        
        Returns:
            历史消息列表，过滤掉content为空的消息
        """
        return [{"role": msg.role, "content": msg.content} for msg in self.chat_storage["chat_history"] if msg.content]
    
    def clear_history(self) -> None:
        """
        清空历史消息
        """
        self.chat_storage["chat_history"] = []
        self.logger.info("Chat history cleared")
