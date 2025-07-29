# -*- coding: utf-8 -*-
from typing import Any, Dict, List, Optional, Union
from uuid import UUID
from langchain.chat_models import ChatOpenAI
from service.coe_analysis.coe_experience_service import create_experience
from langchain.schema.output import LLMResult
from service.coe_analysis.coe_store_service import sync_coe_result
from service.coe_analysis.crawler_data_service import sync_crawler_data
from service.coe_analysis.llm_sdk_importer import NameSpace
from service.coe_analysis.runners.loaders import Document
from abc import abstractmethod
from flask_socketio import emit
from service.lang_chain_utils.lion_client import client as lion
from service.lang_chain_utils.embedding import embed
from service.coe_analysis.config_reader import OPENAI_API_BASE, OPENAI_API_KEY
from service.coe_analysis.runners.retriver import LLMCallback
from service.coe_analysis.data_structure import Answer, COEResult, Experience, MetaMessage
from langchain.callbacks.base import BaseCallbackHandler
from utils import logger, get_now_str
import time
from llmcore_sdk.models.friday import Friday
import uuid
from service.coe_analysis.coe_thread_executor import coe_es_writer


def on_emit(event: str, message: Union[List, Dict, str]):
    '''
    向前端发送请求，这里指定向当前namespace发送请求
    emit函数会通过 flask.session.get('session_id')来确定长链接，此处不会发生广播
    '''
    emit(event, message, namespace=NameSpace)


class LLMChatCallback(BaseCallbackHandler):
    def __init__(self, chain_id: str):
        self.ack = True
        self.chain_id = chain_id
        self.token = ''

    def on_llm_start(
        self,
        serialized: Dict[str, Any],
        prompts: List[str],
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any,
    ) -> None:
        content = prompts[-1]
        logger.info(f'chat/new_ask : {content}')
        on_emit('chat/new_ask',
                {'ask': content, 'chain_id': uuid.uuid1().__str__()})
        return

    def on_llm_new_token(self, token: str, *, run_id: UUID,
                         parent_run_id: Union[UUID, None] = None,
                         **kwargs: Any) -> Any:
        self.token += token
        if (self.ack):
            logger.info(f'chat/new_token : {self.token}')
            on_emit('chat/new_token',
                    {'token': self.token, 'chain_id': self.chain_id})
            self.ack = False
            self.token = ''
        return super().on_llm_new_token(token, run_id=run_id,
                                        parent_run_id=parent_run_id, **kwargs)

    def on_llm_end(self, response: LLMResult, *, run_id: UUID, parent_run_id: UUID = None, **kwargs: Any) -> Any:
        logger.info(f'chat/new_token : {self.token}')
        on_emit('chat/new_token',
                {'token': self.token, 'chain_id': self.chain_id})
        return


class COEChatBaseRunner:
    def __init__(self, result_item: COEResult, _id: str, type: str):
        lion.fetch_config()
        self.result_item = result_item
        self._id = _id
        self.callback = LLMCallback(result_item=result_item, _id=_id)
        model_name = lion.config[f'{lion.app_name}.llm.model_name']
        temperature = lion.config[f'{lion.app_name}.coe.temperature']
        request_timeout = lion.config[f'{lion.app_name}.coe.request_timeout']
        max_retries = lion.config[f'{lion.app_name}.max_retries']
        self.llm = ChatOpenAI(model_name=model_name, streaming=True,
                              openai_api_base=OPENAI_API_BASE,
                              openai_api_key=OPENAI_API_KEY,
                              temperature=temperature,
                              request_timeout=request_timeout,
                              max_retries=max_retries)
        self.type = type
        self.chat_callback = LLMChatCallback(result_item.id)

    def sync(self, coe_id):
        sync_crawler_data(coe_id)

    @abstractmethod
    def pre_check(self) -> bool:
        pass

    @abstractmethod
    def load_retiver(self, coe_id):
        pass

    @abstractmethod
    def chat(self, text) -> bool:
        pass


ChatRunners: Dict[str, COEChatBaseRunner] = {}


class COEBaseRunner:
    '''每一个子任务都有一个Runner对应'''
    def make_answer(self, user: str, answer: str):
        '''在预校验的过程中写入answer，一般是不确定'''
        message = [MetaMessage('user', user),
                   MetaMessage('assistant', answer)]
        exp = create_experience(type=self.result_item.type,
                                coe_id=self.result_item.coe_id,
                                task_id=self.result_item.task_id,
                                message_list=message)
        self.result_item.answer_message.append(Answer(exp_id=exp.id))

    def __init__(self, result_item: COEResult, _id: str):
        lion.fetch_config()
        self.result_item = result_item
        self.callback = LLMCallback(result_item=result_item, _id=_id)
        model_name = lion.config[f'{lion.app_name}.coe.model_name']
        temperature = lion.config[f'{lion.app_name}.coe.temperature']
        request_timeout = lion.config[f'{lion.app_name}.coe.request_timeout']
        max_retries = lion.config[f'{lion.app_name}.max_retries']
        friday_model = lion.config[f'{lion.app_name}.coe.common.friday_model']
        self.llm = ChatOpenAI(model_name=model_name,
                              openai_api_base=OPENAI_API_BASE,
                              openai_api_key=OPENAI_API_KEY,
                              temperature=temperature,
                              request_timeout=request_timeout,
                              max_retries=max_retries)
        self.friday_model = Friday(model=friday_model, max_tokens=1024, direction="COE")
        self.question_prompt = None
        self.refine_prompt = None
        self.system_prompt = None
        self.cot_prompt = None
        self.ask_prompt = None
        self.exps: List[Experience] = []

    @abstractmethod
    def pre_check(self) -> bool:
        pass

    @abstractmethod
    def load(self) -> List[Document]:
        pass

    @abstractmethod
    def split(self, document: List[Document]) -> List[Document]:
        pass

    @abstractmethod
    def summary_and_thought(self, document: List[Document]) -> str:
        pass

    @abstractmethod
    def analysis_and_answer(self, existing_answer: str) -> str:
        pass

    def done_async(self):
        coe_es_writer.submit(self.done_sync)

    def done_sync(self):
        self.result_item.is_done = True
        self.result_item.edit_time = get_now_str()
        if (self.result_item.reason and len(self.result_item.reason) != 0):
            self.result_item.search_vector = embed.get_embedding(
                self.result_item.reason)
        self.callback.save_result_to_es()
        time.sleep(1)  # 等待数据库刷新完成
        try:
            sync_coe_result(coe_id=self.result_item.coe_id, type=self.result_item.type)
            time.sleep(1)  # 等待数据库刷新完成
        except Exception as e:
            logger.warn(f'没有coe {self.result_item.coe_id} {self.result_item.brief}', e.args)

    def done(self):
        self.done_async()
