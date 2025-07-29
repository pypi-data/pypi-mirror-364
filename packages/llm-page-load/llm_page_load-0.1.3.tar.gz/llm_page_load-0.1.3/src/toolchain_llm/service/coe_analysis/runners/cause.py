import json
import re
from typing import List
from langchain.prompts import SystemMessagePromptTemplate, \
    HumanMessagePromptTemplate, ChatPromptTemplate
from langchain import LLMChain
from service.coe_analysis.coe_experience_service import create_experience
from service.coe_analysis.config_reader import OPENAI_API_BASE, OPENAI_API_KEY
from service.coe_analysis.crawler.crawler_data import CrawlerData
from service.coe_analysis.data_structure import Answer, COEResult, MetaMessage
from service.coe_analysis.runners.loaders import COELoader, COESpliter, Document
from service.coe_analysis.runners.base import COEBaseRunner
from service.coe_analysis.runners.retriver import COETopicRetriver, get_fewshoot, get_prompt  # noqa
from service.lang_chain_utils.helper import friday_chat
from service.lang_chain_utils.lion_client import client as lion
from langchain.chat_models import ChatOpenAI
from llmcore_sdk.models.friday import Friday


class COETopicAnalysisRunner:
    '''单独的runner，仅为主题分析的对话框使用'''

    def __init__(self, task_id):
        lion.fetch_config()
        self.retriver = COETopicRetriver(task_id)
        self.prompt = get_prompt('topic', 'ask_prompt')
        model_name = lion.config[f'{lion.app_name}.coe.model_name']
        temperature = lion.config[f'{lion.app_name}.coe.temperature']
        request_timeout = lion.config[f'{lion.app_name}.coe.request_timeout']
        max_retries = lion.config[f'{lion.app_name}.max_retries']
        self.llm = ChatOpenAI(model_name=model_name,
                              openai_api_base=OPENAI_API_BASE,
                              openai_api_key=OPENAI_API_KEY,
                              temperature=temperature,
                              request_timeout=request_timeout,
                              max_retries=max_retries)

    def analysis_once(self, topic):
        coe_result_list = self.retriver.retrive(topic)
        text = []
        for ind, item in enumerate(coe_result_list):
            text.append(f'[线上问题{ind}]\n{item.reason}')
        text = '\n'.join(text)
        chain = LLMChain(verbose=True, prompt=self.prompt, llm=self.llm)
        res = chain.predict(text=text, topic=topic)
        return res, coe_result_list


def find_in_answers(answers: List[str], cls: str):
    for ind, ans in enumerate(answers):
        if cls in ans:
            return ind
    return -1


def switch_by_index(answers: List[str], index1: int, index2: int):
    if index1 < 0 or index1 >= len(answers) or index2 < 0 or index2 >= len(answers):
        return answers
    answers[index1], answers[index2] = answers[index2], answers[index1]
    return answers


class COESummaryRunner(COEBaseRunner):
    def __init__(self, result_item: COEResult, _id: str):
        super().__init__(result_item, _id)
        self.llm.model_name = lion.config[f'{lion.app_name}.coe.cause.model_name']
        self.llm.openai_api_base = lion.config[f'{lion.app_name}.coe.cause.api_base']
        self.ask_prompt = get_prompt('cause', 'ask_prompt')
        self.refine_prompt = get_prompt('cause', 'refine_prompt')
        self.question_prompt = get_prompt('cause', 'question_prompt')
        self.document_variable_name = self.question_prompt.input_variables[0]
        self.initial_response_name = self.ask_prompt.input_variables[0]
        friday_model = lion.config[f'{lion.app_name}.coe.cause.friday_model']
        self.friday_model = Friday(model=friday_model, max_tokens=2048, direction='COE_CAUSE')

        prompt = get_prompt('cause', 'summary_system')
        self.summary_system = SystemMessagePromptTemplate(prompt=prompt)
        prompt = get_prompt('cause', 'system2')
        self.system = SystemMessagePromptTemplate(prompt=prompt)
        prompt = get_fewshoot('cause', 'cot_system', query_variable='query', k=2, dispatch_lion_by_type=True)
        self.cot_system = SystemMessagePromptTemplate(prompt=prompt)

        self.question_prompt = ChatPromptTemplate(messages=[
            self.summary_system,
            HumanMessagePromptTemplate(prompt=self.question_prompt)
        ], input_variables=self.question_prompt.input_variables)
        self.refine_prompt = ChatPromptTemplate(messages=[
            self.summary_system,
            HumanMessagePromptTemplate(prompt=self.refine_prompt)
        ], input_variables=self.refine_prompt.input_variables)

        # self.llm = Claude(auth_token=OPENAI_API_KEY, model='anthropic.claude-v1', temperature=0.01, verbose=True)
        # self.gpt35 = ChatOpenAI(model_name=GPT35NAME, streaming=True,
        #                         openai_api_base=OPENAI_API_BASE,
        #                         openai_api_key=OPENAI_API_KEY,
        #                         temperature=0.01,
        #                         request_timeout=120,
        #                         max_retries=6)
        self.jcjg_list: List[str] = json.loads(lion.config.get(f'{lion.app_name}.coe.cause.jcjg_list'))

    def make_answer(self, user: str, answer: str):
        '''在预校验的过程中写入answer，一般是不确定'''
        message = [MetaMessage('user', user),
                   MetaMessage('assistant', answer)]
        exp = create_experience(type=self.result_item.type,
                                coe_id=self.result_item.coe_id,
                                task_id=self.result_item.task_id,
                                message_list=message)
        self.result_item.answer_message.append(Answer(exp_id=exp.id))

    def valid_doc_timeline(self, docs: List[Document]):
        total = 0
        timeline_l = 0
        for doc in docs:
            if doc.metadata['desc'] in ['[时间线信息]']:
                total += len(doc.page_content)
                timeline_l += 1
        if total <= 500 or timeline_l <= 5:  # 没什么时间线信息
            return False
        return True

    def valid_doc_qa(self, docs: List[Document]):
        qa_l = 0
        for doc in docs:
            if doc.metadata['desc'] in ['[原因分析信息]']:
                qa_l += 1
        if qa_l <= 0:  # 根本没有原因分析信息
            return False
        return True

    def pre_check(self) -> bool:
        '''返回 to_do_next ，是否需要进行LLM询问'''
        if not self.valid_flg:
            self.make_answer('信息太少', '无法判断')
            self.result_item.reason = '信息太少，无法判断'
            return False
        title = self.breif_dict.get('[标题]', CrawlerData(data=''))
        apper = self.breif_dict.get('[现象]', CrawlerData(data=''))
        items = []
        for jcjg in self.jcjg_list:
            jcjg = jcjg.lower()
            if jcjg in title.data.lower()+apper.data.lower():
                items.append(jcjg)
        if len(items) != 0:
            content = '\n'.join([title.get_text(), apper.get_text()])
            flg, res = self.analysis_jcjg_(existing_answer=content, jcjg_list=items)
            if flg:
                self.make_answer(content, res)
                self.result_item.reason = content
                return False
        return True

    def load(self) -> List[Document]:
        loader = COELoader(coe_id=self.result_item.coe_id)
        docs = loader.load()
        valid_flg = self.valid_doc_qa(docs=docs)
        if not valid_flg:  # 如果qa没多少的话，就只能看时间线够不够多了
            valid_flg = self.valid_doc_timeline(docs=docs)
        self.valid_flg = valid_flg
        self.breif_dict = loader.brief_dict
        return docs

    def split(self, document: List[Document]) -> List[Document]:
        text_splitter = COESpliter()
        return text_splitter.split_documents(document)

    def summary_and_thought(self, document: List[Document]) -> str:
        # self.refine_llm_chain = LLMChain(verbose=True, prompt=self.refine_prompt, llm=self.llm)
        res = friday_chat(model=self.friday_model,
                          messages=self.question_prompt.format_messages(text=document[0].page_content),
                          callback=self.callback)
        refine_steps = [res]
        for doc in document[1:]:
            res = friday_chat(model=self.friday_model,
                              messages=self.refine_prompt.format_messages(text=doc.page_content,
                                                                          existing_answer=refine_steps[-1]),
                              callback=self.callback)
            refine_steps.append(res)
        answer = refine_steps[-1]
        self.result_item.reason = answer
        return answer

    # def analysis_third_class_(self, existing_answer: str):
    #     self.ask_third_class = get_prompt('cause', 'ask_third_class')
    #     prompt = ChatPromptTemplate(messages=[
    #         HumanMessagePromptTemplate(prompt=self.ask_third_class)
    #     ], input_variables=['existing_answer'])
    #     chain = LLMChain(verbose=True, prompt=prompt, llm=self.llm)
    #     res = chain.predict(callbacks=[self.callback], existing_answer=existing_answer)
    #     pattern = re.compile(r'- 判断[:：]\s*是')
    #     match = pattern.search(res)
    #     if match:
    #         res = pattern.sub("[第三方问题]", res)
    #         return True, res
    #     return False, res

    def analysis_jcjg_(self, existing_answer: str, jcjg_list: str):
        prompt = get_prompt('cause', 'jcjg')
        prompt = ChatPromptTemplate(messages=[prompt], input_variables=prompt.input_variables)
        res = friday_chat(model=self.friday_model, messages=prompt.format_prompt(
            existing_answer=existing_answer, jcjg_list=jcjg_list
        ), callback=self.callback)
        pattern = re.compile(r'- 判断[:：]\s*是')
        match = pattern.search(res)
        if match:
            res = pattern.sub("[基础架构]", res)
            return True, res
        return False, res

    # def analysis_jcss_(self, existing_answer: str):
    #     self.ask = get_prompt('cause', 'jcss')
    #     prompt = ChatPromptTemplate(messages=[
    #         HumanMessagePromptTemplate(prompt=self.ask)
    #     ], input_variables=['existing_answer'])
    #     chain = LLMChain(verbose=True, prompt=prompt, llm=self.llm)
    #     res = chain.predict(callbacks=[self.callback], existing_answer=existing_answer)
    #     pattern = re.compile(r'- 判断[:：]\s*是')
    #     match = pattern.search(res)
    #     if match:
    #         res = pattern.sub("[基础设施]", res)
    #         return True, res
    #     return False, res

    def analysis_other(self, existing_answer: str):
        prompt = ChatPromptTemplate(messages=[
            self.system,
            self.cot_system.format(query=existing_answer),
            HumanMessagePromptTemplate(prompt=self.ask_prompt)
        ], input_variables=['existing_answer'])
        messages = prompt.format_messages(
            existing_answer=existing_answer,
        )
        res = friday_chat(model=self.friday_model, messages=messages, callback=self.callback)
        return res

    def analysis_and_answer(self, existing_answer: str) -> str:
        # flg, res = self.analysis_third_class_(existing_answer)
        # if not flg:
        #     flg, res = self.analysis_jcjg_(existing_answer)
        # if not flg:
        #     flg, res = self.analysis_jcss_(existing_answer)
        # if flg:
        #     answer_list = [res]
        # else:
        res = self.analysis_other(existing_answer)
        answer_list = res.split('\n\n')
        for item in answer_list:
            if not item.strip().startswith('['):
                continue
            message = [
                MetaMessage('user', existing_answer),
                MetaMessage('assistant', item)
            ]
            exp = create_experience(type=self.result_item.type,
                                    coe_id=self.result_item.coe_id,
                                    task_id=self.result_item.task_id,
                                    message_list=message)
            self.result_item.answer_message.append(Answer(exp_id=exp.id))
            self.exps.append(exp)
        # self.result_item.similiar_case_list = self.cot_system.prompt.get_cot_cache()
        return res

    def deal_answer(self, existing_answer: str, answer: dict) -> str:

        res = answer.get("data", {}).get("choices", [{}])[0].get("message", {}).get("content", "")
        message = [
            MetaMessage('user', existing_answer),
            MetaMessage('assistant', str(res))
        ]
        exp = create_experience(type=self.result_item.type,
                                coe_id=self.result_item.coe_id,
                                task_id=self.result_item.task_id,
                                message_list=message)
        self.result_item.answer_message.append(Answer(exp_id=exp.id))
        self.result_item.message.append(MetaMessage('user', existing_answer))
        self.result_item.message.append(MetaMessage('assistant', str(res)))
        self.exps.append(exp)
        return res