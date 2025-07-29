import logging
import json
import re
from typing import Dict, Any, List, Optional, Tuple

from service.aui_test_agent.hyperjump_copilot.agent.friday_agent import FridayAgent

class ChatBotFridayAgent(FridayAgent):
    """
    ChatBot专用的FridayAgent，负责判断用户请求的复杂性，决定是直接回答还是启动完整的工作流
    """
    
    def __init__(self, model_name: str = 'gpt-4o-2024-08-06', operator: str = "default_user",
                 prompt: str = None, tools: List[Dict[str, Any]] = []):
        """
        初始化ChatBotFridayAgent
        
        Args:
            model_name: 使用的模型名称
            operator: 操作者名称
            prompt: 系统提示词
            tools: 工具列表
        """
        super().__init__(model_name, operator, prompt, tools)
        self.specialized_agents = {}
        self.current_agent = None
        
    def register_agent(self, agent_type: str, agent_instance: FridayAgent) -> None:
        """
        注册专业领域Agent
        Args:
            agent_type: Agent类型标识
            agent_instance: Agent实例
        """
        self.specialized_agents[agent_type] = agent_instance
        self.logger.info(f"Registered agent of type {agent_type}")
        
    def analyze_request(self, message: str, prompt: str = None) -> Dict[str, Any]:
        """
        分析用户请求，判断复杂性和类型
        Args:
            message: 用户消息
            prompt: 系统提示词
            
        Returns:
            包含请求分析结果的字典
        """
        # 使用LLM分析用户请求
        analysis_prompt = f"""你是一个专业的对话分发助手，负责识别用户请求类型并将其转发给合适的专业处理模块。
            # 职责
            - 判断用户请求的复杂性和类型
            - 简单请求（问候、闲聊）由你直接处理
            - 复杂请求转发给对应的专业模块处理
            - 拒绝不适当或有害的请求

            # 执行规则
            请分析以下用户请求，判断:
            1. 请求的复杂性（简单/复杂）
            - 简单请求：问候语、闲聊、基础信息咨询
            - 复杂请求：需要专业知识或工具支持的请求
            2. 如果是复杂请求，属于哪种专业类型:
            - ui_case: 视觉用例、UI测试相关,用于处理imetiuan或者dianping开头的页面链接
            - mini_program: 小程序用例相关
            - natural_language: 自然语言录入相关,用于处理ec链接和自然语言用例
            - other: 其他复杂类型
            3. 请求的置信度：你对分类判断的确信程度（0.0-1.0）
            当前用户请求: {message}
            以JSON格式返回结果,不要添加任何markdown标记:
            {{
            "complexity": "simple/complex",
            "type": "ui_case/mini_program/natural_language/other/none",
            "confidence": 0.0-1.0,
            "thought":"任务识别和对话分发的依据和思考"
            }}
            """
        response_text, response = self.send_message(analysis_prompt, prompt=prompt)
        try:
            # 尝试从内容中提取JSON
            json_match = re.search(r'\`\`\`json\n(.*?)\n\`\`\`|\`\`\`(.*?)\`\`\`|({.*})', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(1) or json_match.group(2) or json_match.group(3)
                analysis = json.loads(json_str)
            else:
                # 如果没有明确的JSON格式，尝试直接解析
                analysis = json.loads(response_text)
                
            return analysis
        except Exception as e:
            self.logger.error(f"Error parsing analysis result: {str(e)}")
            # 默认为简单请求
            return {"complexity": "simple", "type": "none", "confidence": 0.5}
    
    def process_request(self, message: str, prompt: str = None, tools: List[Dict[str, Any]] = None) -> Tuple[str, Dict[str, Any]]:
        """
        处理用户请求，根据分析结果决定是直接回答还是转发给专业Agent
        
        Args:
            message: 用户消息
            prompt: 系统提示词
            tools: 工具列表
            
        Returns:
            处理结果和完整响应
        """
        analysis = self.analyze_request(message, prompt)
        
        if analysis["complexity"] == "simple" or analysis["confidence"] < 0.7:
            # 简单请求或置信度低，直接由ChatBotAgent处理
            self.logger.info(f"Handling simple request directly: {message[:50]}...")
            self.current_agent = None
            return self.send_message(message, prompt=prompt, tools=tools)
        else:
            # 复杂请求，转发给专业Agent
            agent_type = analysis["type"]
            if agent_type in self.specialized_agents:
                self.logger.info(f"Forwarding request to {agent_type} agent: {message[:50]}...")
                self.current_agent = self.specialized_agents[agent_type]
                return self.current_agent.send_message(message, prompt=prompt, tools=tools)
            else:
                # 没有对应的专业Agent，由ChatBotAgent处理
                self.logger.warning(f"No specialized agent for {agent_type}, handling directly")
                self.current_agent = None
                return self.send_message(message, prompt=prompt, tools=tools)
    
    def continue_conversation(self, message: str, prompt: str = None, tools: List[Dict[str, Any]] = None) -> Tuple[str, Dict[str, Any]]:
        """
        继续当前对话，如果有活跃的专业Agent则转发给它
        
        Args:
            message: 用户消息
            prompt: 系统提示词
            tools: 工具列表
            
        Returns:
            处理结果和完整响应
        """
        if self.current_agent:
            return self.current_agent.send_message(message, prompt=prompt, tools=tools)
        else:
            return self.send_message(message, prompt=prompt, tools=tools)

if __name__ == '__main__':
    # 示例系统提示词
    example_prompt = "你是一个智能助手，可以回答用户的各种问题。"
    # 示例工具列表
    example_tools = []

    agent = ChatBotFridayAgent(prompt=example_prompt, tools=example_tools)
    agent.analyze_request('你好')

