import base64
from typing import List
from langchain.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate, ChatPromptTemplate
from langchain import LLMChain
import requests
from service.coe_analysis.coe_experience_service import create_experience
from service.coe_analysis.config_reader import OPENAI_API_BASE, OPENAI_API_KEY
from service.coe_analysis.crawler.getDoc import get_6to2notto, getBriefText, getCausesText, getCoeJson, getTimeLineText  # noqa
from service.coe_analysis.crawler_data_service import find_crawler_data, sync_crawler_data
from service.coe_analysis.data_structure import Answer, Arg, COEResult, MetaMessage
from service.coe_analysis.llm_sdk_importer import COE_CRAWLER_DATA, es_util
from service.coe_analysis.mcm_helper.mcm_helper import get_mcm_plan
from service.coe_analysis.runners.chat_6to2notto import COEChatChain_6to2not
from service.coe_analysis.runners.loaders import COELoader, Document, get_COE_6to2not_Spliter
from service.coe_analysis.runners.base import COEBaseRunner
from service.coe_analysis.runners.retriver import COEChatRetriver, get_fewshoot, get_prompt
from service.lang_chain_utils.helper import friday_chat
from langchain.memory.chat_message_histories.in_memory import ChatMessageHistory
from service.lang_chain_utils.lion_client import client as lion
from utils import logger, merge_lines
from langchain.chat_models import ChatOpenAI
import re
from datetime import datetime
import json
from llmcore_sdk.models.friday import Friday, FridayVision


def get_answer_text(text: str) -> str:
    pattern = re.compile(r'是否违反了要灰度的原则[:：]\s*([\u4e00-\u9fa5]+)')
    match = pattern.findall(text)
    if (len(match) > 0):
        text = str(match[0])
    if text.startswith('没违反'):
        text = '没违反'
    if text.startswith('没有违反'):
        text = '没违反'
    if text.startswith('未违反'):
        text = '没违反'
    if text.startswith('违反'):
        text = '违反'
    if '无法确定' in text:
        text = '无法确定'
    return text


class COE6to2notRunnerNew(COEBaseRunner):
    valid_type_list = ["to_test", "to_claim", "to_check", "to_grey",
                       "to_inspect", "to_rollback", "not_to_delay",
                       "not_to_illagle_change_data", 'null_check']
    valid_type_dict = {
        "to_test": "要测试",
        "to_claim": "要周知",
        "to_check": "要审核",
        "to_grey": "要灰度",
        "to_inspect": "要观测",
        "to_rollback": "要可回滚",
        "not_to_delay": "不要延报故障",
        "not_to_illagle_change_data": "不要违规变更数据",
        'null_check': '异常字段'
    }
    valid_lnk = {
        'to_test': ['km.sankuai.com'],
        'to_claim': ['mcm.sankuai.com'],
        'to_check': ['mcm.sankuai.com'],
        'not_to_delay': ['mcm.sankuai.com']
    }
    valid_k = {
        "to_test": [2, 2, 1],
        "to_claim": [1, 1, 1],
        "to_check": [2, 2, 1],
        "to_grey": [2, 2, 3],
        "to_inspect": [2, 2, 1],
        "to_rollback": [2, 2, 1],
        "not_to_delay": [2, 2, 1],
        "not_to_illagle_change_data": [2, 2, 1],
        'null_check': [2, 2, 1],
    }

    not_need_to_precheck = ['null_check']

    def __init__(self, result_item: COEResult, _id: str, to_do_total: bool = False):
        super().__init__(result_item, _id)
        self.rd_reason = None
        self.pattern = re.compile(r'\[(.*?)\]')
        self.to_do_total = to_do_total
        self.lnk = []
        self.image_path = []

    def init_prompt(self, type):
        self.type = type
        self.cot_system = SystemMessagePromptTemplate(prompt=get_fewshoot(type, 'cot_system', query_variable='query',
                                                                          k=self.valid_k[type][2]))
        self.ask_prompt = get_prompt(type, 'ask_prompt')
        self.refine_prompt = get_prompt(type, 'refine_prompt')
        self.question_prompt = get_prompt(type, 'question_prompt')
        self.background_system_prompt = None
        try:
            self.background_system_prompt = get_prompt(type, 'system')
            self.question_prompt = ChatPromptTemplate(
                messages=[
                    SystemMessagePromptTemplate(
                        prompt=self.background_system_prompt),
                    SystemMessagePromptTemplate(
                        prompt=get_fewshoot(
                            type, 'cot_system', k=self.valid_k[type][0],
                            query_variable='text')),
                    HumanMessagePromptTemplate(
                        prompt=self.question_prompt)],
                input_variables=self.question_prompt.input_variables)
            self.refine_prompt = ChatPromptTemplate(
                messages=[
                    SystemMessagePromptTemplate(
                        prompt=self.background_system_prompt),
                    SystemMessagePromptTemplate(
                        prompt=get_fewshoot(
                            type, 'cot_system', k=self.valid_k[type][1],
                            query_variable='existing_answer')),
                    HumanMessagePromptTemplate(
                        prompt=self.refine_prompt)],
                input_variables=self.refine_prompt.input_variables)
        except Exception as e:
            logger.info(e.args+'\n不使用背景')
            self.question_prompt = ChatPromptTemplate(
                messages=[
                    SystemMessagePromptTemplate(
                        prompt=get_fewshoot(
                            type, 'cot_system', k=self.valid_k[type][0],
                            query_variable='text')),
                    HumanMessagePromptTemplate(prompt=self.question_prompt)],
                input_variables=self.question_prompt.input_variables)
            self.refine_prompt = ChatPromptTemplate(
                messages=[
                    SystemMessagePromptTemplate(
                        prompt=get_fewshoot(
                            type, 'cot_system', k=self.valid_k[type][1],
                            query_variable='existing_answer')),
                    HumanMessagePromptTemplate(
                        prompt=self.refine_prompt)],
                input_variables=self.refine_prompt.input_variables)

        self.document_variable_name = self.question_prompt.input_variables[0]
        self.initial_response_name = self.ask_prompt.input_variables[0]

    def get_table(self, coe_id):
        self.table = get_6to2notto(coe_id)
        return self.table

    def check_lnk(self, lnk):
        if self.type in self.valid_lnk:
            for pattern in self.valid_lnk[self.type]:
                if pattern in lnk:
                    return True
            return False
        return True

    def pre_check(self) -> bool:
        if (self.type in self.not_need_to_precheck):
            return True
        coe_id = self.result_item.coe_id
        type_name = self.valid_type_dict[self.type]
        answer = {
            'coe_id': coe_id,
            'reason': '',
            'input': '',
            'answer': '无法确定'
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
            if len(txt.strip()) != 0 and len(item[0]) != 0:
                self.rd_reason = f'是否违反{type_name}:{item[1]}\n{txt.strip()}'
            else:
                self.rd_reason = ''
        if (not to_do_next):
            if not self.to_do_total:
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
            else:
                self.result_item.pre_checked_passed = False
                #  后续还会进行原因分析
        return to_do_next | self.to_do_total

    def load(self) -> List[Document]:
        loader = COELoader(coe_id=self.result_item.coe_id)
        document = loader.load()
        if (self.rd_reason and len(self.rd_reason) != 0):
            document.insert(0, Document(
                page_content=f'[声明]\n{self.rd_reason}\n\n',
                metadata={"desc": "[研发自证]", "lnk": self.lnk, "img": self.image_path}))
        return document

    def split(self, document: List[Document]) -> List[Document]:
        text_splitter = get_COE_6to2not_Spliter(self.type)
        return text_splitter.split_documents(document)

    def summary_and_thought(self, document: List[Document]) -> str:
        question_chain = LLMChain(verbose=True, prompt=self.question_prompt, llm=self.llm)
        existing_answer = []
        for doc in document:
            res = question_chain.predict(callbacks=[self.callback], text=doc.page_content)
            phase = doc.metadata['phase']
            res = f'---{phase}---\n{res}'
            res_text = get_answer_text(res)
            answer_messages = [
                MetaMessage(role='user', content=doc.page_content),
                MetaMessage(role='assistant', content=res)
            ]
            exp = create_experience(type=self.type,
                                    coe_id=self.result_item.coe_id,
                                    task_id=self.result_item.task_id,
                                    message_list=answer_messages,
                                    pre_checked_passed=True)
            self.result_item.answer_message.append(Answer(exp_id=exp.id))
            if res_text in ['没违反', '违反', '未违反'] or phase == '[自证]':
                existing_answer.append(res)
        answer = '\n\n'.join(existing_answer)
        self.result_item.reason = answer
        return answer.strip()

    def analysis_and_answer(self, existing_answer: str) -> str:
        if len(existing_answer) == 0:
            reason = '在时间线、原因分析、RD自述、反思中均无法确定是否违反'
            answer = '判断依据:在时间线、原因分析、RD自述、反思中均无法确定是否违反\n判断结果:无法确定'
            self.result_item.reason = reason
            answer_messages = [
                MetaMessage(role='user', content=reason),
                MetaMessage(role='assistant', content=answer)
            ]
            exp = create_experience(type=self.type,
                                    coe_id=self.result_item.coe_id,
                                    task_id=self.result_item.task_id,
                                    message_list=answer_messages,
                                    pre_checked_passed=False)
            self.result_item.answer_message.insert(0, Answer(exp_id=exp.id))
            return '判断依据:在时间线、原因分析、RD自述、反思中均无法确定是否违反\n判断结果:无法确定'
        prompt = ChatPromptTemplate(messages=[
            self.cot_system.format(query=existing_answer),
            HumanMessagePromptTemplate(prompt=self.ask_prompt)
        ], input_variables=['existing_answer'])
        if self.background_system_prompt:
            prompt = ChatPromptTemplate(messages=[
                SystemMessagePromptTemplate(prompt=self.background_system_prompt),
                self.cot_system.format(query=existing_answer),
                HumanMessagePromptTemplate(prompt=self.ask_prompt)
            ], input_variables=['existing_answer'])
        chain = LLMChain(verbose=True, prompt=prompt, llm=self.llm)
        res = chain.predict(
            callbacks=[self.callback], existing_answer=existing_answer)
        message = [
            MetaMessage('user', existing_answer),
            MetaMessage('assistant', res)
        ]
        exp = create_experience(type=self.type, coe_id=self.result_item.coe_id,
                                task_id=self.result_item.task_id,
                                message_list=message)
        self.result_item.answer_message.insert(0, Answer(exp_id=exp.id))
        self.result_item.similiar_case_list = \
            self.cot_system.prompt.get_cot_cache()
        return res


class COE6to2notRunner(COEBaseRunner):
    valid_type_list = ["to_test", "to_claim", "to_check", "to_grey",
                       "to_inspect", "to_rollback", "not_to_delay",
                       "not_to_illagle_change_data", 'null_check']
    valid_type_dict = {
        "to_test": ["要测试"],
        "to_claim": ["要周知"],
        "to_check": ["要审核"],
        "to_grey": ["要灰度"],
        "to_inspect": ["要观测"],
        "to_rollback": ["要可回滚"],
        "not_to_delay": ["不要延报故障", "不要瞒报故障"],
        "not_to_illagle_change_data": ["不要违规变更数据"],
        'null_check': ['异常字段']
    }
    valid_lnk = {
        'to_test': ['km.sankuai.com', 'ones.sankuai.com'],
        'to_claim': ['mcm.sankuai.com','mcm.mws.sankuai.com'],
        'to_check': ['mcm.sankuai.com','mcm.mws.sankuai.com'],
        'not_to_delay': ['mcm.sankuai.com','mcm.mws.sankuai.com']
    }
    valid_k = {
        "to_test": [2, 2, 1],
        "to_claim": [1, 1, 1],
        "to_check": [2, 2, 1],
        "to_grey": [1, 0, 1],
        "to_inspect": [2, 2, 1],
        "to_rollback": [1, 1, 0],
        "not_to_delay": [2, 2, 1],
        "not_to_illagle_change_data": [2, 2, 1],
        'null_check': [2, 2, 1],
    }

    not_need_to_precheck = ['null_check']

    def __init__(self, result_item: COEResult, _id: str, to_do_total: bool = False, args: List[Arg] = []):
        super().__init__(result_item, _id)
        self.rd_reason = None
        self.pattern = re.compile(r'\[(.*?)\]')
        self.to_do_total = to_do_total
        self.lnk = []
        self.image_path = []
        lion.fetch_config()
        friday_model = lion.config[f'{lion.app_name}.coe.tonotto.model']
        friday_vision = lion.config[f'{lion.app_name}.coe.tonotto.model_vision']
        for arg in args:
            if arg.key == 'model':
                friday_model = arg.value
        self.tonotto_friday = Friday(model=friday_model, max_tokens=2048,
                                     temperature=0.01, direction='COE_TONOTTO')
        self.tonotto_vision = FridayVision(friday_vision, max_tokens=2048,
                                           temperature=0.01, direction='COE_TONOTTO')

    def init_prompt(self, type):
        self.type = type
        self.cot_system = SystemMessagePromptTemplate(prompt=get_fewshoot(type, 'cot_system', query_variable='query',
                                                                          k=self.valid_k[type][2]))
        self.ask_prompt = get_prompt(type, 'ask_prompt')
        self.refine_prompt = get_prompt(type, 'refine_prompt')
        self.question_prompt = get_prompt(type, 'question_prompt')
        self.background_system_prompt = None
        self.image_prompt = None
        try:
            self.image_prompt = get_prompt(type, 'image_check', prefix=f'{lion.app_name}.coe')
        except Exception:
            pass
        try:
            self.background_system_prompt = get_prompt(type, 'system')
            self.question_prompt = ChatPromptTemplate(
                messages=[
                    SystemMessagePromptTemplate(
                        prompt=self.background_system_prompt),
                    SystemMessagePromptTemplate(
                        prompt=get_fewshoot(
                            type, 'cot_system', k=self.valid_k[type][0],
                            query_variable='text')),
                    HumanMessagePromptTemplate(
                        prompt=self.question_prompt)],
                input_variables=self.question_prompt.input_variables)
            self.refine_prompt = ChatPromptTemplate(
                messages=[
                    SystemMessagePromptTemplate(
                        prompt=self.background_system_prompt),
                    SystemMessagePromptTemplate(
                        prompt=get_fewshoot(
                            type, 'cot_system', k=self.valid_k[type][1],
                            query_variable='existing_answer')),
                    HumanMessagePromptTemplate(
                        prompt=self.refine_prompt)],
                input_variables=self.refine_prompt.input_variables)
        except Exception as e:
            logger.info(e.args+'\n不使用背景')
            self.question_prompt = ChatPromptTemplate(
                messages=[
                    SystemMessagePromptTemplate(
                        prompt=get_fewshoot(
                            type, 'cot_system', k=self.valid_k[type][0],
                            query_variable='text')),
                    HumanMessagePromptTemplate(prompt=self.question_prompt)],
                input_variables=self.question_prompt.input_variables)
            self.refine_prompt = ChatPromptTemplate(
                messages=[
                    SystemMessagePromptTemplate(
                        prompt=get_fewshoot(
                            type, 'cot_system', k=self.valid_k[type][1],
                            query_variable='existing_answer')),
                    HumanMessagePromptTemplate(
                        prompt=self.refine_prompt)],
                input_variables=self.refine_prompt.input_variables)

        self.document_variable_name = self.question_prompt.input_variables[0]
        self.initial_response_name = self.ask_prompt.input_variables[0]

    def get_table(self, coe_id):
        self.table = get_6to2notto(coe_id)
        return self.table

    def check_lnk(self, lnks):
        if self.type in self.valid_lnk:
            for pattern in self.valid_lnk[self.type]:
                for lnk in lnks:
                    if isinstance(lnk, str):
                        if pattern in lnk:
                            return True
            return False
        return True

    def pre_check(self, no_self_prove: bool = False) -> bool:
        if (self.type in self.not_need_to_precheck):
            return True
        if no_self_prove:
            return True
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
            if (item[0] not in phase):
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
                    answer['reason'] += '有mcm或其他相关链接\n'
                if (len(img) != 0):
                    img_check_ans, reason = self.image_check(img[0])
                    if img_check_ans:  # 如果图片有效
                        answer['answer'] = '没违反'
                        to_do_next = False
                        answer['reason'] += reason
                answer['reason'] += txt
        self.result_item.message.append(MetaMessage(
            role='user', content='[预校验(不涉及大模型问答)]表格内容如下:\n{}'
            .format(answer['input'])))
        self.result_item.message.append(MetaMessage(
            role='assistant', content='[预校验(不涉及大模型问答)]\nRD陈述:{}\n判断结果:{}'
            .format(answer['reason'], answer['answer'])))
        self.rd_reason = txt.strip()
        self.result_item.reason = answer['reason']
        answer_messages = [
            MetaMessage(role='user', content=answer['reason']),
            MetaMessage(role='assistant', content='RD陈述:{}\n判断结果:{}'
                        .format(answer['reason'], answer['answer']))
        ]
        # 必然不可以被当成experience
        exp = create_experience(type=self.type,
                                coe_id=self.result_item.coe_id,
                                task_id=self.result_item.task_id,
                                message_list=answer_messages,
                                pre_checked_passed=False, need_embedding=False)
        self.result_item.pre_checked_passed = False
        self.result_item.answer_message.append(Answer(exp_id=exp.id))
        return to_do_next | self.to_do_total

    def load(self) -> List[Document]:
        loader = COELoader(coe_id=self.result_item.coe_id)
        document = loader.load()
        table = self.get_table(self.result_item.coe_id)
        if table is None:
            return document
        phase = self.valid_type_dict[self.type]
        for item in table:
            if item[0] not in phase:
                continue
            rd_reason = item[2]['text']
            lnk = item[2]['link']
            img = item[2]['image']
            content = "[研发人员自我陈述]\n"
            if rd_reason and item[1]:
                content += f'是否违规:{item[1]}\n{rd_reason}\n'
            if lnk:
                content += f'链接:{lnk}\n'
            if img:
                content += f'截图:{img}\n'
            document.insert(0, Document(
                page_content = content,
                metadata={"desc": "[研发自证]", "lnk": lnk, "img": img}))
        return document

    def split(self, document: List[Document]) -> List[Document]:
        text_splitter = get_COE_6to2not_Spliter(self.type)
        return text_splitter.split_documents(document)

    def encode_image(self, image_path: str):
        '''将图片编码为base64格式'''
        if image_path.startswith('http'):
            response = requests.get(image_path)
            return base64.b64encode(response.content).decode('utf-8')
        else:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')

    def image_check(self, img: str):
        '''图片有效性判断'''
        if None or self.image_prompt is None:
            return False, '无法判断'
        # self.callback.result_item.message.append(
        #     MetaMessage(role='system', content=self.background_system_prompt.format()))
        self.callback.result_item.message.append(
            MetaMessage(role='user', content=f"<img src=\"{img}\"></img>{self.image_prompt.format()}"))
        try:
            res = self.tonotto_vision(messages=[{"role": "user",
                                                 "content": self.image_prompt.format(),
                                                 "image_url": img}])
        except Exception:
            res = '无法确定'
        self.callback.result_item.message.append(
            MetaMessage(role='assistant', content=res))
        pattern = re.compile(r'图片有效[:：]\s*([\u4e00-\u9fa5]+)')
        match = pattern.findall(res)
        if (len(match) > 0):
            answer = str(match[0])
        elif '是' in answer.split('\n')[0]:
            answer = '是'
        else:
            answer = '否'
        return answer == '是' or answer == '有效', res

    def summary_and_thought(self, document: List[Document]) -> str:
        res = friday_chat(model=self.tonotto_friday, callback=self.callback,
                          messages=self.question_prompt.format_messages(text=document[0].page_content))
        refine_steps = [res]
        answer = refine_steps[-1]
        self.result_item.reason = answer
        message = [
            MetaMessage('user', self.transfer_existing_answer(answer)),
            MetaMessage('assistant', self.transfer_existing_answer(answer))
        ]
        exp = create_experience(type=self.type, coe_id=self.result_item.coe_id,
                                task_id=self.result_item.task_id,
                                message_list=message)
        # 进行头插，将大模型的判断结果作为最终结果。
        self.result_item.answer_message.insert(0, Answer(exp_id=exp.id))
        return answer

    def transfer_existing_answer(self, existing_answer: str):
        items = merge_lines(existing_answer)
        answer = []
        for item in items:
            key = item['key']
            value = item['value']
            if '推测' in key:
                continue
            answer.append(f'{key}: {value}')
        answer = '\n'.join(answer)
        return answer

    def analysis_and_answer(self, existing_answer: str) -> str:
        return existing_answer
        # prompt = ChatPromptTemplate(messages=[
        #     self.cot_system.format(query=existing_answer),
        #     HumanMessagePromptTemplate(prompt=self.ask_prompt)
        # ], input_variables=['existing_answer'])
        # if self.background_system_prompt:
        #     prompt = ChatPromptTemplate(messages=[
        #         SystemMessagePromptTemplate(prompt=self.background_system_prompt),
        #         self.cot_system.format(query=existing_answer),
        #         HumanMessagePromptTemplate(prompt=self.ask_prompt)
        #     ], input_variables=['existing_answer'])
        # res = friday_chat(model=self.tonotto_friday, callback=self.callback,
        #                   messages=prompt.format_messages(existing_answer=existing_answer))
        # message = [
        #     MetaMessage('user', self.transfer_existing_answer(existing_answer)),
        #     MetaMessage('assistant', res)
        # ]
        # exp = create_experience(type=self.type, coe_id=self.result_item.coe_id,
        #                         task_id=self.result_item.task_id,
        #                         message_list=message)
        # # 进行头插，将大模型的判断结果作为最终结果。
        # self.result_item.answer_message.insert(0, Answer(exp_id=exp.id))
        # self.result_item.similiar_case_list = \
        #     self.cot_system.prompt.get_cot_cache()
        # return res


class COE6to2notMCMRunner(COE6to2notRunner):
    valid_type_list = ['to_claim', 'to_check']

    def pre_check(self, no_self_prove: bool = False) -> bool:
        to_do_next = super().pre_check(no_self_prove)
        if not to_do_next:
            return False
        mcm_ids = set()
        coe_id = self.result_item.coe_id
        table = self.get_table(coe_id)
        if (table is None):
            return to_do_next
        regex = r'\/mine\/plan\/detail\/(\d+)'
        for item in table:
            lnk = item[2]['link']
            for url in lnk:
                if not isinstance(url, str):
                    continue
                numbers = re.findall(regex, url)
                if numbers:
                    mcm_ids.add(numbers[0])
        timeLineText = getTimeLineText(coe_id)
        related_time_line = []
        for ind, item in enumerate(timeLineText):
            for url in item.link_list:
                numbers = re.findall(regex, url)
                if numbers:
                    mcm_ids.add(numbers[0])
                    if ind != 0:
                        related_time_line.append(item)
        content = '\n'.join([self.result_item.brief] + [i.data for i in related_time_line])
        mcm_ids = list(mcm_ids)
        for mcm_id in mcm_ids:
            try:
                plan = get_mcm_plan(mcm_id)
                notice = plan.planNotice.content
                prompt = get_prompt(type='tonotto', template='mcm.is_related', prefix=f'{lion.app_name}.coe')
                chain = LLMChain(verbose=True, prompt=prompt, llm=self.llm)
                res = chain.predict(callbacks=[self.callback], notice=notice, content=content)
                pattern = re.compile(r'回答[:：]\s*([\u4e00-\u9fa5]+)')
                match = pattern.findall(res)
                if (len(match) > 0):
                    answer = str(match[0])
                elif '是' in res.split('\n')[0]:
                    answer = '是'
                else:
                    answer = '否'
                if answer == '是':
                    message = [
                        MetaMessage('user', f'mcm链接 : https://mcm.mws.sankuai.com/#/mine/plan/detail/{mcm_id}'),
                        MetaMessage('assistant', f'判断结果:没违反\n判断依据: 由于这个 mcm 链接 https://mcm.mws.sankuai.com/#/mine/plan/detail/{mcm_id} 与 coe 相关，可以作为证据')  # noqa
                    ]
                    self.result_item.message.append(MetaMessage('assistant', f'判断结果:没违反\n判断依据: 由于这个 mcm 链接 https://mcm.mws.sankuai.com/#/mine/plan/detail/{mcm_id} 与 coe 相关，可以作为证据'))  # noqa
                    exp = create_experience(type=self.type, coe_id=self.result_item.coe_id,
                                            task_id=self.result_item.task_id,
                                            message_list=message)
                    self.result_item.answer_message.insert(0, Answer(exp_id=exp.id))
                    self.callback.save_result_to_es()
                    return False | self.to_do_total
            except Exception:
                pass
        return True


class COE6to2notS9Runner(COE6to2notRunner):
    valid_type_list = ['not_to_delay']

    def pre_check(self, no_self_prove: bool = False) -> bool:
        to_do_next = super().pre_check()
        # if not to_do_next or not self.result_item.pre_checked_passed:
        # 如果之前的过了，有自主上报，或者有证据，那么就可以不看S9
        if not to_do_next:
            return False
        # if self.result_item.level not in ['S9', 'S4', 'S3', 'S2', 'S1', 'S0']:
        if self.result_item.level in ['E', '事件']:
            self.result_item.message.append(MetaMessage(
                role='assistant', content='[S9校验]\n判断结果:没违反\n判断依据:由于当前的COE是 {} 级别的，所以跳过判定'
                .format(self.result_item.level)))
            self.result_item.reason = '没违反'
            # if not self.to_do_total:
            # S9 筛掉了还是要再进行提问，S9筛的可以当首要原因
            answer_messages = [
                MetaMessage(role='user', content='没违反'),
                MetaMessage(role='assistant',
                            content='判断结果:没违反\n判断依据:由于当前的COE是 {} 级别的，所以跳过判定'
                            .format(self.result_item.level))
            ]
            exp = create_experience(type=self.type,
                                    coe_id=self.result_item.coe_id,
                                    task_id=self.result_item.task_id,
                                    message_list=answer_messages,
                                    pre_checked_passed=False)
            self.result_item.pre_checked_passed = False
            self.result_item.answer_message.insert(0, Answer(exp_id=exp.id))
            self.callback.save_result_to_es()
            return False | self.to_do_total
        return True


class COEReportTimeRunner(COE6to2notS9Runner):
    valid_type_list = ['not_to_delay']

    def pre_check(self) -> bool:
        super_flg = super().pre_check()
        if not super_flg:
            return False
        incident = getCoeJson('', self.result_item.coe_id)['incident']
        try:
            notify_time_str = incident['notify_time']
            find_time_str = incident['find_time']
            notify_time = datetime.strptime(notify_time_str, "%Y-%m-%d %H:%M:%S")
            find_time = datetime.strptime(find_time_str, "%Y-%m-%d %H:%M:%S")
        except Exception:
            return True  # 没有信息，必须校验
        time_diff = notify_time - find_time
        time_diff_minutes = time_diff.total_seconds() / 60
        if time_diff_minutes < 60:
            self.result_item.message.append(MetaMessage(
                role='assistant', content='[时间校验]\n判断结果:没违反\n判断依据:由于当前的COE通告时长{}分钟<60分钟，所以跳过判定'
                .format(time_diff_minutes)))
            self.result_item.reason = '没违反'
            answer_messages = [
                MetaMessage(role='user', content='没违反'),
                MetaMessage(role='assistant',
                            content='判断结果:没违反\n判断依据:由于当前的COE通告时长{}分钟<60分钟，所以跳过判定'
                            .format(time_diff_minutes))
            ]
            exp = create_experience(type=self.type,
                                    coe_id=self.result_item.coe_id,
                                    task_id=self.result_item.task_id,
                                    message_list=answer_messages,
                                    pre_checked_passed=False)
            self.result_item.pre_checked_passed = False
            self.result_item.answer_message.insert(0, Answer(exp_id=exp.id))
            self.callback.save_result_to_es()
            return False | self.to_do_total
        return True


class COE6to2notMutiAskRunner(COEBaseRunner):
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
    valid_lnk = {
        'to_test': ['km.sankuai.com'],
        'to_claim': ['mcm.sankuai.com'],
        'to_check': ['mcm.sankuai.com'],
        'not_to_delay': ['mcm.sankuai.com']
    }

    def __init__(self, result_item: COEResult, _id: str, type: str):
        super().__init__(result_item, _id)
        self.rd_reason = None
        self.pattern = re.compile(r'\[(.*?)\]')
        self.lnk = []
        self.image_path = []
        self.chat_history = ChatMessageHistory()
        self.type = type
        self.sync_coe_by_id(result_item.coe_id)
        self.init_prompt(self.type)

    def init_prompt(self, type):
        prefix = f'{lion.app_name}.coe'
        self.prefix = prefix
        lion.fetch_config()
        self.type = type
        system = get_prompt(self.type, 'chat.system', prefix=prefix)
        self.ask_prompt = get_prompt(self.type, 'chat.final_ask', prefix=prefix)
        system = SystemMessagePromptTemplate(prompt=system)
        coe_content = SystemMessagePromptTemplate(prompt=get_prompt(self.type, 'chat.coe_content', prefix=prefix))
        query = HumanMessagePromptTemplate.from_template('{query}')
        prompt = ChatPromptTemplate(
            messages=[system, coe_content, query],
            input_variables=['content', 'query'])
        self.system = system
        self.chain = COEChatChain_6to2not(verbose=True, prompt=prompt, llm=self.llm,
                                          chat_history=self.chat_history, max_token=1000)

    def get_table(self, coe_id):
        self.table = get_6to2notto(coe_id)
        return self.table

    def check_lnk(self, lnk):
        if self.type in self.valid_lnk:
            for pattern in self.valid_lnk[self.type]:
                if pattern in lnk:
                    return True
            return False
        return True

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
        return True

    def sync_coe_by_id(self, coe_id):
        query = {
            "query": {"bool": {"must": [{"term": {"coe_id": coe_id}}]}},
            "sort": [{"sync_time": {"order": "desc"}}],
            "size": 1000
        }
        items = es_util.search(index=COE_CRAWLER_DATA, query=query)
        if len(items) == 0:
            sync_crawler_data(coe_id)

    def load_retiver(self, coe_id):
        self.retriver = COEChatRetriver(min_token=1500, k=10, type=self.type)

    def load(self) -> List[Document]:
        self.load_retiver(self.result_item.coe_id)
        self.ask_list = lion.config[f'{self.prefix}.{self.type}.chat.ask_list']
        self.ask_list = json.loads(self.ask_list)
        return [Document(page_content='placeholder')]

    def split(self, document: List[Document]) -> List[Document]:
        return document

    def chat(self, text) -> bool:
        docs = self.retriver.get_relevant_documents(text, self.result_item.coe_id)
        content = []
        for doc in docs:
            tmp = doc.page_content
            content.append(tmp)
        content = '\n'.join(content)
        _input = {
            'query': text,
            'content': content
        }
        answer = self.chain.predict(**_input, callbacks=[self.callback])
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
        return answer

    def pattern_fnd(self, text, pattern):
        match = pattern.findall(text)
        if (len(match) > 0):
            text = str(match[0])
        return text

    def answer_to_yes_no(self, answer):
        not_mention = r'未提及|没有明确|无法判断|不明确|可能|大概|也许'
        no_pattern = r'否|没有|无|不|未'
        yes_pattern = r'是|有|存在|提到|涉及'

        phase = 'not_mention'
        if re.search(not_mention, answer):
            phase = 'not_mention'
        elif re.search(no_pattern, answer):
            phase = 'no'
        elif re.search(yes_pattern, answer):
            phase = 'yes'
        return phase

    def rec_ask(self, prev: str, ask_config: dict):
        answer_pattern = re.compile(r'(?:判断|推测)结果[:：]\s*([\u4e00-\u9fa5]+)')
        reason_pattern = re.compile(r'原因[:：]\s*(.+)')
        if 'answer' in ask_config:
            answer = ask_config['answer'] + '\n' + '判断原因:' + prev
            logger.info(answer)
            return answer
        if 'query' in ask_config:
            text = self.chat(ask_config['query'])
            answer = self.pattern_fnd(text, answer_pattern)
            reason = self.pattern_fnd(text, reason_pattern)
            phase = self.answer_to_yes_no(answer)
            if 'any' in ask_config:
                answer = self.rec_ask(reason, ask_config['any'])
            elif phase in ask_config:
                answer = self.rec_ask(reason, ask_config[phase])
            else:
                answer = "判断结果:无法确定" + '\n' + '判断原因:' + reason
                logger.info(answer)
            return answer

    def summary_and_thought(self, document: List[Document]) -> str:
        answers = []
        for conf in self.ask_list:
            ans = self.rec_ask('', conf)
            answers.append(ans)
        answers = '\n\n'.join(answers)
        return answers

    def analysis_and_answer(self, content: str) -> str:
        # prompt = ChatPromptTemplate(messages=[
        #     self.system,
        #     # self.cot_system.format(query=content),
        #     HumanMessagePromptTemplate(prompt=self.ask_prompt)
        # ], input_variables=['content'])
        # chain = LLMChain(verbose=True, prompt=prompt, llm=self.llm)
        # res = chain.predict(callbacks=[self.callback], content=content)

        answer_pattern = re.compile(r'(?:判断|推测)结果[:：]\s*([\u4e00-\u9fa5]+)')
        res = '判断结果:无法确定'
        for ans in answer_pattern.findall(content):
            if '没违反' in ans:
                res = "判断结果:没违反"
                break
            elif '违反' in ans:
                res = '判断结果:违反'
                break

        message = [
            MetaMessage('user', content),
            MetaMessage('assistant', res)
        ]
        exp = create_experience(type=self.type, coe_id=self.result_item.coe_id,
                                task_id=self.result_item.task_id,
                                message_list=message)
        self.result_item.answer_message.insert(0, Answer(exp_id=exp.id))
        self.result_item.reason = content
        return res


class COE6to2notMutiAskRunner_to_test(COE6to2notMutiAskRunner):
    def __init__(self, result_item: COEResult, _id: str, type: str):
        super().__init__(result_item, _id, type)
        model_name = 'gpt-4'
        temperature = lion.config[
            f'{lion.app_name}.coe.temperature']
        request_timeout = lion.config[
            f'{lion.app_name}.coe.request_timeout']
        max_retries = lion.config[f'{lion.app_name}.max_retries']
        self.llm = ChatOpenAI(model_name=model_name,
                              openai_api_base=OPENAI_API_BASE,
                              openai_api_key=OPENAI_API_KEY,
                              temperature=temperature,
                              request_timeout=request_timeout,
                              max_retries=max_retries)

    def pre_check(self) -> bool:
        is_passed = super().pre_check()
        content = []
        for desc in ['[发生时间]', '[研发自证]']:
            data_list, _ = find_crawler_data(coe_id=self.result_item.coe_id, desc=desc, type=self.type)
            if len(data_list) == 0:
                continue
            data = data_list[0].get_text().strip()
            content.append(data)
        content = '\n\n'.join(content)
        prompt = get_prompt(self.type, template='chat.pre_check', prefix=self.prefix)
        chain = LLMChain(verbose=True, prompt=prompt, llm=self.llm)
        answer = chain.predict([self.callback], content=content)
        self.result_item.reason = content
        message = [
            MetaMessage('user', content),
            MetaMessage('assistant', answer)
        ]
        exp = create_experience(type=self.type, coe_id=self.result_item.coe_id,
                                task_id=self.result_item.task_id,
                                message_list=message)
        answer_pattern = re.compile(r'结果[:：]\s*([\u4e00-\u9fa5]+)')
        ans = self.pattern_fnd(answer, answer_pattern)
        if '无法确定' in ans or '无法判断' in ans:
            self.result_item.answer_message.append(Answer(exp_id=exp.id))
            self.callback.save_result_to_es()
            return is_passed
        elif '没违反' in ans:
            self.result_item.answer_message.insert(0, Answer(exp_id=exp.id))
            self.callback.save_result_to_es()
            return False
        elif '违反' in ans:
            self.result_item.answer_message.insert(0, Answer(exp_id=exp.id))
            self.callback.save_result_to_es()
            return False
        return is_passed
