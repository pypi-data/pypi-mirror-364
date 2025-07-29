import logging
import traceback
from typing import List, Dict, Any, Optional
from openai import OpenAI

# 导入 Friday 和 FridayVision 类
try:
    from llmcore_sdk.models import Friday, FridayVision
except ImportError:
    print("警告: llmcore_sdk 未找到，请确保已正确安装。")
    # 简单的占位符类，方便代码结构
    class Friday:
        def __init__(self, *args, **kwargs):
            self.last_cost = 0
            self.last_response = {}
            self.prompt_tokens = 0
            self.completion_tokens = 0
            raise ImportError("llmcore_sdk.models.Friday 未找到")

        def __call__(self, *args, **kwargs):
            raise NotImplementedError
            
        def complex_chat(self, *args, **kwargs):
            raise NotImplementedError

    class FridayVision(Friday):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

# 配置日志
logger = logging.getLogger(__name__)

class LLMClient:
    """简化版的大语言模型客户端，用于调用 Friday 和 FridayVision API。"""
    
    def __init__(self, log_level=logging.INFO):
        """
        初始化 LLMClient。
        
        Args:
            log_level: 日志级别，默认为 logging.INFO
        """
        # 配置日志
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        self.logger = logging.getLogger("LLMClient")
        
    def text_request(
        self, 
        prompt: str, 
        model_name: str = "gpt-4o-2024-05-13", 
        max_tokens: int = 256, 
        direction: str = "LLMClient",
        functions: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """
        发送纯文本请求到 LLM。
        
        Args:
            prompt: 用户输入的提示文本
            model_name: 模型名称
            max_tokens: 最大生成 token 数
            direction: 请求方向标识
            functions: 可选的函数定义列表
            
        Returns:
            str: 模型返回的响应文本
        """
        self.logger.info(f"[MODEL]={model_name}")
        
        try:
            # 创建 Friday 实例
            model = Friday(
                model_name, 
                max_tokens=max_tokens, 
                direction=direction,
                functions=functions
            )
            
            # 发送请求
            messages = [{"role": "user", "content": prompt}]
            response = model(messages)
            
            # 记录成本信息
            self.logger.info(f"[COST]={model.last_cost}")
            return response
            
        except Exception as e:
            self.logger.error(f"请求模型 {model_name} 时出错: {e}")
            traceback.print_exc()
            raise
    
    def complex_chat(
        self, 
        messages: List[Dict[str, Any]], 
        model_name: str = "gpt-4o-2024-05-13", 
        max_tokens: int = 256, 
        direction: str = "LLMClient",
        response_format: Optional[Dict[str, str]] = None
    ) -> str:
        """
        发送复杂对话请求到 LLM。
        
        Args:
            messages: 消息列表，包含角色和内容
            model_name: 模型名称
            max_tokens: 最大生成 token 数
            direction: 请求方向标识
            response_format: 可选的响应格式，如 {"type": "json_object"}
            
        Returns:
            str: 模型返回的响应文本
        """
        self.logger.info(f"[MODEL]={model_name}")
        
        try:
            # 创建 Friday 实例
            model = Friday(
                model_name, 
                max_tokens=max_tokens, 
                direction=direction
            )
            
            # 发送请求
            kwargs = {}
            if response_format:
                kwargs["response_format"] = response_format
                
            response = model.complex_chat(messages, **kwargs)
            
            # 记录成本信息
            self.logger.info(f"[COST]={model.last_cost}")
            return response
            
        except Exception as e:
            self.logger.error(f"请求模型 {model_name} 时出错: {e}")
            traceback.print_exc()
            raise
    
    def vision_request(
        self, 
        prompt_or_messages, 
        image_path_or_model_name=None, 
        model_name: str = "anthropic.claude-3.7-sonnet", 
        max_tokens: int = 256, 
        direction: str = "LLMCORE-PTEST",
        use_s3_image: bool = True,
        temperature: float = 0.1
    ) -> str:
        """
        发送包含图像的多模态请求到 LLM。
        
        支持两种调用方式：
        1. vision_request(prompt, image_path, model_name, ...) - 传递字符串提示词和图片路径
        2. vision_request(messages, model_name, ...) - 传递消息列表
        
        Args:
            prompt_or_messages: 提示词字符串或消息列表
            image_path_or_model_name: 图片路径（第一种调用方式）或模型名称（第二种调用方式）
            model_name: 模型名称
            max_tokens: 最大生成 token 数
            direction: 请求方向标识
            use_s3_image: 是否使用 S3 图像处理
            temperature: 温度参数
            
        Returns:
            str: 模型返回的响应文本
        """
        self.logger.info(f"[MODEL]={model_name}")
        
        try:
            # 创建 FridayVision 实例
            model = FridayVision(
                model=model_name, 
                max_tokens=max_tokens, 
                direction=direction,
                temperature=temperature
            )
            
            # 判断调用方式并构建messages
            if isinstance(prompt_or_messages, str):
                # 第一种调用方式：vision_request(prompt, image_path, ...)
                prompt = prompt_or_messages
                image_path = image_path_or_model_name
                
                # 构建messages格式 - Friday API格式
                messages = [
                    {
                        "role": "user",
                        "content": prompt,
                        "image_url": image_path
                    }
                ]
            else:
                # 第二种调用方式：vision_request(messages, model_name, ...)
                messages = prompt_or_messages
                # 如果第二个参数是字符串且不是图片路径，则可能是模型名称
                if isinstance(image_path_or_model_name, str) and not image_path_or_model_name.endswith(('.png', '.jpg', '.jpeg')):
                    model_name = image_path_or_model_name
                
                # 修复messages格式，确保符合Friday API要求
                for message in messages:
                    if isinstance(message, dict) and "content" in message:
                        content = message["content"]
                        # 如果content是列表，需要转换为Friday API格式
                        if isinstance(content, list):
                            # 提取文本内容
                            text_content = ""
                            image_urls = []
                            for item in content:
                                if isinstance(item, dict):
                                    if item.get("type") == "text":
                                        text_content += item.get("text", "")
                                    elif item.get("type") == "image_url":
                                        img_url = item.get("image_url", {}).get("url", "")
                                        if img_url:
                                            image_urls.append(img_url)
                            
                            # 转换为Friday API格式
                            message["content"] = text_content
                            if image_urls:
                                if len(image_urls) == 1:
                                    message["image_url"] = image_urls[0]
                                else:
                                    message["image_url"] = image_urls
            
            # 发送请求
            response = model.complex_chat(messages)
            
            # 记录成本信息
            self.logger.info(f"[COST]={model.last_cost}")
            return response
        except Exception as e:
            self.logger.error(f"请求模型 {model_name} 时出错: {e}")
            traceback.print_exc()
            raise

# 示例用法
if __name__ == "__main__":
    client = LLMClient()
    
    # 示例 1: 使用函数调用能力
    functions = [{
        "name": "say_hello", 
        "description": "打招呼", 
        "parameters": {
            "type": "object",
            "properties": {"who": {"type": "string", "description": "你是谁"}},
            "required": ["who"]
        }
    }]
    
    # 测试 text_request (对应示例中的 Friday 直接调用)
    try:
        response = client.text_request(
            prompt="你好", 
            model_name="gpt-4o-2024-05-13",
            functions=functions
        )
        print(f"文本请求响应: {response}")
    except Exception as e:
        print(f"文本请求失败: {e}")
    
    # 测试 complex_chat (对应示例中的 Friday.complex_chat)
    try:
        response = client.complex_chat(
            messages=[{"role": "user", "content": "你好"}],
            model_name="gpt-4o-2024-05-13"
        )
        print(f"对话请求响应: {response}")
    except Exception as e:
        print(f"对话请求失败: {e}")
    
    # 测试 vision_request (对应示例中的 FridayVision.complex_chat)
    try:
        response = client.vision_request(
            "你好，这是什么图片", 
            "https://s3plus.vip.sankuai.com/v1/mss_8122b41e49f949ed966dc671c9211129/issue/coe-files/2024-05-21-144600-b6417b5e-ac30-420c-b740-56cc9a3b7dcf__image.png",
            model_name="gpt-4o-2024-05-13"
        )
        print(f"视觉请求响应: {response}")
    except Exception as e:
        print(f"视觉请求失败: {e}")


