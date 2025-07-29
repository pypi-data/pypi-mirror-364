import logging
import re
from typing import Dict, Any, List, Tuple

from service.aui_test_agent.hyperjump_copilot.agent.friday_agent import FridayAgent

class MiniProgramFridayAgent(FridayAgent):
    """
    小程序用例专用的FridayAgent
    """
    
    def __init__(self, model_name: str = 'gpt-4o-2024-08-06', operator: str = "default_user"):
        """
        初始化MiniProgramFridayAgent
        
        Args:
            model_name: 使用的模型名称
            operator: 操作者名称
        """
        super().__init__(model_name, operator)
        self.current_state = "initial"  # 状态: initial, collecting_info, generating, confirming
    
    def process_by_state(self, message: str) -> str:
        """
        根据当前状态处理用户消息
        
        Args:
            message: 用户消息
            
        Returns:
            处理后的消息
        """
        if self.current_state == "initial":
            # 检查消息中是否包含小程序ID
            app_id_match = re.search(r'小程序ID[是为:=\s]+([a-zA-Z0-9]+)', message)
            if app_id_match:
                self.current_state = "collecting_info"
            return message
        
        elif self.current_state == "collecting_info":
            # 检查是否已收集足够信息
            if "页面路径" in message or "path" in message.lower():
                self.current_state = "generating"
            return message
        
        elif self.current_state == "generating":
            # 已经在生成用例，更新状态为确认
            self.current_state = "confirming"
            return message
        
        elif self.current_state == "confirming":
            # 检查用户是否确认或要求重新生成
            if "重新生成" in message or "修改" in message:
                self.current_state = "generating"
            elif "符合" in message or "保存" in message or "确认" in message:
                self.current_state = "initial"  # 保存后重置状态
            
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
                content = response["data"]["choices"][0]["message"]["content"]
                
                # 检查是否包含function call
                if "function_call" in response["data"]["choices"][0]["message"]:
                    function_name = response["data"]["choices"][0]["message"]["function_call"]["name"]
                    
                    if function_name == "mini_program_case_generate":
                        self.current_state = "generating"
                    elif function_name == "save_mini_program_case":
                        self.current_state = "initial"  # 保存后重置状态
                
                # 根据内容更新状态
                if "请提供小程序ID" in content:
                    self.current_state = "collecting_info"
                elif "生成测试用例" in content and "是否符合预期" in content:
                    self.current_state = "confirming"
        except Exception as e:
            self.logger.error(f"Error updating state from response: {str(e)}")