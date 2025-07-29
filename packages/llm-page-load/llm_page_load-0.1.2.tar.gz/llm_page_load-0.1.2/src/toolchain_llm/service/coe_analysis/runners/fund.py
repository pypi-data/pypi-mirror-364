from typing import Dict, List, Tuple
from langchain.prompts import SystemMessagePromptTemplate, \
    HumanMessagePromptTemplate, ChatPromptTemplate, AIMessagePromptTemplate
from langchain import PromptTemplate
from service.coe_analysis.coe_experience_service import create_experience
from service.coe_analysis.coe_store_service import search_coe
from service.coe_analysis.crawler.getDoc import get_6to2notto, getBriefText, get_tag
from service.coe_analysis.data_structure import Answer, COEResult, COEStoreageData, MetaMessage
from service.coe_analysis.runners.loaders import COELoader, COESpliter_fund_acc, Document
from service.coe_analysis.runners.base import COEBaseRunner
from service.coe_analysis.runners.retriver import LLMCallback2, get_chat_prompt, get_prompt
from service.lang_chain_utils.helper import friday_chat
from service.lang_chain_utils.lion_client import client as lion
from llmcore_sdk.models.chatglm import ChatGLM
from token_count.tokenizer import count_token
from llmcore_sdk.models import Friday
import re
import os
from service.coe_analysis.llm_sdk_importer import es_util
import json

EXTRA_TXT = """
在分析线上问题影响的时候，建议思考以下问题:

1. 异常访问是否发生在某个特定的时间段?如果是,那么可以考虑这个时间段内的订单损失情况。

2. 异常访问是否影响到了所有门店?如果是,那么可以考虑所有门店的订单损失情况。

3. 是否有其他客户反馈也遇到了类似的问题?如果有,那么可以考虑这个因素对订单损失的影响。

4. 是否有官方声明或公告来解释这个问题?如果有,那么可以参考官方公告来判断是否有订单损失。
"""


def batch_search_chain_by_id(chain_id_list: List[str], size: int = 1000) -> Tuple[List[COEResult], List[str]]:
    try:
        query_josn = {
            "query": {"bool": {"must": [
                {"terms": {"id": chain_id_list}}
            ]}},
            "size": size
        }
        answer = es_util.search(index='coe_analysis_detail', query=query_josn)
        items = [COEResult.from_es(i) for i in answer]
        _ids = [i['_id'] for i in answer]
        return items, _ids
    except Exception:
        return None, None


class COEFoundJudgementLoader(COELoader):
    def __init__(self, coe_id: str) -> None:
        super().__init__(coe_id=coe_id)
        self.coe_id = coe_id

    def load(self) -> List[Document]:
        coe_id = self.coe_id
        tags = get_tag(coe_id)
        tag_content = ''
        for phase in ['订单损失量', '涉及金额（元）', '实际资损金额（元）', '财务差异金额（元）']:
            if phase not in tags:
                continue
            text = tags[phase]
            try:
                if float(text) > 0:
                    tag_content += f'{phase}: {text}'
            except Exception:
                continue
        briefText = getBriefText(coe_id, scenetivity=False)
        documents = [
            Document(
                page_content=item.get_text(),
                metadata={'desc': item.desc, 'category': item.category, 'time_stamp': item.time_stamp})
            for item in briefText if item.desc in ['[标题]', '[现象]', '[客户影响]']
        ]
        self.brief_dict = {item.desc: item for item in briefText}
        self.tags = tags
        if len(tag_content) != 0:
            documents = [Document(page_content=tag_content, metadata={
                                  'desc': '[额外标签信息]'})] + documents
        return documents


class COEFundJudgementRunner(COEBaseRunner):
    valid_type_list = ['fund_judgement']

    def init_model(self):
        temperature = lion.config[f'{lion.app_name}.coe.temperature']
        self.glm = ChatGLM(temperature=temperature)
        Env = os.getenv('Env', 'dev')
        if Env != 'pord':
            self.glm.host = 'https://aiengineering.sankuai.com/conversation/chatglm'

    def __init__(self, result_item: COEResult, _id: str):
        super().__init__(result_item, _id)
        lion.fetch_config()
        lion_prefix = f'{lion.app_name}.coe'
        self.type = 'fund_judgement'
        self.question = get_chat_prompt(self.type, 'question', prefix=lion_prefix)
        self.ask = get_prompt(self.type, 'ask', prefix=lion_prefix)
        self.name_check_prompt = get_prompt(self.type, 'name_check', prefix=lion_prefix)
        self.init_model()
        self.max_token = 3000
        self.callback = LLMCallback2(result_item=result_item, _id=_id)

    def check_name(self, name: str) -> bool:
        '''如果名字里面有某些关键词的话，就默认召回，如果是无法确定的话，就给一些自查的建议'''
        keys = {
            "风险要素关键词": {
                "价": ['底价', '卖价', '佣金率', '商品库存'],
                "惠": ['优惠商品', '优惠人群', '优惠库存', '优惠预算'],
                "买/约": ['实付', '发票', '税费', '时区', '汇率', '币种'],
                "佣/润": ['佣金', '账单', '付款单', '发票'],
                "帐": ['财务']
            },
            "风险类型关键词": ['商品不可售卖', '商品价格错误', '优惠价格错误', '选人错误', '分摊错误', '清分错误', '超佣', '零佣', '负佣'],
            "其他": ['风控']
        }
        self.check_name_reason = '不确定'
        for k, v in keys['风险要素关键词'].items():
            for key in v:
                if key in name:
                    self.check_name_reason = f'标题: {name}\n含有关键词:{key},属于 风险要素关键词 {k}'
                    return True
        for key in keys['风险类型关键词']:
            if key in name:
                self.check_name_reason = f'标题: {name}\n含有关键词:{key},属于 风险类型关键词'
                return True
        for key in keys['其他']:
            if key in name:
                self.check_name_reason = f'标题: {name}\n含有关键词:{key}'
                return True
        # chain = LLMChain(
        #     verbose=True, prompt=self.name_check_prompt, llm=self.llm)
        # answer = chain.predict(callbacks=[self.callback], title=name)
        # self.check_name_reason = answer
        # pattern = re.compile(r'是否存在资金风险[:：]\s*([\u4e00-\u9fa5]+)')
        # match = pattern.findall(answer)
        # if (len(match) > 0):
        #     ans = str(match[0])
        #     if '是' in ans:
        #         return True
        # return False
        return True

    def check_info_exist(self, tags: Dict[str, str]) -> bool:
        '''如果信息都是缺的，完全无法判断的话，那么就不会召回，问的话结果也是不相关，不会告诉RD'''
        for phase in ['订单损失量', '涉及金额（元）', '实际资损金额（元）', '财务差异金额（元）']:
            if phase not in tags:
                continue
            elif tags[phase] == 'None':
                continue
            else:
                return True
        return False

    def make_answer(self, user: str, answer: str):
        '''在预校验的过程中写入answer，一般是不确定'''
        message = [MetaMessage('user', user),
                   MetaMessage('assistant', answer)]
        exp = create_experience(type=self.result_item.type,
                                coe_id=self.result_item.coe_id,
                                task_id=self.result_item.task_id,
                                message_list=message)
        self.result_item.answer_message.append(Answer(exp_id=exp.id))

    def pre_check(self) -> bool:
        # 1. 通过名字预判断是不是风控类型的COE
        name = self.breif_dict.get('[标题]', None)
        if name is not None:
            name = name.data
        else:
            name = ''
        name_fk_flg = self.check_name(name)
        # 2. 信息缺失校验，如果信息缺失且不是风控的，那么就算不相关。
        #    如果风控相关，但是信息缺失了，那么就输出填写建议
        #    如果风控相关，而且信息至少填了一些，那么很有可能就是资损的COE，除非RD分析出不涉及。这一点预计通过大模型校验
        tags = self.tags
        info_exist_flg = self.check_info_exist(tags)
        if not name_fk_flg:
            self.result_item.reason = self.check_name_reason
            self.make_answer(self.check_name_reason, '不相关')
            # 不进行下一步
            return False
        else:
            self.result_item.reason = self.check_name_reason
            self.make_answer(self.check_name_reason, '缺少内容无法确认，倾向于认为有资金安全风险')
            # 不进行下一步，这个算召回
            if not info_exist_flg:
                return False
        return True

    def load(self) -> List[Document]:
        loader = COEFoundJudgementLoader(coe_id=self.result_item.coe_id)
        self.loader = loader
        docs = loader.load()
        # load 的内部会额外产生 brief_dict，由于不符合loader父类所以不是正常返回。
        self.breif_dict = loader.brief_dict
        self.tags = loader.tags
        return docs

    def split(self, document: List[Document]) -> List[Document]:
        text = ''
        tokens = 0
        for d in document:
            cur_token = count_token(d.page_content)
            if tokens + cur_token > self.max_token:
                break
            tokens += cur_token
            text += d.page_content
        return [Document(page_content=text, metadata={'tokens': tokens})]

    def summary_and_thought(self, document: List[Document]) -> str:
        answer = friday_chat(model=self.friday_model,
                             messages=self.question.format_messages(text=document[0].page_content,
                                                                    title=self.result_item.brief),
                             callback=self.callback)
        return answer

    def search_json(self, text):
        pattern = r'\{.*\}'
        # 搜索匹配的内容
        match = re.search(pattern, text)
        # 检查是否找到了匹配的内容
        if match:
            # 获取匹配的字符串
            matched_json = match.group()
            return json.loads(matched_json)
        else:
            return {}

    def analysis_and_answer(self, existing_answer: str) -> str:
        to_do_glm = False
        pattern = re.compile(r'回答[:：]\s*([\u4e00-\u9fa5]+)')
        match = pattern.findall(existing_answer)
        if (len(match) > 0):
            answer = str(match[0])
        elif '是' in existing_answer.split('\n')[0]:
            answer = '是'
        elif '否' in existing_answer.split('\n')[0]:
            answer = '否'
        else:
            answer = existing_answer

        if answer == '否':
            answer = '虽无明确金额损失或者财务差异, 但是建议关注其资金风险情况'
        self.make_answer(existing_answer, answer)
        if to_do_glm:
            '''以前判断由于包含敏感信息，所以要glm，现在看好像还行'''
            prompt = self.ask.format(text=existing_answer)
            answer = self.glm(prompt, callbacks=[self.callback])
            json_content = self.search_json(answer)
            ans = json_content.get('is_fund_save', answer)
            message = [MetaMessage('user', existing_answer),
                       MetaMessage('assistant', ans)]
            exp = create_experience(type=self.result_item.type,
                                    coe_id=self.result_item.coe_id,
                                    task_id=self.result_item.task_id,
                                    message_list=message)
            self.result_item.answer_message.append(Answer(exp_id=exp.id))
        return answer


class COEFundProblemRunner(COEBaseRunner):
    valid_type_list = ['fund_acc', 'fund_activity_save', 'rule_safety']

    def __init__(self, result_item: COEResult, _id: str):
        super().__init__(result_item, _id)

    def init_prompt(self, type):
        self.chain_system_prompt = get_prompt(type, 'chain_system_prompt')
        self.system_prompt = get_prompt(type, 'system_prompt')
        self.ask_prompt = get_prompt(type, 'ask_prompt')
        self.refine_prompt = get_prompt(type, 'refine_prompt')
        self.question_prompt = get_prompt(type, 'question_prompt')
        self.prefix_prompt = get_prompt(type, 'prefix_prompt')
        self.yes_prompt = PromptTemplate(
            template='好的我知道了，我会按照这个经验知识分析线上问题', input_variables=[])
        self.document_variable_name = self.question_prompt.input_variables[0]
        self.initial_response_name = self.ask_prompt.input_variables[0]

    def pre_check(self) -> bool:
        '''返回 to_do_next ，是否需要进行LLM询问'''
        return True

    def load(self) -> List[Document]:
        loader = COELoader(coe_id=self.result_item.coe_id)
        return loader.load()

    def split(self, document: List[Document]) -> List[Document]:
        text_splitter = COESpliter_fund_acc()
        return text_splitter.split_documents(document)

    def summary_and_thought(self, document: List[Document]) -> str:
        question_prompt = ChatPromptTemplate(messages=[
            SystemMessagePromptTemplate(prompt=self.chain_system_prompt),
            HumanMessagePromptTemplate(prompt=self.question_prompt)
        ], input_variables=self.question_prompt.input_variables)
        refine_prompt = ChatPromptTemplate(messages=[
            SystemMessagePromptTemplate(prompt=self.chain_system_prompt),
            HumanMessagePromptTemplate(prompt=self.refine_prompt)
        ], input_variables=self.refine_prompt.input_variables)
        res = friday_chat(model=self.friday_model,
                          messages=question_prompt.format_messages(text=document[0].page_content),
                          callback=self.callback)
        refine_steps = [res]
        for doc in document[1:]:
            res = friday_chat(model=self.friday_model,
                              messages=refine_prompt.format_messages(text=doc.page_content,
                                                                     existing_answer=refine_steps[-1]),
                              callback=self.callback)
            refine_steps.append(res)
        answer = refine_steps[-1]
        self.result_item.reason = answer
        return answer

    def analysis_and_answer(self, existing_answer: str) -> str:
        prompt = ChatPromptTemplate(input_variables=['existing_answer'],
                                    messages=[SystemMessagePromptTemplate(
                                        prompt=self.system_prompt),
            HumanMessagePromptTemplate(
                                        prompt=self.prefix_prompt),
            AIMessagePromptTemplate(
                                        prompt=self.yes_prompt),
            HumanMessagePromptTemplate(
                                        prompt=self.ask_prompt)])
        res = friday_chat(self.friday_model,
                          prompt.format_messages(existing_answer=existing_answer),
                          callback=self.callback)
        answer_list = res.split('\n\n')
        for item in answer_list:
            message = [
                MetaMessage('user', existing_answer),
                MetaMessage('assistant', item)
            ]
            exp = create_experience(type=self.result_item.type,
                                    coe_id=self.result_item.coe_id,
                                    task_id=self.result_item.task_id,
                                    message_list=message)
            self.result_item.answer_message.append(Answer(exp_id=exp.id))
        return res


class COEFundAggregrateClassifyRunner(COEBaseRunner):
    valid_type_list = ['fund_aggr_classify']

    def __init__(self, result_item: COEResult, _id: str):
        super().__init__(result_item, _id)

    def init_prompt(self, type):
        self.ask_prompt = get_prompt(type, 'ask', prefix=f'{lion.app_name}.coe')
        model_name = lion.config[f'{lion.app_name}.coe.{type}.model_name']
        self.friday_model_fund = Friday(model=model_name, max_tokens=1024, direction='COE')
        self.cls_ans = []

    def pre_check(self) -> bool:
        '''返回 to_do_next ，是否需要进行LLM询问'''
        coe_id = self.result_item.coe_id
        coe_store, _ = search_coe(coe_id=coe_id)
        mole_first_level_tag = coe_store.fund_safety.mole_first_level_tag
        if mole_first_level_tag == '后台&系统通道':
            # 只有 后台&系统通道 会进行二级分类
            return True
        else:
            self.make_answer(mole_first_level_tag, mole_first_level_tag)
            return False

    def get_6to2not_data(self, coe_id):
        rows = get_6to2notto(coe_id=coe_id)
        text = []
        for row in rows:
            title = row[0]
            answer = row[1]
            reason = row[2]['text']
            text.append(f"是否违反{title}:{answer}。\n原因:{reason}")
        return '\n\n'.join(text)

    def load(self) -> List[Document]:
        coe_id = self.result_item.coe_id
        coe_store, _ = search_coe(coe_id=coe_id)
        self.coe_store = coe_store
        loader = COEFoundJudgementLoader(self.result_item.coe_id)
        return loader.load()

    def split(self, document: List[Document]) -> List[Document]:
        return document

    def make_history(self, role, content):
        self.result_item.message.append(
            MetaMessage(role=role, content=content))

    def ask_fund_security(self, document):
        '''在这里会进行一次 fund_judgement'''
        if '稳定性类' in self.cls_ans:
            return '稳定性类问题，资金安全不做工'
        question = get_chat_prompt('fund_judgement', 'question', prefix=f'{lion.app_name}.coe')
        content = ''.join([doc.page_content for doc in document])
        existing_answer = friday_chat(self.friday_model_fund, question.format_messages(
            text=content, title=self.result_item.brief), callback=self.callback)
        self.make_answer(question.format(text=content, title=self.result_item.brief), existing_answer)
        # 进行结果拆分
        pattern = re.compile(r'回答[:：]\s*([\u4e00-\u9fa5]+)')
        match = pattern.findall(existing_answer)
        if (len(match) > 0):
            answer = str(match[0])
        elif '是' in existing_answer.split('\n')[0]:
            answer = '是'
        elif '否' in existing_answer.split('\n')[0]:
            answer = '否'
        else:
            answer = existing_answer
        if answer == '是':
            self.cls_ans.append('资金安全类')
        self.result_item.reason = existing_answer
        return existing_answer

    def ask_wendingxing(self, coe_store: COEStoreageData):
        '''进行进一步的稳定性判断'''
        if coe_store.cause_analysis and coe_store.cause_analysis.analysis_result_id:
            cause = coe_store.cause_analysis
            chain_id = cause.analysis_result_id
            chains, _ids = batch_search_chain_by_id(chain_id_list=[chain_id])
            chain = chains[0]
            text = chain.reason
            if chain.reason == '信息太少，无法判断':
                text = chain.brief
            prompt = get_chat_prompt('fund_judgement', 'wendingxing', prefix=f'{lion.app_name}.coe')
            res = friday_chat(self.friday_model_fund, prompt.format_messages(
                text=text), callback=self.callback)
            self.make_answer(prompt.format(text=text), res)
            pattern = re.compile(r'回答[:：]\s*(.*)')
            ans = re.findall(pattern=pattern, string=res)
            if len(ans) > 0:
                ans = ans[0]
                if '是' in ans:
                    return True
        return False

    def summary_and_thought(self, document: List[Document]) -> str:
        to_test_tonotto = False
        self.result_item.reason = '具体信息查看下列分析结果'
        # 非技术故障
        if self.coe_store.category in ['非技术类事故', '故障演练'] or \
                '需求问题' in [self.coe_store.cause_analysis.rd_result, self.coe_store.cause_analysis.analysis_result]:
            self.make_history('user', f'故障类型:{self.coe_store.category}')
            self.make_history('assistant', '[非技术故障]\n非技术类事故和故障演练都属<非技术故障>')
            self.make_answer(f'故障类型:{self.coe_store.category}', '[非技术故障]\n非技术类事故和故障演练都属<非技术故障>')
            self.cls_ans.append('非技术故障')
        # 安全生产类
        if to_test_tonotto:
            '''暂时不做这一块判断了，以后可能会打开'''
            fields = ['to_test', 'to_claim', 'to_check', 'to_grey', 'to_inspect', 'to_rollback', 'not_to_delay',
                      'not_to_illagle_change_data']
            for field in fields:
                value = getattr(self.coe_store, field)
                if value:
                    if value.rd_result in ["违反", "无法确定", "涉及"]:
                        self.make_history('user', f'{field}:{value.rd_result}')
                        self.make_history('assistant', f'[安全生产类]\nRD 自认为违反了{field}')
                        self.make_answer(f'{field}:{value.rd_result}', f'[安全生产类]\nRD 自认为违反了{field}')
                        self.cls_ans.append('安全生产类')
                    elif value.analysis_result in ["违反", "无法确定"]:
                        self.make_history('user', f'要测试:{value.analysis_result}')
                        self.make_history('assistant', f'[安全生产类]\nLLM 认为违反了{field}')
                        self.make_answer(f'要测试:{value.analysis_result}', f'[安全生产类]\nLLM 认为违反了{field}')
                        self.cls_ans.append('安全生产类')
        # 业务逻辑类 vs 稳定性类
        valid_results = ['线上环境变更', '线上流量突增', '线上压测触发', '基础设施异动', '业务环境变化']
        if self.coe_store.trigger_method:
            trigger = self.coe_store.trigger_method.rd_result
            if trigger in valid_results:
                self.make_history('user', f'线上问题触发条件:{trigger}')
                self.make_history('assistant', f'[稳定性类]\n {valid_results}都是稳定性类')
                self.make_answer(f'线上问题触发条件:{trigger}', f'[稳定性类]\n {valid_results}都是稳定性类')
                self.cls_ans.append('稳定性类')
            elif self.ask_wendingxing(self.coe_store):
                self.make_answer('线上问题与机房、限流等相关，属于稳定性问题', '[稳定性类]\n 是稳定性类')
                self.cls_ans.append('稳定性类')
            elif trigger:
                self.make_history('user', f'线上问题触发条件:{trigger}')
                self.make_history('assistant', '[业务逻辑类]\n')
                self.make_answer(f'线上问题触发条件:{trigger}', '[业务逻辑类]\n')
                self.cls_ans.append('业务逻辑类')

        self.ask_fund_security(document)
        return self.result_item.reason

    def analysis_and_answer(self, existing_answer: str) -> str:
        self.cls_ans = list(set(self.cls_ans))
        message = [
            MetaMessage('user', existing_answer),
            MetaMessage('assistant', ', '.join(self.cls_ans))
        ]
        exp = create_experience(type=self.result_item.type,
                                coe_id=self.result_item.coe_id,
                                task_id=self.result_item.task_id,
                                message_list=message)
        self.result_item.answer_message.insert(0, Answer(exp_id=exp.id))
        return ', '.join(self.cls_ans)


if __name__ == '__main__':
    callback = LLMCallback2(COEResult(['1'], '1', '1', '1', '1', ''), '1')
    # llm = ChatOpenAI(model_name=GPT35NAME,
    #                  openai_api_base=OPENAI_API_BASE,
    #                  openai_api_key=OPENAI_API_KEY)
    glm = ChatGLM(temperature=0.01, verbose=True)
    lion.fetch_config()
    lion_prefix = f'{lion.app_name}.coe'
    type = 'fund_judgement'
    question = get_prompt(type, 'question', prefix=lion_prefix)
    # chain = LLMChain(verbose=True, prompt=question, llm=llm)
    # chain.predict(callbacks=[callback], text='')
    glm(question.format(text=''), callbacks=[callback])
