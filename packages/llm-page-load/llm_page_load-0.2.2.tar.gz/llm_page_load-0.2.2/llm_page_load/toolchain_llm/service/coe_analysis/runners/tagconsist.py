from typing import List
from langchain.prompts import SystemMessagePromptTemplate, \
    HumanMessagePromptTemplate, ChatPromptTemplate
from langchain import LLMChain
from service.coe_analysis.coe_experience_service import create_experience
from service.coe_analysis.crawler.getDoc import get_tag
from service.coe_analysis.data_structure import Answer, COEResult, MetaMessage
from service.coe_analysis.runners.loaders import COELoader, Document, dispatch_COE_Spliter
from service.coe_analysis.runners.base import COEBaseRunner
from service.coe_analysis.runners.retriver import get_fewshoot, get_prompt
from utils import logger


class COETagConsistantRunner(COEBaseRunner):
    valid_type_list = ["trigger_condition"]
    valid_type_dict = {
        "trigger_condition": "触发条件一致性",
    }
    valid_k = {
        "trigger_condition": [1, 1, 1],
    }
    tag_not_need_to_analysis = {
        'trigger_condition': ['代码发布上线']
    }
    tag_name_dict = {
        'trigger_condition': '线上问题触发条件'
    }

    def __init__(self, result_item: COEResult, _id: str):
        super().__init__(result_item, _id)
        self.to_do_total = False
        self.tag = 'None'

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

    def pre_check(self) -> bool:
        coe_id = self.result_item.coe_id
        to_do_next = True
        tag_dict = get_tag(coe_id)
        tag = tag_dict.get(self.tag_name_dict[self.type], 'None')
        self.tag = tag
        not_need_to_analysis = self.tag_not_need_to_analysis.get(self.type, [])
        if tag in not_need_to_analysis:
            to_do_next = False
            self.result_item.message.append(MetaMessage(
                role='user', content=f'[预校验]\ntag为:\n{tag}'))
            self.result_item.message.append(MetaMessage(
                role='assistant', content=f'[预校验]\n判断结果: 准确\n线上问题触发条件:{tag}'))
            if not self.to_do_total:
                self.result_item.reason = f'[预校验]\n判断依据: {tag}直接认定为准确\n判断结果: 准确\n线上问题触发条件:{tag}'
                answer_messages = [
                    MetaMessage(role='user', content=self.result_item.reason),
                    MetaMessage(role='assistant', content=self.result_item.reason)
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
        return document

    def split(self, document: List[Document]) -> List[Document]:
        text_splitter = dispatch_COE_Spliter(self.type)
        return text_splitter.split_documents(document)

    def summary_and_thought(self, document: List[Document]) -> str:
        self.initial_llm_chain = LLMChain(verbose=True, prompt=self.question_prompt, llm=self.llm)
        self.refine_llm_chain = LLMChain(verbose=True, prompt=self.refine_prompt, llm=self.llm)
        res = self.initial_llm_chain.predict(callbacks=[self.callback],
                                             text=document[0].page_content,
                                             tag=self.tag)
        refine_steps = [res]
        for doc in document[1:]:
            res = self.refine_llm_chain.predict(callbacks=[self.callback],
                                                tag=self.tag,
                                                text=doc.page_content,
                                                existing_answer=refine_steps[-1])
            refine_steps.append(res)
        answer = refine_steps[-1]
        self.result_item.reason = answer
        return answer

    def analysis_and_answer(self, existing_answer: str) -> str:
        prompt = ChatPromptTemplate(messages=[
            self.cot_system.format(query=existing_answer),
            HumanMessagePromptTemplate(prompt=self.ask_prompt)
        ], input_variables=['existing_answer', 'tag'])
        if self.background_system_prompt:
            prompt = ChatPromptTemplate(messages=[
                SystemMessagePromptTemplate(prompt=self.background_system_prompt),
                self.cot_system.format(query=existing_answer),
                HumanMessagePromptTemplate(prompt=self.ask_prompt)
            ], input_variables=['existing_answer', 'tag'])
        chain = LLMChain(verbose=True, prompt=prompt, llm=self.llm)
        res = chain.predict(
            callbacks=[self.callback], existing_answer=existing_answer, tag=self.tag)
        message = [
            MetaMessage('user', existing_answer),
            MetaMessage('assistant', res)
        ]
        exp = create_experience(type=self.type, coe_id=self.result_item.coe_id,
                                task_id=self.result_item.task_id,
                                message_list=message)
        self.result_item.answer_message.append(Answer(exp_id=exp.id))
        self.result_item.similiar_case_list = \
            self.cot_system.prompt.get_cot_cache()
        return res
