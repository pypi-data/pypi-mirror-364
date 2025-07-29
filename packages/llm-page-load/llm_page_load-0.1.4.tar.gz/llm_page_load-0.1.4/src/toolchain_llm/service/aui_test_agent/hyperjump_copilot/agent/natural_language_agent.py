import logging
from typing import Dict, Any, List, Tuple

from service.aui_test_agent.hyperjump_copilot.agent.friday_agent import FridayAgent

class NaturalLanguageFridayAgent(FridayAgent):
    """
    自然语言录入专用的FridayAgent
    """
    
    def __init__(self, model_name: str = 'gpt-4o-2024-08-06', operator: str = "default_user"):
        """
        初始化NaturalLanguageFridayAgent
        
        Args:
            model_name: 使用的模型名称
            operator: 操作者名称
        """
        super().__init__(model_name, operator)
        self.has_device = False
        self.current_state = "initial"  # 状态: initial, device_applying, device_ready, executing
    
    def process_by_state(self, message: str) -> str:
        """
        根据当前状态处理用户消息
        
        Args:
            message: 用户消息
            
        Returns:
            处理后的消息
        """
        if self.current_state == "initial":
            # 检查是否需要申请设备
            if "申请设备" in message or "申请一台设备" in message:
                self.current_state = "device_applying"
            return message
        
        elif self.current_state == "device_applying":
            # 正在申请设备，不需要特殊处理
            return message
        
        elif self.current_state == "device_ready":
            # 设备已就绪，检查用户是否要执行操作
            if "执行" in message or "操作" in message:
                self.current_state = "executing"
            return message
        
        elif self.current_state == "executing":
            # 正在执行操作，检查是否要退出
            if "退出" in message or "不需要了" in message or "回收" in message:
                self.current_state = "initial"
                self.has_device = False
            return message
        
        return message
    
    def send_message(self, 
                    message: str, 
                    role: str = 'user',
                    prompt: str = None,
                    tools: List[Dict[str, Any]] = None,
                    max_tokens: int = 2048) -> Tuple[str, Dict[str, Any]]:
        """
        重写send_message方法，添加状态处理
        
        Args:
            message: 要发送的消息内容
            role: 消息角色，默认为'user'
            prompt: 系统提示词，如不提供则使用空字符串
            tools: 工具列表，如不提供则使用None
            max_tokens: 最大生成token数
            
        Returns:
            模型生成的回复内容和完整响应
        """
        # 根据当前状态处理消息
        processed_message = self.process_by_state(message)
        
        # 调用父类的send_message方法
        response_text, response = super().send_message(processed_message, role, prompt, tools, max_tokens)
        
        # 根据响应更新状态
        self.update_state_from_response(response)
        
        return response_text, response
    
    def update_state_from_response(self, response: Dict[str, Any]) -> None:
        """
        根据响应更新状态
        
        Args:
            response: API响应
        """
        try:
            if "data" in response and "choices" in response["data"]:
                # 检查是否包含function call
                if "function_call" in response["data"]["choices"][0]["message"]:
                    function_name = response["data"]["choices"][0]["message"]["function_call"]["name"]
                    
                    if function_name == "apply_for_device":
                        self.current_state = "device_applying"
                    elif function_name == "reclaim_current_device":
                        self.current_state = "initial"
                        self.has_device = False
                    elif function_name == "apply_action":
                        # 如果是第一次执行操作，说明设备已就绪
                        if not self.has_device:
                            self.has_device = True
                            self.current_state = "device_ready"
                        else:
                            self.current_state = "executing"
                
                # 根据内容更新状态
                content = response["data"]["choices"][0]["message"]["content"]
                if "设备已经连接成功" in content:
                    self.current_state = "device_ready"
                    self.has_device = True
                elif "不好意思现在找不到执行机" in content:
                    self.current_state = "initial"
                    self.has_device = False
        except Exception as e:
            self.logger.error(f"Error updating state from response: {str(e)}")