import re
from typing import List
from langchain.prompts import SystemMessagePromptTemplate, \
    HumanMessagePromptTemplate, ChatPromptTemplate
from langchain.prompts.chat import ChatPromptValue
from service.coe_analysis.coe_experience_service import create_experience
from service.coe_analysis.crawler.getDoc import get_6to2notto
from service.coe_analysis.data_structure import Answer, COEResult, MetaMessage
from service.coe_analysis.runners.base import COEChatBaseRunner, on_emit
from service.coe_analysis.llm_sdk_importer import es_util, COE_CRAWLER_DATA
from service.coe_analysis.runners.retriver import COEChatRetriver, get_prompt
from token_count.tokenizer import count_token
from service.lang_chain_utils.lion_client import client as lion
from langchain import LLMChain
from typing import Any, Dict, Optional, Tuple
from langchain.memory.chat_message_histories.in_memory import ChatMessageHistory
from langchain.schema import PromptValue, BaseMessage, HumanMessage, SystemMessage
from langchain.callbacks.manager import (
    AsyncCallbackManagerForChainRun,
    CallbackManagerForChainRun
)
from langchain.input import get_colored_text
import time

lion_prefix = f'{lion.app_name}.coe'


class COEChatChain_6to2not(LLMChain):
    chat_history: ChatMessageHistory
    max_token: int = 1000

    def get_history(self) -> List[BaseMessage]:
        messages = self.chat_history.messages
        messages = messages[::-1]
        history = []
        token = 0
        for message in messages:
            add_token = count_token(message.content)
            if isinstance(message, HumanMessage) and token+add_token >= self.max_token:
                return history[::-1]
            token += add_token
            history.append(message)
        return history[::-1]

    def prep_prompts(
        self,
        input_list: List[Dict[str, Any]],
        run_manager: Optional[CallbackManagerForChainRun] = None,
    ) -> Tuple[List[PromptValue], Optional[List[str]]]:
        """Prepare prompts from inputs."""
        stop = None
        if "stop" in input_list[0]:
            stop = input_list[0]["stop"]
        prompts = []
        for inputs in input_list:
            selected_inputs = {k: inputs[k] for k in self.prompt.input_variables}
            prompt = self.prompt.format_prompt(**selected_inputs)
            messages = self.get_history() + prompt.to_messages()  # 通过 messages 的方式组装 history
            # 把system放在最开始
            system = []
            qa = []
            for message in messages:
                if isinstance(message, SystemMessage):
                    system.append(message)
                else:
                    qa.append(message)
            messages = system + qa
            prompt = ChatPromptValue(messages=messages)

            _colored_text = get_colored_text(prompt.to_string(), "green")
            _text = "Prompt after formatting:\n" + _colored_text
            if run_manager:
                run_manager.on_text(_text, end="\n", verbose=self.verbose)
            if "stop" in inputs and inputs["stop"] != stop:
                raise ValueError(
                    "If `stop` is present in any inputs, should be present in all."
                )
            prompts.append(prompt)
        return prompts, stop

    async def aprep_prompts(
        self,
        input_list: List[Dict[str, Any]],
        run_manager: Optional[AsyncCallbackManagerForChainRun] = None,
    ) -> Tuple[List[PromptValue], Optional[List[str]]]:
        """Prepare prompts from inputs."""
        return self.prep_prompts(input_list, run_manager)


class ChatRunner_6to2not(COEChatBaseRunner):
    valid_type_list = ["to_test", "to_claim", "to_check", "to_grey",
                       "to_inspect", "to_rollback", "not_to_delay",
                       "not_to_illagle_change_data"]
    valid_type_dict = {
        "to_test": "要测试",
        "to_claim": "要周知",
        "to_check": "要审核",
        "to_grey": "要灰度",
        "to_inspect": "要观测",
        "to_rollback": "要可回滚",
        "not_to_delay": "不要延报故障",
        "not_to_illagle_change_data": "不要违规变更数据",
    }

    def __init__(self, result_item: COEResult, _id: str, type: str):
        super().__init__(result_item, _id, type)
        self.rd_reason = None
        self.pattern = re.compile(r'\[(.*?)\]')
        self.lnk = []
        self.image_path = []
        self.chat_history = ChatMessageHistory()
        # for i in result_item.message:
        #     if i.role in ['human', 'user']:
        #         self.chat_history.add_user_message(i.content)
        #     elif i.role in ['assistant', 'ai']:
        #         self.chat_history.add_ai_message(i.content)
        self.init_prompt(self.type)

    def init_prompt(self, type):
        lion.fetch_config()
        self.type = type
        system = get_prompt(self.type, 'chat.system', prefix=lion_prefix)
        system = SystemMessagePromptTemplate(prompt=system)
        coe_content = SystemMessagePromptTemplate(prompt=get_prompt(self.type, 'chat.coe_content', prefix=lion_prefix))
        query = HumanMessagePromptTemplate.from_template('{query}')
        prompt = ChatPromptTemplate(
            messages=[system, coe_content, query],
            input_variables=['content', 'query'])
        self.chain = COEChatChain_6to2not(verbose=True, prompt=prompt, llm=self.llm,
                                          chat_history=self.chat_history, max_token=1000)

    def get_table(self, coe_id):
        self.table = get_6to2notto(coe_id)
        return self.table

    def pre_check(self) -> bool:
        coe_id = self.result_item.coe_id
        answer = {
            'coe_id': coe_id,
            'reason': '',
            'input': '',
            'answer': '无法判断'
        }
        txt = ''
        to_do_next = True
        table = self.get_table(coe_id)
        if (table is None):
            return to_do_next
        phase = self.valid_type_dict[self.type]
        for item in table:
            if (item[0] != phase):
                continue
            txt = item[2]['text']
            lnk = item[2]['link']
            img = item[2]['image']
            self.lnk = lnk
            self.image_path = img
            answer['input'] = \
                f'是否违规:{item[1]}\n研发人员自我陈述:{txt}\n链接:{lnk}\n截图:{img}'
            if (item[1] in ['是', '违规']):
                answer['answer'] = '违反'
                to_do_next = False
                answer['reason'] += 'RD自认为有违反\n'+txt
            else:
                if (len(lnk) != 0 and self.check_lnk(lnk)):
                    answer['answer'] = '没违反'
                    to_do_next = False
                    answer['reason'] += '有学城的超链接\n'
                if (len(img) != 0):
                    answer['answer'] = '没违反'
                    to_do_next = False
                    answer['reason'] += '有贴截图\n'
                answer['reason'] += txt
        self.result_item.message.append(MetaMessage(
            role='user', content='[预校验(不涉及大模型问答)]表格内容如下:\n{}'
            .format(answer['input'])))
        self.result_item.message.append(MetaMessage(
            role='assistant', content='[预校验(不涉及大模型问答)]\nRD陈述:{}\n判断结果:{}'
            .format(answer['reason'], answer['answer'])))
        self.rd_reason = txt.strip()
        if (not to_do_next):
            self.result_item.reason = answer['reason']
            answer_messages = [
                MetaMessage(role='user', content=answer['reason']),
                MetaMessage(role='assistant', content='RD陈述:{}\n判断结果:{}'
                            .format(answer['reason'], answer['answer']))
            ]
            exp = create_experience(type=self.type,
                                    coe_id=self.result_item.coe_id,
                                    task_id=self.result_item.task_id,
                                    message_list=answer_messages,
                                    pre_checked_passed=False)
            self.result_item.pre_checked_passed = False
            self.result_item.answer_message.append(Answer(exp_id=exp.id))
        return to_do_next

    def sync_coe(self, coe_id):
        query = {
            "query": {"bool": {"must": [{"term": {"coe_id": coe_id}}]}},
            "sort": [{"sync_time": {"order": "desc"}}],
            "size": 1000
        }
        items = es_util.search(index=COE_CRAWLER_DATA, query=query)
        if len(items) != 0:
            return

    def load_retiver(self, coe_id):
        query = {
            "query": {"bool": {"must": [{"term": {"coe_id": coe_id}}]}},
            "sort": [{"sync_time": {"order": "desc"}}],
            "size": 1000
        }
        items = es_util.search(index=COE_CRAWLER_DATA, query=query)
        if len(items) == 0:
            self.sync(coe_id)
        self.retriver = COEChatRetriver(min_token=2000, k=10, type=self.type)

    def chat(self, text) -> bool:
        on_emit('chat/loading', {'loading': True, 'chain_id': self.result_item.id})
        docs = self.retriver.get_relevant_documents(text, self.result_item.coe_id)
        on_emit('chat/loading', {'loading': False, 'chain_id': self.result_item.id})
        content = []
        for doc in docs:
            tmp = doc.page_content
            if len(doc.metadata.get('lnk', [])) != 0:
                tmp += '链接:'+str(doc.metadata.get('lnk')) + '\n'
            content.append(tmp)
        content = '\n'.join(content)
        _input = {
            'query': text,
            'content': content
        }
        answer = self.chain.predict(**_input, callbacks=[self.callback, self.chat_callback])
        self.chat_history.add_user_message(text)
        self.chat_history.add_ai_message(answer)
        message = [
            MetaMessage('user', text),
            MetaMessage('system', content),
            MetaMessage('assistant', answer)
        ]
        exp = create_experience(type=self.type, coe_id=self.result_item.coe_id,
                                task_id=self.result_item.task_id,
                                message_list=message)
        # self.result_item.answer_message.insert(0, Answer(exp_id=exp.id))
        self.result_item.answer_message.append(Answer(exp_id=exp.id))
        self.callback.save_result_to_es()
        time.sleep(1)
        on_emit('chat/done', {'chain_id': self.result_item.id, 'answer': answer})
