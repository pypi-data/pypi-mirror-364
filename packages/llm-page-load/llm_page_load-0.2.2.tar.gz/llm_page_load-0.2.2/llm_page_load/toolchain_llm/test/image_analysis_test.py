from langchain.chat_models.base import BaseChatModel
from langchain.llms.utils import enforce_stop_tokens
from typing import Any, Coroutine, List, Optional
from langchain.schema import (
    BaseMessage,
    ChatResult,
    HumanMessage,
    ChatGeneration,
    AIMessage
)
from langchain.callbacks.manager import (
    AsyncCallbackManagerForLLMRun,
    CallbackManagerForLLMRun,
)
import requests
import json
import base64
from langchain.chat_models import ChatOpenAI
from service.coe_analysis.config_reader import get_kms
from utils import GPT35NAME


def url_to_base64(url):
    response = requests.get(url)
    image_bytes = response.content
    image_base64 = base64.b64encode(image_bytes).decode('utf-8')
    return image_base64


class ChatGLM(BaseChatModel):
    max_token: int = 10000
    temperature: float = 0.1
    top_p = 0.9
    host = 'http://10.164.6.121:8414'
    history = []

    @property
    def _llm_type(self) -> str:
        return "ChatGLM"

    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        # headers中添加上content-type这个参数，指定为json格式
        headers = {'Content-Type': 'application/json'}
        data = json.dumps({
            'prompt': prompt,
            'temperature': self.temperature,
            'history': self.history,
            'max_length': self.max_token
        })
        response = requests.post(f"{self.host}", headers=headers, data=data)
        if response.status_code != 200:
            return "获取结果失败"
        resp = response.json()
        if stop is not None:
            response = enforce_stop_tokens(response, stop)
        self.history = self.history+[[None, resp['response']]]
        return resp['response']

    def call_with_image(self, prompt, image_path, stop=None):
        headers = {'Content-Type': 'application/json'}
        data = json.dumps({
            'prompt': prompt,
            'image': url_to_base64(image_path),
            'temperature': self.temperature,
            'history': self.history,
            'max_length': self.max_token
        })
        response = requests.post(f"{self.host}", headers=headers, data=data)
        if response.status_code != 200:
            return "获取结果失败"
        resp = response.json()
        if stop is not None:
            response = enforce_stop_tokens(response, stop)
        self.history = self.history+[[None, resp['response']]]
        return resp['response']

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
    ) -> ChatResult:
        answer = [self._call(prompt=i.content, stop=stop) for i in messages]
        generations = [ChatGeneration(message=AIMessage(content=i)) for i in answer]
        return ChatResult(generations=generations, llm_output={"model_name": 'chatglm'})

    def _agenerate(self, messages: List[BaseMessage], stop: List[str] = None,
                   run_manager: AsyncCallbackManagerForLLMRun = None) -> Coroutine[Any, Any, ChatResult]:
        return None


if __name__ == '__main__':
    OPENAI_API_BASE = 'https://aigc.sankuai.com/v1/openai/native'
    OPENAI_API_KEY = get_kms('FRIDAY_APPID')
    model_name = GPT35NAME
    # model_name = 'gpt-4'
    temperature = 0.01
    max_retries = 6
    request_timeout = 60
    llm = ChatOpenAI(model_name=model_name,
                     openai_api_base=OPENAI_API_BASE,
                     openai_api_key=OPENAI_API_KEY,
                     verbose=True,
                     temperature=temperature,
                     request_timeout=request_timeout,
                     max_retries=max_retries)
    ans = llm.generate([[HumanMessage(content='你好')]])
    print(ans)
    text = ans.generations[0][0].text
    print(text)
