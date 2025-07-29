from typing import List
from langchain.document_loaders.base import BaseLoader
from langchain.schema import Document
from service.coe_analysis.search_coe_result_item import search_coe_result_item
from service.coe_analysis.crawler.getDoc import getBriefText, getCausesText, getTimeLineText
from service.coe_analysis.coe_store_service import search_coe
from service.coe_analysis.runners.base import COEBaseRunner
from service.coe_analysis.data_structure import Arg, COEResult
from service.coe_analysis.runners.retriver import LLMCallback2
from service.lang_chain_utils.helper import friday_chat
from service.lang_chain_utils.lion_client import client as lion
from llmcore_sdk.models.friday import Friday
from langchain.schema.messages import HumanMessage
from utils import logger


class DeterminateSearchLoader(BaseLoader):
    def __init__(self, coe_id: str, content_fields: list) -> None:
        super().__init__()
        self.coe_id = coe_id
        self.content_fields = content_fields
        self.brief = None
        self.causes = None

    def get_cause_sum(self) -> List[Document]:
        coe_store, _ = search_coe(coe_id=self.coe_id)
        cause_task = coe_store.cause_analysis.analysis_task_id
        if isinstance(cause_task, list) and len(cause_task) > 0:
            cause_task = cause_task[0]
        result_item, _id = search_coe_result_item(self.coe_id, 'cause', cause_task)
        summary = result_item.reason
        return [Document(page_content=f'总结结果：{summary}\n\n')]

    def get_brief(self, field):
        if self.brief is None:
            self.brief = getBriefText(self.coe_id, scenetivity=True)
        for text in self.brief:
            if text.desc == field:
                return [Document(page_content=text.get_text())]
        return []

    def get_cuases(self, field):
        if self.causes is None:
            self.causes = getCausesText(id=self.coe_id)
        for text in self.causes:
            if text.desc == '[原因分析信息]' and text.category == field:
                return [Document(page_content=text.get_text())]
        return []

    def get_timeline(self):
        timeline = getTimeLineText(id=self.coe_id)
        return [Document(page_content=text.get_text()) for text in timeline]

    def load(self) -> List[Document]:
        docs = []
        func_map = {
            '智能总结': self.get_cause_sum,
            '时间线': self.get_timeline
        }
        for field in self.content_fields:
            if field in func_map:
                func = func_map.get(field)
                try:
                    docs.extend(func())
                except Exception as e:
                    logger.exception(repr(e))
                    pass
            elif field in ['[发生时间]', '[标题]', '[现象]', '[客户影响]', '[故障类型]',
                           '[经验教训]', '[正确做法]', '[开始处理时间]']:
                docs.extend(self.get_brief(field))
            elif field in ["分析测试流程", "分析规避方案", "分析故障发现", "分析Code Review流程", '分析故障根因', "分析故障影响",
                           "分析应急预案", "分析测试流程", "分析变更流程", "分析故障响应", "分析故障定位", "分析处理流程", "其他"]:
                docs.extend(self.get_cuases(field))
        return docs


class DeterminateSearchRunner(COEBaseRunner):
    valid_type_list = ['determinate_search']

    def __init__(self, result_item: COEResult, _id: str, args: List[Arg] = []):
        super().__init__(result_item, _id)
        lion.fetch_config()
        self.model_name = 'deepseek-chat'
        self.cretia = ''
        self.few_shot = ''
        self.content_fields = ['智能总结', '[标题]', '[现象]', '[故障类型]', '[经验教训]']
        self.keywords = []
        self.system_prompt = ''
        self.output_format = '请按照如下格式输出: \n回答: 相关 或者 不相关\n原因: '
        for arg in args:
            if arg.key == 'model':
                self.model_name = arg.value
            elif arg.key == 'cretia':
                self.cretia = arg.value
            elif arg.key == 'few_shot':
                self.few_shot = arg.value
            elif arg.key == 'content_fields' and arg.value and len(arg.value) != 0:
                self.content_fields = arg.value.split(',')
            elif arg.key == 'keywords' and arg.value and len(arg.value) != 0:
                self.keywords = arg.value.split(',')
            elif arg.key == 'system':
                self.system_prompt = arg.value
            elif arg.key == 'output_format':
                self.output_format = arg.value
        self.type = 'determinate_search'
        self.model = Friday(model=self.model_name, max_tokens=1024, temperature=0.1, direction='COE')
        self.callback = LLMCallback2(result_item=result_item, _id=_id)

    def load(self) -> List[Document]:
        self.loader = DeterminateSearchLoader(coe_id=self.result_item.coe_id, content_fields=self.content_fields)
        return self.loader.load()

    def split(self, document: List[Document]) -> List[Document]:
        self.docs = document
        return document

    def pre_check(self) -> bool:
        if len(self.docs) == 0:
            self.make_answer('信息太少', '回答: 无法判断\n原因:信息太少')
            self.result_item.reason = '信息太少，无法判断'
            return False
        for keyword in self.keywords:
            for doc in self.docs:
                if keyword in doc.page_content:
                    self.make_answer(doc.page_content, f'回答: 相关\n原因:匹配到关键词: {keyword}')
                    self.result_item.reason = doc.page_content + f'\n\n匹配到关键词: {keyword}'
                    return False
        return True

    def summary_and_thought(self, document: List[Document]) -> str:
        in_all = ''.join([i.page_content for i in document])
        self.result_item.reason = in_all
        return in_all

    def analysis_and_answer(self, existing_answer: str) -> str:
        prompt = []
        if self.system_prompt and len(self.system_prompt) != 0:
            prompt.append(f'背景知识: {self.system_prompt}')
        prompt.append('--------筛选条件如下--------')
        prompt.append(self.cretia)
        if self.few_shot and len(self.few_shot) != 0:
            prompt.append('--------示例如下--------')
            prompt.append(self.few_shot)
        prompt.append('--------COE内容如下--------')
        prompt.append(existing_answer)
        prompt.append('--------请按照如下格式作答----------')
        prompt.append(self.output_format)
        prompt = '\n'.join(prompt)
        answer = friday_chat(self.model, messages=[HumanMessage(content=prompt)], callback=self.callback)
        self.make_answer(prompt, answer)
        return answer
