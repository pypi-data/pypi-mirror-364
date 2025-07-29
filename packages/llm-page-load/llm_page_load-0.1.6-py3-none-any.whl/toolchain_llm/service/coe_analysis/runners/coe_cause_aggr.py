from typing import Dict, List
import uuid
from service.coe_analysis.coe_chain_service import (bulk_create_chain_by_object)
from service.coe_analysis.coe_experience_service import (batch_find_experience, bulk_create_exp_by_object,
                                                         create_experience, find_experience)
from service.coe_analysis.data_structure import Answer, COEResult, Experience, MetaMessage, COEStoreageData
from service.coe_analysis.runners.coe_cause_search import CauseTreeSearchRunner
from service.coe_analysis.runners.loaders import Document
from service.coe_analysis.runners.base import COEBaseRunner
from service.coe_analysis.result_analysis import get_result_to_show
from service.coe_analysis.runners.retriver import LLMCallback2, get_prompt
from service.coe_analysis.search_coe_result_item import batch_search_chain_by_id, search_all_chain
from service.lang_chain_utils.helper import FridayChain
from service.lang_chain_utils.lion_client import client as lion
from service.coe_analysis.coe_store_service import batch_search_coe_storage, list_coe
import sklearn.cluster
from service.coe_analysis.config_reader import OPENAI_API_BASE, OPENAI_API_KEY, DEFAULT_AGGR_COEID_PLACEHOLDER
from langchain.chat_models import ChatOpenAI
import numpy as np
from token_count.tokenizer import count_token
import re
import time
from service.lang_chain_utils.embedding import m3embed
from sklearn import preprocessing
from utils import GPT35NAME, get_now_str, logger
from service.coe_analysis.llm_sdk_importer import es_util, COE_ANALYSIS_DETAIL
from service.coe_analysis.coe_task_service import search_task, update_task


class SetList:
    def __init__(self):
        self.data = set()

    def add(self, d):
        self.data.add(d)

    def __dict__(self):
        return list(self.data)


class COECauseAggrBaseRunner(COEBaseRunner):
    def __init__(self, result_item: COEResult, _id: str):
        super().__init__(result_item, _id)
        lion.fetch_config()
        self.llm.model_name = lion.config[f'{lion.app_name}.coe.cause_aggr.model_name']
        self.llm.openai_api_base = lion.config[f'{lion.app_name}.coe.cause_aggr.api_base']

    def pre_check(self) -> bool:
        return True

    def split(self, document: List[Document]) -> List[Document]:
        return document

    def done(self):
        self.result_item.is_done = True
        self.result_item.edit_time = get_now_str()
        if (self.result_item.reason and len(self.result_item.reason) != 0):
            self.result_item.search_vector = m3embed.get_embedding(
                self.result_item.reason)
        self.callback.save_result_to_es()

    def save_to_es(self, q, a):
        message = [
            MetaMessage('user', q),
            MetaMessage('assistant', a)
        ]
        exp = create_experience(type=self.result_item.type,
                                coe_id=None,
                                task_id=self.result_item.task_id,
                                message_list=message)
        self.result_item.answer_message.append(Answer(exp_id=exp.id))

    def analysis_and_answer(self, existing_answer: str) -> str:
        return existing_answer


class COECauseAggrByExperienceGetter():
    '''通过RD写的经验知识当作聚类'''

    def __init__(self) -> None:
        self.type = 'aggr_by_experience'
        self.coe_list = []
        pass

    def init(self, create_begin, create_end, cause, size=500, k=10,
             levels=None, orgs=None, is_exclude_light_template=False) -> None:
        self.create_begin = create_begin
        self.create_end = create_end
        self.cause = cause
        self.is_exclude_light_template = is_exclude_light_template
        self.orgs = orgs
        self.levels = levels
        self.size = size
        self.k = k

    def load(self) -> Dict[int, List[COEStoreageData]]:
        coe_list, _ = list_coe(self.create_begin, self.create_end, self.size, 0,
                               is_exclude_light_template=self.is_exclude_light_template,
                               orgs=self.orgs, levels=self.levels,
                               other_must_inner=[{"term": {"cause_analysis.rd_result.keyword": self.cause}},
                                                 {"exists": {"field": "experience_embedding"}}])
        self.coe_list = coe_list
        data = np.array([coe.experience_embedding for coe in coe_list])
        km_cluster = sklearn.cluster.KMeans(
            n_clusters=self.k, init='k-means++')
        result = km_cluster.fit_predict(data)
        clusted_coe_dict: Dict[int, List[COEStoreageData]] = {}
        for coe, cluster in zip(coe_list, result):
            c = str(cluster)
            if c not in clusted_coe_dict:
                clusted_coe_dict[c] = []
            clusted_coe_dict[c].append(coe)
        return clusted_coe_dict


class COECauseAggrBySecondClassifyGetter():
    '''通过“二级分类”的输出项做聚类'''

    def __init__(self) -> None:
        self.type = 'aggr_by_second_classify'
        self.coe_list = []
        pass

    def init(self, create_begin, create_end, cause, size=500, k=10,
             levels=None, orgs=None, is_exclude_light_template=False) -> None:
        self.create_begin = create_begin
        self.create_end = create_end
        self.cause = cause
        self.is_exclude_light_template = is_exclude_light_template
        self.orgs = orgs
        self.levels = levels
        self.size = size
        self.k = k

    def load(self) -> Dict[int, List[COEStoreageData]]:
        coe_list, _ = list_coe(self.create_begin, self.create_end, self.size, 0,
                               is_exclude_light_template=self.is_exclude_light_template,
                               orgs=self.orgs, levels=self.levels,
                               other_must_inner=[{"term": {"cause_analysis.analysis_result.keyword": self.cause}}])
        self.coe_list = coe_list

        def find_coe_by_id(coe_id):
            for coe in coe_list:
                if str(coe.coe_id) == str(coe_id):
                    return coe
        emb_data = []
        chain_ids = []
        emb_content = []
        for i in coe_list:
            if i.cause_analysis and i.cause_analysis.analysis_result_id:
                chain_ids.append(i.cause_analysis.analysis_result_id)
        chains, _ = batch_search_chain_by_id(chain_id_list=chain_ids)
        for result_item in chains:
            if len(result_item.answer_message) == 0 or not result_item.is_done:
                continue
            first_saved_exp_id = result_item.answer_message[0].exp_id
            exp, _ = find_experience(first_saved_exp_id)
            if self.cause:
                result_to_show = get_result_to_show(
                    result_item=result_item, first_saved_exp=exp)
                if result_to_show != self.cause:
                    continue
            second_class = self.get_second_classify(exp.data[-1].content)
            # second_class_embedding = m3embed.embed_query(second_class)
            # emb_data.append(second_class_embedding)
            coe = find_coe_by_id(result_item.coe_id)
            emb_data.append(coe.cause_embedding)
            emb_content.append(
                {"second_class": second_class, "brief": result_item.brief})
        data = np.array(emb_data)
        data = preprocessing.normalize(data)  # 归一化后的欧氏距离就相当于余弦距离
        # km_cluster = sklearn.cluster.KMeans(n_clusters=self.k, init='k-means++')
        km_cluster = sklearn.cluster.AgglomerativeClustering(n_clusters=self.k)
        result = km_cluster.fit_predict(data)
        clusted_coe_dict: Dict[int, List[COEStoreageData]] = {}
        for coe, cluster in zip(emb_content, result):
            c = str(cluster)
            if c not in clusted_coe_dict:
                clusted_coe_dict[c] = []
            clusted_coe_dict[c].append(coe)
        return clusted_coe_dict

    def get_second_classify(self, text: str):
        pattern = r"分类思路和原因[:：]\s*(.+)"
        result = re.search(pattern, text)
        if result:
            category = result.group(1)
            return category
        else:
            return text


class COECauseAggrByKeywordsGetter():
    '''使用LLM自动生成的keywords作为分类依据'''

    def __init__(self) -> None:
        self.type = 'aggr_by_kw'
        self.coe_list = []

    def init(self, create_begin, create_end, cause=None, size=500, k=10,
             levels=None, orgs=None, is_exclude_light_template=False) -> None:
        self.create_begin = create_begin
        self.create_end = create_end
        self.cause = cause
        self.is_exclude_light_template = is_exclude_light_template
        self.orgs = orgs
        self.levels = levels
        self.size = size
        self.k = k

    def key_words_aggr_prepare(self):
        other_must_inner = []
        logger.info(
            f'key_words_aggr_prepare : begin={self.create_begin}  enc={self.create_end}  cause={self.cause}')
        if self.cause:
            other_must_inner = [
                {"term": {"cause_analysis.analysis_result.keyword": self.cause}}]
        coe_list, _ = list_coe(self.create_begin, self.create_end, self.size, 0,
                               is_exclude_light_template=self.is_exclude_light_template,
                               orgs=self.orgs, levels=self.levels,
                               other_must_inner=other_must_inner)
        self.coe_list = coe_list
        chain_ids = []
        for i in coe_list:
            if i.cause_analysis and i.cause_analysis.analysis_result_id:
                chain_ids.append(i.cause_analysis.analysis_result_id)
        chains, _ = batch_search_chain_by_id(chain_id_list=chain_ids)
        logger.info(f'key_words_aggr_prepare find {len(chains)} chains')
        data = []
        excludes = ['问题', '逻辑', '错误']
        for chain in chains:
            first_saved_exp_id = chain.answer_message[0].exp_id
            exp, _ = find_experience(first_saved_exp_id)
            text = exp.data[-1].content
            pattern = r"关键词[:：]\s*(.+)"
            result = re.search(pattern, text)
            category = result.group(1)
            category = re.split(r',\s*|，\s*|、\s*', category)
            for key in category:
                key_exclude = key
                for ex in excludes:
                    key_exclude = key_exclude.replace(ex, '')
                logger.info(f'进行embedding : {key_exclude}')
                data.append({
                    'keyword': key_exclude,
                    'chain_id': chain.id
                })
        sentences = [i['keyword'] for i in data]
        embs = m3embed.embed_documents(sentences)
        for d, e in zip(data, embs):
            d['embedding'] = e
        logger.info('key_words_aggr_prepare finish')
        return data

    def load(self):
        cause_aggr_keywords = self.key_words_aggr_prepare()
        data = np.array([d['embedding'] for d in cause_aggr_keywords])
        data = preprocessing.normalize(data)
        # dis = pairwise_distances(data)
        # dis_l = []
        # for i in range(data.shape[0]):
        #     for j in range(i+1,data.shape[0]):
        #         dis_l.append(dis[i][j])
        # dis_l = np.array(dis_l)
        # import matplotlib.pyplot as plt
        # plt.hist(dis_l)
        # plt.show()
        # cluster = sklearn.cluster.KMeans(n_clusters=50, init='k-means++')
        logger.info('aggr method is AgglomerativeClustering')
        if len(data) < 30:
            raise Exception('数据太少')
        if self.k is None or self.k == 0:
            self.k = len(data)//4
        cluster = sklearn.cluster.AgglomerativeClustering(
            n_clusters=self.k, compute_distances=True)
        result = cluster.fit_predict(data)
        clusted_preview: Dict[str, List] = {}
        for d, cluster in zip(cause_aggr_keywords, result):
            c = str(cluster)
            if c not in clusted_preview:
                clusted_preview[c] = []
            clusted_preview[c].append({"keyword": d['keyword']})
        return clusted_preview


class COECauseAggrSimpleGetter(COECauseAggrByKeywordsGetter):
    def __init__(self) -> None:
        self.type = 'aggr_simple'
        self.coe_list = []
        self.first_cls = ['需求问题', '技术设计', '代码逻辑', '配置问题', '数据存储', '服务上下游协同问题', '上线流程', '线上环境操作不当',
                          '性能问题', '基础架构', '基础设施', '外部依赖', '第三方问题', '安全问题']

    def find_cls(self, text: str):
        for c in self.first_cls:
            if c in text:
                return True
        return False

    def text_prepate(self, text: str, title: str):
        lines = text.split('\n')[1:]  # 第一行是一级分类
        data = [f'线上问题: {title}']
        for line in lines:
            title = line.split(':')[0]
            other = line.split(':')[1:]
            other = ''.join(other)
            sentences = other.split('。')
            sentences = [s for s in sentences if not self.find_cls(s)]
            data.append(title + ":" + '。'.join(sentences))
        return '\n'.join(data)

    def load(self):
        other_must_inner = []
        logger.info(
            f'key_words_aggr_prepare : begin={self.create_begin}  enc={self.create_end}  cause={self.cause}')
        if self.cause:
            other_must_inner = [
                {"term": {"cause_analysis.rd_result.keyword": self.cause}}]
        coe_list, _ = list_coe(self.create_begin, self.create_end, self.size, 0,
                               is_exclude_light_template=self.is_exclude_light_template,
                               orgs=self.orgs, levels=self.levels,
                               other_must_inner=other_must_inner)
        self.coe_list = coe_list
        chain_ids = []
        for i in coe_list:
            if i.cause_analysis and i.cause_analysis.analysis_result:
                chain_ids.append(i.cause_analysis.analysis_result_id)
        chains, _ = batch_search_chain_by_id(chain_id_list=chain_ids)
        logger.info(f'key_words_aggr_prepare find {len(chains)} chains')
        data = []
        for chain in chains:
            first_saved_exp_id = chain.answer_message[0].exp_id
            exp, _ = find_experience(first_saved_exp_id)
            text = exp.data[-1].content
            title = chain.brief
            data.append({"text": self.text_prepate(text, title)})
        return {DEFAULT_AGGR_COEID_PLACEHOLDER: data}


class COECauseAggrByExperienceRunner(COECauseAggrBaseRunner):
    valid_types = ['aggr_by_experience']

    def __init__(self, result_item: COEResult, _id: str, coe_list: List[COEStoreageData], cause: str):
        super().__init__(result_item, _id)
        lion.fetch_config()
        lion_prefix = f'{lion.app_name}.coe'
        self.type = 'aggr_by_experience'
        self.question = get_prompt(self.type, 'question', prefix=lion_prefix)
        self.ask = get_prompt(self.type, 'ask', prefix=lion_prefix)
        self.callback = LLMCallback2(result_item=result_item, _id=_id)
        self.coe_list = coe_list
        self.cause = cause

    def load(self):
        min_token = 5500
        documents = []
        txt = []
        current_token = 0
        for coe in self.coe_list:
            tmp_txt = f'---- [标题] {coe.brief} ----\n{coe.experience}'
            tmp_token = count_token(tmp_txt)
            if current_token + tmp_token > min_token:
                documents.append(Document(page_content='\n\n'.join(txt)))
                txt = [tmp_txt]
                current_token = tmp_token
            else:
                txt.append(tmp_txt)
                current_token += tmp_token
        documents.append(Document(page_content='\n\n'.join(txt)))
        return documents

    def summary_and_thought(self, document: List[Document]) -> str:
        answers = []
        chain = FridayChain(verbose=True, prompt=self.question, llm=self.friday_model)
        for doc in document:
            ans = chain.predict(
                callbacks=[self.callback], content=doc.page_content, cause=self.cause)
            self.save_to_es(doc.page_content, ans)
            self.result_item.reason = doc.page_content
            answers.append(ans)
        answer = '\n\n'.join(answers)
        return answer


class COECauseAggrBySecondClassifyRunner(COECauseAggrBaseRunner):
    valid_types = ['aggr_by_second_classify_from_task']

    def __init__(self, result_item: COEResult, _id: str, coe_list: List[Dict], cause: str):
        super().__init__(result_item, _id)
        lion.fetch_config()
        lion_prefix = f'{lion.app_name}.coe'
        self.type = 'aggr_by_second_classify_from_task'
        self.question = get_prompt(self.type, 'question', prefix=lion_prefix)
        self.callback = LLMCallback2(result_item=result_item, _id=_id)
        self.coe_list = coe_list
        self.cause = cause
        if cause == '代码逻辑':
            self.cause = '代码逻辑错误'

    def load(self):
        min_token = 7500
        documents = []
        txt = []
        current_token = 0
        for coe in self.coe_list:
            brief = coe['brief']
            second_class = coe['second_class']
            tmp_txt = f'---- [标题] {brief} ----\n{second_class}'
            tmp_token = count_token(tmp_txt)
            if current_token + tmp_token > min_token:
                documents.append(Document(page_content='\n\n'.join(txt)))
                txt = [tmp_txt]
                current_token = tmp_token
            else:
                txt.append(tmp_txt)
                current_token += tmp_token
        documents.append(Document(page_content='\n\n'.join(txt)))
        return documents

    def summary_and_thought(self, document: List[Document]) -> str:
        answers = []
        chain = FridayChain(verbose=True, prompt=self.question, llm=self.friday_model)
        for doc in document:
            ans = chain.predict(
                callbacks=[self.callback], content=doc.page_content, cause=self.cause)
            self.save_to_es(doc.page_content, ans)
            self.result_item.reason = doc.page_content
            answers.append(ans)
        answer = '\n\n'.join(answers)
        return answer


class COECauseAggrByKeywordsClassifyRunner(COECauseAggrBaseRunner):
    valid_types = ['aggr_by_kw']

    def __init__(self, result_item: COEResult, _id: str, data_list: List[Dict], cause: str):
        super().__init__(result_item, _id)
        lion.fetch_config()
        lion_prefix = f'{lion.app_name}.coe'
        self.type = 'aggr_by_kw'
        self.question = get_prompt(self.type, 'question', prefix=lion_prefix)
        self.callback = LLMCallback2(result_item=result_item, _id=_id)
        self.data_list = data_list
        self.cause = cause
        if cause == '代码逻辑':
            self.cause = '代码逻辑错误'

    def load(self):
        documents = []
        txt = []
        token = 0
        for data in self.data_list:
            keyword = data['keyword']
            txt.append(keyword)
            token += count_token(txt)
            if token > 10000:
                token = 0
                documents.append(Document(page_content=','.join(txt)))
                txt = []
        if len(txt) != 0:
            documents.append(Document(page_content=','.join(txt)))
        return documents

    def summary_and_thought(self, document: List[Document]) -> str:
        answers = []
        chain = FridayChain(verbose=True, prompt=self.question, llm=self.friday_model)
        for doc in document:
            ans = chain.predict(
                callbacks=[self.callback], content=doc.page_content)
            self.save_to_es(doc.page_content, ans)
            self.result_item.reason = doc.page_content
            answers.append(ans)
        answer = '\n\n'.join(answers)
        return answer


class COECauseAggrSimpleRunner(COECauseAggrByKeywordsClassifyRunner):
    def load(self):
        documents = []
        txt = []
        token = 0
        for data in self.data_list:
            text = data['text']
            txt.append(text)
            token += count_token(text)
            if token > 100000:
                token = 0
                documents.append(Document(page_content='\n\n'.join(txt)))
                txt = []
        if len(txt) != 0:
            documents.append(Document(page_content='\n\n'.join(txt)))
        return documents

    def summary_and_thought(self, document: List[Document]) -> str:
        answers = []
        lion_prefix = f'{lion.app_name}.coe'
        question = get_prompt('aggr_by_kw', 'aggr', prefix=lion_prefix)
        chain = FridayChain(verbose=True, prompt=question, llm=self.friday_model)
        for doc in document:
            ans = chain.predict(
                callbacks=[self.callback], content=doc.page_content)
            self.save_to_es(doc.page_content, ans)
            self.result_item.reason = doc.page_content
            answers.append(ans)
        answer = '\n'.join(answers)
        return answer


class COECauseAggrSimpleDoneRunner(COECauseAggrBaseRunner):
    def __init__(self, task_id) -> None:
        self.task_id = task_id
        self.task, self._id_task = search_task(task_id)
        self.coe_ids = [coe.coe_id for coe in self.task.choosed_coe_list]
        self.first_cls = ['需求问题', '技术设计', '代码逻辑', '配置问题', '数据存储', '服务上下游协同问题', '上线流程', '线上环境操作不当',
                          '性能问题', '基础架构', '基础设施', '外部依赖', '第三方问题', '安全问题']
        self.stop_words = ['错误', '不足']

    def find_cls(self, text: str):
        for c in self.first_cls:
            if c in text:
                return True
        return False

    def replace_stop_words(self, text: str):
        for stop_word in self.stop_words:
            text = text.replace(stop_word, '')
        return text

    def text_prepate(self, text: str, title: str):
        lines = text.split('\n')[1:]  # 第一行是一级分类
        data = [title]
        for line in lines:
            title = line.split(':')[0]
            other = line.split(':')[1:]
            other = ''.join(other)
            if '问题出现的阶段' in title:
                continue
            elif '关键词' in title and not self.find_cls(other):
                # sentences = re.split('，|,|、', other)
                sentences = [self.replace_stop_words(other)]
                continue
            elif '二级分类' in title and not self.find_cls(other):
                sentences = [self.replace_stop_words(other)]
                continue
            else:
                sentences = other.split('。')
                sentences = [self.replace_stop_words(s) for s in sentences if not self.find_cls(s)]
            sentences = [i for i in sentences if len(i) > 2]  # 至少2个字符
            data.extend(sentences)
        return data

    def save_embeddings_as_chain(self):
        '''将所有的coe的描述都存成chain'''
        # 查找所有结果
        coes, _ids = batch_search_coe_storage(coe_ids=self.coe_ids, size=1000)
        chain_ids = []
        for i in coes:
            if i.cause_analysis and i.cause_analysis.analysis_result_id:
                chain_ids.append(i.cause_analysis.analysis_result_id)
        chains, _ = batch_search_chain_by_id(chain_id_list=chain_ids)
        chain_dict = {i.id: i for i in chains}
        data = []
        reference = []
        _, exp_dict = batch_find_experience([i.answer_message[0].exp_id for i in chains if len(i.answer_message) > 0
                                            and i.answer_message[0].exp_id is not None])
        for chain in chains:
            first_saved_exp_id = chain.answer_message[0].exp_id
            if first_saved_exp_id not in exp_dict:
                exp_dict[first_saved_exp_id], _ = find_experience(first_saved_exp_id)
            exp = exp_dict[first_saved_exp_id]
            text = exp.data[-1].content
            title = chain.brief
            preped = self.text_prepate(text, title)
            data.extend(preped)
            reference.extend([chain.id]*len(preped))
        # 进行embedding
        prep_embed = []
        for i in range(0, len(data), 128):
            batch = data[i:i+128]
            prep_embed.extend(m3embed.embed_documents(batch))
        # 将结果保存为chain
        items = []
        item_dict = {}
        emb_exps = []
        for chain in chains:
            item = COEResult(task_id=[self.task_id], coe_id=chain.coe_id, brief=chain.brief,
                             type='embedding_storage', id=str(uuid.uuid1().int), occur_time=get_now_str(),
                             reason=exp.data[-1].content)
            items.append(item)
            item_dict[chain.id] = item
        logger.info(f'新建的 chain 数量 {len(items)}')
        for chain_id, query, embed in zip(reference, data, prep_embed):
            chain = chain_dict[chain_id]
            first_saved_exp_id = chain.answer_message[0].exp_id
            exp = exp_dict[first_saved_exp_id]
            item: COEResult = item_dict[chain_id]
            embed_exp = Experience(
                task_id=[self.task_id],
                coe_id=chain.coe_id,
                type='embedding_storage',
                data=[MetaMessage(role='user', content=query)],
                id=str(uuid.uuid1().int),
                search_text=query,
                search_embedding=embed
            )
            item.answer_message.append(Answer(exp_id=embed_exp.id))
            emb_exps.append(embed_exp)
        logger.info(f'新建的 exp 数量 {len(emb_exps)}')
        bulk_create_chain_by_object(items)
        bulk_create_exp_by_object(emb_exps)
        logger.info('COECauseAggrSimpleDoneRunner 完毕')

    def aggr_to_one(self):
        self.save_embeddings_as_chain()
        if 'embedding_storage' not in self.task.sub_task_type_list:
            self.task.sub_task_type_list.append('embedding_storage')
            update_task(self.task, self._id_task)
        if 'aggr_recall_placeholder' not in self.task.sub_task_type_list:
            self.task.sub_task_type_list.append('aggr_recall_placeholder')
            update_task(self.task, self._id_task)
        search_runner = CauseTreeSearchRunner(task_id=self.task_id)
        search_runner.tree_search()

    def done(self):
        pass


class COECauseAggrByKeywordsDoneRunner(COECauseAggrBaseRunner):
    def __init__(self, task_id) -> None:
        self.task_id = task_id
        self.type = 'aggr_by_kw'
        id = str(uuid.uuid1().int)
        brief = ''
        level = ''
        occur_time = get_now_str()
        edit_time = get_now_str()
        new_chain = COEResult(task_id=[str(self.task_id)], edit_time=edit_time, coe_id='-1', type=self.type+'_to_one',
                              id=id, brief=brief, occur_time=occur_time, level=level)
        index_json = new_chain.to_json_dict()
        es_util.index(index=COE_ANALYSIS_DETAIL, body=index_json, id=id)
        task, _id = search_task(task_id=self.task_id)
        self.task = task
        if self.type+'_to_one' not in task.sub_task_type_list:
            task.sub_task_type_list.append(self.type+'_to_one')
            update_task(task=task, _id=_id)
        time.sleep(1)
        self.result_item = new_chain
        self.llm = ChatOpenAI(model_name=GPT35NAME,
                              openai_api_base=OPENAI_API_BASE,
                              openai_api_key=OPENAI_API_KEY,
                              request_timeout=60,
                              max_retries=3)
        lion_prefix = f'{lion.app_name}.coe'
        self.aggr = get_prompt(self.type, 'aggr', prefix=lion_prefix)
        self.callback = LLMCallback2(result_item=new_chain, _id=id)

    def aggr_to_one(self):
        docs = self.get_answers()
        for doc in docs:
            content = doc.page_content
            chain = FridayChain(verbose=True, prompt=self.aggr, llm=self.friday_model)
            ans = chain.predict(callbacks=[self.callback], content=content)
            self.save_to_es(content, ans)
        self.result_item.reason = '--'

    def get_answers(self) -> List[Document]:
        result_list, _ = search_all_chain(self.task_id, from_=0, size=1000)
        _, exp_dict = batch_find_experience(
            [i.answer_message[0].exp_id for i in result_list if len(i.answer_message) > 0])
        answer = []
        token = 0
        docs = []
        for item in result_list:
            if item.type != self.type:
                continue
            if (not item.is_done or len(item.answer_message) == 0):
                continue
            else:
                first_saved_exp_id = item.answer_message[0].exp_id
                if first_saved_exp_id not in exp_dict:
                    exp_dict[first_saved_exp_id], _ = find_experience(
                        first_saved_exp_id)
                result_to_show = get_result_to_show(
                    result_item=item, first_saved_exp=exp_dict.get(first_saved_exp_id))

            # result_to_show += f'\n具体内容:{item.reason}'
            token += count_token(result_to_show)
            answer.append(result_to_show)
            if token > 10000:
                token = 0
                docs.append(Document(page_content='\n----\n'.join(answer)))
                answer = []
        if len(answer) > 0:
            docs.append(Document(page_content='\n----\n'.join(answer)))
        return docs


def get_aggr_getter_by_type(type):
    if type == 'aggr_by_experience':
        return COECauseAggrByExperienceGetter()
    elif type == 'aggr_by_second_classify':
        return COECauseAggrBySecondClassifyGetter()
    elif type == 'aggr_by_kw':
        return COECauseAggrByKeywordsGetter()
    elif type == 'aggr_simple':
        return COECauseAggrSimpleGetter()
    else:
        raise NotImplementedError(f'没有实现 {type}')


def aggr_get_runner_by_type(result_item, _id, type, data_list, cause):
    if type == 'aggr_by_experience':
        return COECauseAggrByExperienceRunner(result_item=result_item, _id=_id, coe_list=data_list, cause=cause)
    elif type == 'aggr_by_second_classify_from_task' or type == 'aggr_by_second_classify':
        return COECauseAggrBySecondClassifyRunner(result_item=result_item,
                                                  _id=_id, coe_list=data_list, cause=cause)
    elif type == 'aggr_by_kw':
        return COECauseAggrByKeywordsClassifyRunner(result_item=result_item, _id=_id, data_list=data_list, cause=cause)
    elif type == 'aggr_simple':
        return COECauseAggrSimpleRunner(result_item=result_item, _id=_id, data_list=data_list, cause=cause)
    else:
        raise NotImplementedError(f'没有实现 {type}')


def aggr_get_done_runner(type, task_id):
    if type == 'aggr_by_kw':
        return COECauseAggrByKeywordsDoneRunner(task_id=task_id)
    elif type == 'aggr_simple':
        return COECauseAggrSimpleDoneRunner(task_id=task_id)
    else:
        return None
