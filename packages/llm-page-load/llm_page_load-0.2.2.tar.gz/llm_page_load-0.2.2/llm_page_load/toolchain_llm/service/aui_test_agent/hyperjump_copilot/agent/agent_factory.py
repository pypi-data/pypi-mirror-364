import logging
from typing import Optional

from service.aui_test_agent.hyperjump_copilot.agent.friday_agent import FridayAgent
from service.aui_test_agent.hyperjump_copilot.agent.chatbot_agent import ChatBotFridayAgent
from service.aui_test_agent.hyperjump_copilot.agent.ui_case_agent import UICaseFridayAgent
from service.aui_test_agent.hyperjump_copilot.agent.mini_program_agent import MiniProgramFridayAgent
from service.aui_test_agent.hyperjump_copilot.agent.natural_language_agent import NaturalLanguageFridayAgent

class AgentFactory:
    """
    Agent工厂类，用于创建和管理各种Agent
    """
    
    def __init__(self, model_name: str = 'gpt-4o-2024-08-06'):
        """
        初始化Agent工厂
        
        Args:
            model_name: 使用的模型名称
        """
        self.model_name = model_name
        self.logger = logging.getLogger(self.__class__.__name__)
        self.agents = {}  # 存储已创建的Agent实例
        
    def create_agent(self, agent_type: str, operator: str = "default_user") -> FridayAgent:
        """
        创建指定类型的Agent
        
        Args:
            agent_type: Agent类型，可选值: chatbot, ui_case, mini_program, natural_language
            operator: 操作者名称
            
        Returns:
            创建的Agent实例
        """
        agent_key = f"{agent_type}_{operator}"
        
        # 如果已经创建过相同配置的Agent，直接返回
        if agent_key in self.agents:
            return self.agents[agent_key]
        
        # 根据类型创建不同的Agent
        if agent_type == "chatbot":
            agent = ChatBotFridayAgent(self.model_name, operator)
        elif agent_type == "ui_case":
            agent = UICaseFridayAgent(self.model_name, operator)
        elif agent_type == "mini_program":
            agent = MiniProgramFridayAgent(self.model_name, operator)
        elif agent_type == "natural_language":
            agent = NaturalLanguageFridayAgent(self.model_name, operator)
        else:
            raise ValueError(f"Unsupported agent type: {agent_type}")
        
        # 存储创建的Agent
        self.agents[agent_key] = agent
        self.logger.info(f"Created agent of type {agent_type} for operator {operator}")
        
        return agent
    
    def create_chatbot_agent(self, operator: str = "default_user") -> ChatBotFridayAgent:
        """
        创建ChatBotAgent并注册专业领域Agent
        
        Args:
            operator: 操作者名称
            
        Returns:
            创建的ChatBotAgent实例
        """
        # 创建ChatBotAgent
        chatbot_agent = self.create_agent("chatbot", operator)
        
        # 创建并注册专业领域Agent
        ui_case_agent = self.create_agent("ui_case", operator)
        mini_program_agent = self.create_agent("mini_program", operator)
        natural_language_agent = self.create_agent("natural_language", operator)
        
        # 注册专业领域Agent
        chatbot_agent.register_agent("ui_case", ui_case_agent)
        chatbot_agent.register_agent("mini_program", mini_program_agent)
        chatbot_agent.register_agent("natural_language", natural_language_agent)
        
        return chatbot_agent
    
    def get_agent(self, agent_type: str, operator: str = "default_user") -> Optional[FridayAgent]:
        """
        获取已创建的Agent
        
        Args:
            agent_type: Agent类型
            operator: 操作者名称
            
        Returns:
            Agent实例，如果不存在则返回None
        """
        agent_key = f"{agent_type}_{operator}"
        return self.agents.get(agent_key)
    
    def close_all_agents(self) -> None:
        """
        关闭所有Agent的会话
        """
        for agent in self.agents.values():
            agent.clear_history()
        
        self.agents = {}
        self.logger.info("Closed all agent sessions")