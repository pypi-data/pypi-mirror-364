from typing import List
from langchain.document_loaders.base import BaseLoader
from langchain.schema import Document
from service.coe_analysis.crawler.getDoc import getBriefText, getCausesText, getTimeLineText
from token_count.tokenizer import count_token
import datetime
import re
from utils import logger


class COELoader(BaseLoader):
    def __init__(self, coe_id: str) -> None:
        super().__init__()
        self.coe_id = coe_id

    def load(self) -> List[Document]:
        coe_id = self.coe_id
        briefText = getBriefText(coe_id)
        self.brief_dict = {item.desc: item for item in briefText}
        timeLineText = getTimeLineText(coe_id)
        causesText = getCausesText(coe_id)
        lst = briefText+timeLineText+causesText
        documents = [
            Document(
                page_content=item.get_text(),
                metadata={'desc': item.desc, 'category': item.category, 'time_stamp': item.time_stamp})
            for item in lst]
        return documents


class COESpliter():
    def __init__(self):
        self.min_token = 12000

    def split_documents(self, documents: List[Document]):
        answer = []
        tmp = ''
        now_token = 0
        self.start = False
        for ind, document in enumerate(documents):
            # if document.metadata['category'] in ["分析故障根因", "分析故障定位", "分析规避方案", '分析Code Review流程'] \
            #         and document.metadata['desc'] in ['[原因分析信息]']:
            if document.metadata['desc'] in ['[原因分析信息]']:
                if document.metadata['category'] == '分析测试流程':  # 分析测试流程暂不分析
                    continue
                else:
                    tmp += document.page_content
            elif document.metadata['desc'] in ['[时间线信息]']:
                tmp += document.page_content
            elif document.metadata['desc'] in ['[发生时间]', '[标题]', '[现象]', '[客户影响]', '[故障类型]', '[经验教训]',
                                               '[正确做法]', '[开始处理时间]']:
                tmp += document.page_content
                now_token = count_token(tmp)
            if now_token > self.min_token:
                answer.append(Document(page_content=tmp, metadata={}))
                tmp = ''
        if (len(tmp) != 0):
            answer.append(Document(page_content=tmp, metadata={}))
        return answer


class COESpliter_to_test():
    def __init__(self):
        self.min_token = 5500
        self.start = False

    def split_documents(self, documents: List[Document]):
        answer = []
        tmp = ''
        self.start = True
        for ind, document in enumerate(documents):
            if document.metadata['desc'] in ['[原因分析信息]'] \
                    and document.metadata['category'] in ["分析测试流程", "分析规避方案", "分析故障发现", "分析Code Review流程", '分析故障根因']:
                tmp += document.page_content
            # elif document.metadata['desc'] in ['[时间线信息]']:
            #     tmp += document.page_content
            # elif document.metadata['desc'] in ['[时间线信息]'] and document.metadata['category'] in ['occur_time']:
            #     self.start = True
            #     tmp += document.page_content
            # elif document.metadata['desc'] in ['[时间线信息]'] and self.start \
            #         and document.metadata['category'] is not None and len(document.metadata['category']) != 0:
            #     tmp += document.page_content
            #     self.start = False
            elif document.metadata['desc'] in ['[发生时间]', '[标题]', '[故障类型]']:
                tmp += document.page_content
            elif document.metadata['desc'] in ['[研发自证]']:
                tmp += document.page_content
                if len(document.metadata.get('lnk', [])) != 0:
                    tmp += '链接:'+str(document.metadata.get('lnk')) + '\n'

            if (count_token(tmp) > self.min_token):
                answer.append(Document(page_content=tmp, metadata={}))
                tmp = ''
        # append to tail
        for ind, document in enumerate(documents):
            if document.metadata['desc'] in ['[经验教训]']:
                tmp += document.page_content
            elif document.metadata['desc'] in ['[研发自证]']:
                tmp += document.page_content
                if len(document.metadata.get('lnk', [])) != 0:
                    tmp += '链接:'+str(document.metadata.get('lnk')) + '\n'
            if (count_token(tmp) > self.min_token):
                answer.append(Document(page_content=tmp, metadata={}))
                tmp = ''
        if (len(tmp) != 0):
            answer.append(Document(page_content=tmp, metadata={}))
        return answer


class COESpliter_to_claim():
    def __init__(self):
        self.min_token = 3500
        self.start = False

    def split_documents(self, documents: List[Document]):
        answer = []
        tmp = ''
        self.start = False
        for ind, document in enumerate(documents):
            if document.metadata['desc'] in ['[原因分析信息]'] and document.metadata['category'] in ["分析变更流程"]:
                tmp += document.page_content
            # elif document.metadata['desc'] in ['[时间线信息]'] and document.metadata['category'] in ['occur_time']:
            #     self.start = True
            #     tmp += document.page_content
            elif document.metadata['desc'] in ['[时间线信息]']:
                tmp += document.page_content
            # elif self.start and document.metadata['desc'] in ['[时间线信息]', '[发生时间]']:
                # tmp += document.page_content
            elif document.metadata['desc'] in ['[发生时间]', '[标题]', '[故障类型]']:
                tmp += document.page_content
            elif document.metadata['desc'] in ['[研发自证]']:
                tmp += document.page_content
                if len(document.metadata.get('lnk', [])) != 0:
                    tmp += '链接:'+str(document.metadata.get('lnk')) + '\n'

            if (count_token(tmp) > self.min_token):
                answer.append(Document(page_content=tmp, metadata={}))
                tmp = ''
                # append to tail
        for ind, document in enumerate(documents):
            if document.metadata['desc'] in ['[经验教训]']:
                tmp += document.page_content
            if (count_token(tmp) > self.min_token):
                answer.append(Document(page_content=tmp, metadata={}))
                tmp = ''
        if (len(tmp) != 0):
            answer.append(Document(page_content=tmp, metadata={}))
        return answer


class COESpliter_to_check():
    def __init__(self):
        self.min_token = 3500
        self.start = False

    def split_documents(self, documents: List[Document]):
        answer = []
        tmp = ''
        self.start = False
        for ind, document in enumerate(documents):
            if document.metadata['desc'] in ['[原因分析信息]'] and document.metadata['category'] in ["分析Code Review流程", "其他", "分析变更流程"]:
                tmp += document.page_content
            elif document.metadata['desc'] in ['[时间线信息]']:
                tmp += document.page_content
            elif document.metadata['desc'] in ['[发生时间]', '[标题]', '[故障类型]']:
                tmp += document.page_content
            elif document.metadata['desc'] in ['[研发自证]']:
                tmp += document.page_content
                if len(document.metadata.get('lnk', [])) != 0:
                    tmp += '链接:'+str(document.metadata.get('lnk')) + '\n'

            if (count_token(tmp) > self.min_token):
                answer.append(Document(page_content=tmp, metadata={}))
                tmp = ''
        for ind, document in enumerate(documents):
            if document.metadata['desc'] in ['[经验教训]', '[研发自证]']:
                tmp += document.page_content
            if (count_token(tmp) > self.min_token):
                answer.append(Document(page_content=tmp, metadata={}))
                tmp = ''
        if (len(tmp) != 0):
            answer.append(Document(page_content=tmp, metadata={}))
        return answer


class COESpliter_to_grey_new():
    def __init__(self):
        self.min_token = 3500
        self.start = False

    def split_time_line(self, documents: List[Document]):
        tmp = ''
        answer = []
        for ind, document in enumerate(documents):
            if document.metadata['desc'] in ['[时间线信息]', '[发生时间]', '[标题]', '[故障类型]']:
                tmp += document.page_content
            if (count_token(tmp) > self.min_token):
                answer.append(Document(page_content=tmp, metadata={'phase': '[时间线信息]'}))
                tmp = ''
        if (len(tmp) != 0):
            answer.append(Document(page_content=tmp, metadata={'phase': '[时间线信息]'}))
        return answer

    def split_qa(self, documents: List[Document]):
        tmp = ''
        answer = []
        for ind, document in enumerate(documents):
            if document.metadata['desc'] in ['[原因分析信息]'] \
                    and document.metadata['category'] in ["其他", "分析测试流程", "分析故障定位", "分析处理流程"]:
                tmp += document.page_content
            if (count_token(tmp) > self.min_token):
                answer.append(Document(page_content=tmp, metadata={'phase': '[原因分析信息]'}))
                tmp = ''
        if (len(tmp) != 0):
            answer.append(Document(page_content=tmp, metadata={'phase': '[原因分析信息]'}))
        return answer

    def split_self_prove(self, documents: List[Document]):
        tmp = ''
        answer = []
        occur = False
        for ind, document in enumerate(documents):
            if document.metadata['desc'] in ['[研发自证]']:
                tmp += document.page_content
                occur = True
                if len(document.metadata.get('lnk', [])) != 0:
                    tmp += '链接:'+str(document.metadata.get('lnk')) + '\n'
            elif document.metadata['desc'] in ['[发生时间]']:
                tmp += document.page_content
            if (count_token(tmp) > self.min_token):
                answer.append(Document(page_content=tmp, metadata={'phase': '[自证]'}))
                tmp = ''
        if (len(tmp) != 0):
            answer.append(Document(page_content=tmp, metadata={'phase': '[自证]'}))
        return answer if occur else []

    def split_sum_up(self, documents: List[Document]):
        tmp = ''
        answer = []
        for ind, document in enumerate(documents):
            if document.metadata['desc'] in ['[经验教训]']:
                tmp += document.page_content
            if (count_token(tmp) > self.min_token):
                answer.append(Document(page_content=tmp, metadata={'phase': '[反思]'}))
                tmp = ''
        if (len(tmp) != 0):
            answer.append(Document(page_content=tmp, metadata={'phase': '[反思]'}))
        return answer

    def split_documents(self, documents: List[Document]):
        return [
            *self.split_self_prove(documents),
            *self.split_time_line(documents),
            *self.split_qa(documents),
            *self.split_sum_up(documents),
        ]


class COESpliter_to_grey():
    def __init__(self):
        self.min_token = 3500
        self.start = False

    def split_documents(self, documents: List[Document]):
        answer = []
        tmp = ''
        self.start = False
        for ind, document in enumerate(documents):
            if document.metadata['desc'] in ['[原因分析信息]'] \
                    and document.metadata['category'] in ["其他", "分析测试流程", "分析故障定位", "分析处理流程"]:
                tmp += document.page_content
            elif document.metadata['desc'] in ['[时间线信息]']:
                tmp += document.page_content
            elif document.metadata['desc'] in ['[发生时间]', '[标题]', '[故障类型]']:
                tmp += document.page_content
            elif document.metadata['desc'] in ['[研发自证]']:
                tmp += document.page_content
                if len(document.metadata.get('lnk', [])) != 0:
                    tmp += '链接:'+str(document.metadata.get('lnk')) + '\n'

            if (count_token(tmp) > self.min_token):
                answer.append(Document(page_content=tmp, metadata={}))
                tmp = ''
            # elif document.metadata['desc'] in ['[时间线信息]'] and not self.start and count_token(tmp) > 50 \
            #         and '[研发人员自己声明]' in tmp:
            #     # 单独判断开头，进行强调
            #     self.start = True
            #     answer.append(Document(page_content=tmp, metadata={}))
            #     tmp = ''
        for ind, document in enumerate(documents):
            if document.metadata['desc'] in ['[经验教训]', '[研发自证]']:
                tmp += document.page_content
            if (count_token(tmp) > self.min_token):
                answer.append(Document(page_content=tmp, metadata={}))
                tmp = ''
        if (len(tmp) != 0):
            answer.append(Document(page_content=tmp, metadata={}))
        return answer


class COESpliter_to_inspect():
    def __init__(self):
        self.min_token = 3500
        self.start = False

    def split_documents(self, documents: List[Document]):
        answer = []
        tmp = ''
        self.start = False
        for ind, document in enumerate(documents):
            if document.metadata['desc'] in ['[原因分析信息]'] \
                    and document.metadata['category'] in ["其他", "分析故障发现", "分析故障响应", "分析故障定位"]:
                tmp += document.page_content
            elif document.metadata['desc'] in ['[时间线信息]']:
                tmp += document.page_content
            elif document.metadata['desc'] in ['[发生时间]', '[标题]', '[故障类型]']:
                tmp += document.page_content
            elif document.metadata['desc'] in ['[研发自证]']:
                tmp += document.page_content
                if len(document.metadata.get('lnk', [])) != 0:
                    tmp += '链接:'+str(document.metadata.get('lnk')) + '\n'

            if (count_token(tmp) > self.min_token):
                answer.append(Document(page_content=tmp, metadata={}))
                tmp = ''
        for ind, document in enumerate(documents):
            if document.metadata['desc'] in ['[经验教训]', '[研发自证]']:
                tmp += document.page_content
            if (count_token(tmp) > self.min_token):
                answer.append(Document(page_content=tmp, metadata={}))
                tmp = ''
        if (len(tmp) != 0):
            answer.append(Document(page_content=tmp, metadata={}))
        return answer


class COESpliter_to_rollback():
    def __init__(self):
        self.min_token = 3500
        self.start = False

    def split_documents(self, documents: List[Document]):
        answer = []
        tmp = ''
        self.start = False
        for ind, document in enumerate(documents):
            if document.metadata['desc'] in ['[原因分析信息]'] \
                    and document.metadata['category'] in ["其他", "分析应急预案", "分析变更流程", "分析故障响应", "分析处理流程"]:
                tmp += document.page_content
            elif document.metadata['desc'] in ['[时间线信息]', '[经验教训]']:
                tmp += document.page_content
            elif document.metadata['desc'] in ['[开始处理时间]', '[标题]', '[故障类型]']:
                tmp += document.page_content
            elif document.metadata['desc'] in ['[研发自证]']:
                tmp += document.page_content
                if len(document.metadata.get('lnk', [])) != 0:
                    tmp += '链接:'+str(document.metadata.get('lnk')) + '\n'

            if (count_token(tmp) > self.min_token):
                answer.append(Document(page_content=tmp, metadata={}))
                tmp = ''
        for ind, document in enumerate(documents):
            if document.metadata['desc'] in ['[经验教训]', '[研发自证]']:
                tmp += document.page_content
            if (count_token(tmp) > self.min_token):
                answer.append(Document(page_content=tmp, metadata={}))
                tmp = ''
        if (len(tmp) != 0):
            answer.append(Document(page_content=tmp, metadata={}))
        return answer


class COESpliter_not_to_delay():
    def __init__(self):
        self.min_token = 4500
        self.start = None

    def prase_time_stamp(self, text):
        pattern = r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}"
        match = re.search(pattern, text)
        if not match:
            return None
        else:
            return datetime.datetime.strptime(match.group(), "%Y-%m-%d %H:%M:%S")

    def diff_time_stamp(self, text):
        if self.start is None or text is None:
            return True
        try:
            start = self.prase_time_stamp(self.start)
            now = self.prase_time_stamp(text)
            diff = now - start
            if diff.total_seconds() / 60 <= 30:
                return True
            else:
                return False
        except Exception as e:
            logger.warn(e.args)
            return True

    def split_documents(self, documents: List[Document]):
        answer = []
        tmp = ''
        self.start = None
        for ind, document in enumerate(documents):
            # 计算是否delay，需要起始时间，30分钟以外的就不算了
            if document.metadata['desc'] in ['[时间线信息]']:
                category = document.metadata['category']
                if category in ['handle_time']:
                    self.start = document.metadata['time_stamp']

            if document.metadata['desc'] in ['[原因分析信息]'] \
                    and document.metadata['category'] in ["其他", "分析应急预案", "分析故障响应", "分析故障影响", "分析故障发现", "分析处理流程"]:
                tmp += document.page_content
            elif document.metadata['desc'] in ['[时间线信息]']:
                # if self.diff_time_stamp(document.metadata['time_stamp']):
                tmp += document.page_content
            elif document.metadata['desc'] in ['[开始处理时间]', '[标题]', '[经验教训]', '[故障类型]']:
                tmp += document.page_content
            elif document.metadata['desc'] in ['[研发自证]']:
                tmp += document.page_content
                if len(document.metadata.get('lnk', [])) != 0:
                    tmp += '链接:'+str(document.metadata.get('lnk')) + '\n'
            if (count_token(tmp) > self.min_token):
                answer.append(Document(page_content=tmp, metadata={}))
                tmp = ''
        for ind, document in enumerate(documents):
            if document.metadata['desc'] in ['[经验教训]', '[研发自证]']:
                tmp += document.page_content
            if (count_token(tmp) > self.min_token):
                answer.append(Document(page_content=tmp, metadata={}))
                tmp = ''
        if (len(tmp) != 0):
            answer.append(Document(page_content=tmp, metadata={}))
        return answer


class COESpliter_not_to_illagle_change_data():
    def __init__(self):
        self.min_token = 3500
        self.start = False

    def split_documents(self, documents: List[Document]):
        answer = []
        tmp = ''
        self.start = False
        for ind, document in enumerate(documents):
            if document.metadata['desc'] in ['[原因分析信息]'] \
                    and document.metadata['category'] in ["分析故障根因", "分析变更流程", "分析故障响应", "分析处理流程", "分析故障定位", "分析故障发现"]:
                tmp += document.page_content
            elif document.metadata['desc'] in ['[时间线信息]']:
                tmp += document.page_content
            elif document.metadata['desc'] in ['[发生时间]', '[标题]', '[故障类型]']:
                tmp += document.page_content
            elif document.metadata['desc'] in ['[研发自证]']:
                tmp += document.page_content
                if len(document.metadata.get('lnk', [])) != 0:
                    tmp += '链接:'+str(document.metadata.get('lnk')) + '\n'

            if (count_token(tmp) > self.min_token):
                answer.append(Document(page_content=tmp, metadata={}))
                tmp = ''
        for ind, document in enumerate(documents):
            if document.metadata['desc'] in ['[经验教训]', '[研发自证]']:
                tmp += document.page_content
            if (count_token(tmp) > self.min_token):
                answer.append(Document(page_content=tmp, metadata={}))
                tmp = ''
        if (len(tmp) != 0):
            answer.append(Document(page_content=tmp, metadata={}))
        return answer


class COESpliter_null_check():
    def __init__(self):
        self.min_token = 1000
        self.start = False

    def split_documents(self, documents: List[Document]):
        answer = []
        tmp = ''
        self.start = False
        for ind, document in enumerate(documents):
            if document.metadata['category'] in ["分析故障根因", "分析故障定位", "分析规避方案"] \
                    and document.metadata['desc'] in ['[原因分析信息]']:
                tmp += document.page_content
            elif document.metadata['category'] in ['location_time']:
                self.start = True
                tmp += document.page_content
            elif self.start and document.metadata['desc'] in ['[时间线信息]', '[发生时间]']:
                tmp += document.page_content
            elif document.metadata['desc'] in ['[标题]', '[现象]']:
                tmp += document.page_content
            if (count_token(tmp) > self.min_token):
                answer.append(Document(page_content=tmp, metadata={}))
                tmp = ''
        if (len(tmp) != 0):
            answer.append(Document(page_content=tmp, metadata={}))
        return answer


class COESpliter_fund_acc():
    def __init__(self):
        self.min_token = 1000
        self.start = False

    def split_documents(self, documents: List[Document]):
        answer = []
        tmp = ''
        self.start = False
        for ind, document in enumerate(documents):
            if document.metadata['category'] in ["分析故障根因", "分析故障定位", "分析故障发现", '分析故障响应'] \
                    and document.metadata['desc'] in ['[原因分析信息]']:
                tmp += document.page_content
            elif document.metadata['category'] in ['location_time']:
                self.start = True
                tmp += document.page_content
            elif self.start and document.metadata['desc'] in ['[时间线信息]']:
                tmp += document.page_content
            elif document.metadata['desc'] in ['[标题]', '[现象]']:
                tmp += document.page_content
            if (count_token(tmp) > self.min_token):
                answer.append(Document(page_content=tmp, metadata={}))
                tmp = ''
        if (len(tmp) != 0):
            answer.append(Document(page_content=tmp, metadata={}))
        return answer


class COESpliter_trigger_condition():
    def __init__(self):
        self.min_token = 1000
        self.start = False

    def split_documents(self, documents: List[Document]):
        answer = []
        tmp = ''
        self.start = True
        for ind, document in enumerate(documents):
            if document.metadata['desc'] in ['[原因分析信息]']:
                tmp += document.page_content
            elif document.metadata['desc'] in ['[发生时间]', '[标题]', '[时间线信息]']:
                tmp += document.page_content
            if (count_token(tmp) > self.min_token):
                answer.append(Document(page_content=tmp, metadata={}))
                tmp = ''
        # append to tail
        for ind, document in enumerate(documents):
            if document.metadata['desc'] in ['[经验教训]']:
                tmp += document.page_content
            if (count_token(tmp) > self.min_token):
                answer.append(Document(page_content=tmp, metadata={}))
                tmp = ''
        if (len(tmp) != 0):
            answer.append(Document(page_content=tmp, metadata={}))
        return answer


spliter_dict = {
    'cause': COESpliter(),
    'to_test': COESpliter_to_test(),
    'to_claim': COESpliter_to_claim(),
    'to_check': COESpliter_to_check(),
    'to_grey': COESpliter_to_grey(),
    'to_inspect': COESpliter_to_inspect(),
    'to_rollback': COESpliter_to_rollback(),
    'not_to_delay': COESpliter_not_to_delay(),
    'not_to_illagle_change_data': COESpliter_not_to_illagle_change_data(),
    'null_check': COESpliter_null_check(),
    'fund_acc': COESpliter_fund_acc(),
    'fund_activity_save': COESpliter_fund_acc(),
    'rule_safety': COESpliter_fund_acc(),
    'trigger_condition': COESpliter_trigger_condition()
}


def get_COE_6to2not_Spliter(template):
    return spliter_dict.get(template, COESpliter())


def dispatch_COE_Spliter(template):
    return spliter_dict.get(template, COESpliter())
