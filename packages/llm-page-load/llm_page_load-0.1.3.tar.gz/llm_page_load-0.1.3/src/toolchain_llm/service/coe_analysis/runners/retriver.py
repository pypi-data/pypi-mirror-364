# -*- coding: utf-8 -*-
from typing import Any, Dict, List, Optional
from uuid import UUID
from langchain.callbacks.base import BaseCallbackHandler
from langchain.schema import LLMResult
from service.coe_analysis.data_structure import COEResult, MetaMessage, SimiliarCase
from utils import logger
import re
from token_count.tokenizer import count_token
from service.coe_analysis.data_structure import Experience, COECrawlerData
from langchain.prompts import PromptTemplate, FewShotPromptTemplate, ChatPromptTemplate, HumanMessagePromptTemplate
from langchain.schema import BaseMessage, BaseRetriever, Document
from langchain.prompts.example_selector.base import BaseExampleSelector
from langchain.prompts.base import DEFAULT_FORMATTER_MAPPING
from langchain.schema import HumanMessage, SystemMessage
from service.coe_analysis.llm_sdk_importer import es_util
from service.lang_chain_utils.lion_client import client as lion
from service.lang_chain_utils.embedding import embed
from service.coe_analysis.coe_thread_executor import coe_es_writer
import yaml

lion_prefix = f'{lion.app_name}.llm.coe.prompt_template'
# lion_prefix = f'{lion.app_name}.coe.test'

def get_chat_prompt(type, template, prefix=lion_prefix):
    pt = get_prompt(type, template, prefix)
    return ChatPromptTemplate(messages=[
        HumanMessagePromptTemplate(prompt=pt)
    ], input_variables=pt.input_variables)


def get_prompt(type, template, prefix=lion_prefix):
    '''lion获取prompt，包装为PromptTemplate'''

    type_6to2notto = ['to_test','to_claim','to_grey','to_inspect','to_rollback','to_check','not_to_delay','not_to_illagle_change_data']
    pattern = r'\{([a-zA-Z_]+)\}'
    path1 = ""
    path2 = ""
    filename = 'service/coe_analysis/prompt/' + type + '.yml'
    if type in type_6to2notto and template in ['ask_prompt', 'question_prompt', 'refine_prompt']:
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                config = yaml.safe_load(file)
                print("Config loaded successfully:", config)
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
        text = config[template]
    else:
        if f'{prefix}.{type}.{template}' in lion.config:
            text = lion.config[f'{prefix}.{type}.{template}']
        elif f'{prefix}.{template}' in lion.config:
            text = lion.config[f'{prefix}.{template}']
        else:
            path1 = f'{prefix}.{type}.{template}'
            path2 = f'{prefix}.{template}'
            raise Exception(f'没有 path1={path1}\n没有 path2={path2}')
    variables = re.findall(pattern, text)
    return PromptTemplate(template=text, input_variables=variables)


class FewShotSystem(FewShotPromptTemplate):
    '''自己定义的 few shot 可以反馈经验知识'''

    def get_cot_cache(self):
        return self.example_selector.cache

    def format(self, **kwargs: Any) -> str:
        kwargs = self._merge_partial_and_user_variables(**kwargs)
        # Get the examples to use.
        query = kwargs[self.input_variables[0]]
        examples = self._get_examples(query=query)
        examples = [
            {k: e[k] for k in self.example_prompt.input_variables}
            for e in examples
        ]
        # Format the examples.
        example_strings = [
            self.example_prompt.format(**example) for example in examples
        ]
        # Create the overall template.
        pieces = [self.prefix, *example_strings, self.suffix]
        template = self.example_separator.join(
            [piece for piece in pieces if piece])

        # Format the template with the input variables.
        return DEFAULT_FORMATTER_MAPPING[self.template_format](template)


def get_fewshoot(type, template, k=3, query_variable='query', dispatch_lion_by_type=False):
    '''封装fewshot，需要拆分lion的模板'''
    pattern = r'\{([a-zA-Z_]+)\}'
    text = lion.config[f'{lion_prefix}.{template}']
    if dispatch_lion_by_type:
        text = lion.config[f'{lion_prefix}.{type}.{template}']
    variables = re.findall(pattern, text)
    text = text.split('(prefix&suffix)')
    prefix = text[0]
    example = text[1]
    suffix = text[2]
    variables = re.findall(pattern, example)
    retriver = COEChainRetriver(type, var_names=variables, k=k)
    example_prompt = PromptTemplate(
        input_variables=variables, template=example)
    return FewShotSystem(input_variables=[query_variable], example_selector=retriver,
                         prefix=prefix, suffix=suffix,
                         example_prompt=example_prompt,
                         validate_template=False, example_separator='\n')


class LLMCallback2(BaseCallbackHandler):
    '''每次start和end，都会涉及到结果保存的操作，end的时候会持久化存储'''

    def __init__(self, result_item: COEResult, _id: str):
        self.result_item = result_item
        self.client = es_util.client
        self.headers = es_util.headers
        self._id = _id
        self.index = 'coe_analysis_detail'

    def save_result_to_es(self):
        body = {
            "doc": self.result_item.to_json_dict()
        }
        self.client.update(self.index, id=self._id,
                           body=body, headers=self.headers)

    def on_chat_model_start(self, serialized: Dict[str, Any],
                            messages: List[List[BaseMessage]], *,
                            run_id: UUID, parent_run_id: UUID = None,
                            **kwargs: Any) -> Any:
        # 对于 chatOpenAI 可以用
        content = messages[0][0].content
        for msg in messages[0]:
            if isinstance(msg, HumanMessage):
                content = msg.content
                logger.info(f'[Human]\n{content}')
            elif isinstance(msg, SystemMessage):
                logger.info(f'[System]\n{msg.content}')
        self.result_item.message.append(
            MetaMessage(role='user', content=content))

    def on_llm_start(
        self,
        serialized: Dict[str, Any],
        prompts: List[str],
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any,
    ) -> None:
        # 对于glm可用，不会干扰llm
        content = prompts[-1]
        self.result_item.message.append(
            MetaMessage(role='user', content=content))

    def on_llm_end(self, response: LLMResult, *, run_id: UUID,
                   parent_run_id: UUID = None, **kwargs: Any) -> Any:
        response_text = response.generations[0][0].text
        logger.info(f'[AI]\n{response_text}')
        self.result_item.message.append(MetaMessage(
            role='assistant', content=response_text))
        coe_es_writer.submit(self.save_result_to_es)


class LLMCallback(BaseCallbackHandler):
    '''每次start和end，都会涉及到结果保存的操作，end的时候会持久化存储'''

    def __init__(self, result_item: COEResult, _id: str):
        self.result_item = result_item
        self.client = es_util.client
        self.headers = es_util.headers
        self._id = _id
        self.index = 'coe_analysis_detail'

    def save_result_to_es(self):
        body = {
            "doc": self.result_item.to_json_dict()
        }
        self.client.update(self.index, id=self._id,
                           body=body, headers=self.headers)

    def on_chat_model_start(self, serialized: Dict[str, Any],
                            messages: List[List[BaseMessage]], *,
                            run_id: UUID, parent_run_id: UUID = None,
                            **kwargs: Any) -> Any:
        content = messages[0][0].content
        for msg in messages[0]:
            if isinstance(msg, HumanMessage):
                content = msg.content
                logger.info(f'[Human]\n{content}')
            elif isinstance(msg, SystemMessage):
                logger.info(f'[System]\n{msg.content}')
        self.result_item.message.append(
            MetaMessage(role='user', content=content))

    def on_llm_end(self, response: LLMResult, *, run_id: UUID,
                   parent_run_id: UUID = None, **kwargs: Any) -> Any:
        response_text = response.generations[0][0].text
        logger.info(f'[AI]\n{response_text}')
        self.result_item.message.append(MetaMessage(
            role='assistant', content=response_text))
        coe_es_writer.submit(self.save_result_to_es)


class COETopicRetriver:
    def __init__(self, task_id):
        self.index_name = 'coe_analysis_detail'
        self.client = es_util.client
        self.task_id = task_id
        self.type = 'cause'
        self.vector_field = 'search_vector'
        self.k = 5

    def retrive(self, query: str) -> List[COEResult]:
        threshold = float(lion.config[f'{lion.app_name}.cot_threshold'])
        query_vector = embed.get_embedding(query)
        body = {
            "script_score": {
                "query": {"bool": {"must": [
                    {"term": {"task_id": self.task_id}},
                    {'term': {'type': self.type}}
                ]}},
                "script": {
                    "source": "cosineSimilarity(params.query_vector," +
                    f" '{self.vector_field}') + 1.0",
                    "params": {"query_vector": query_vector},
                }
            }
        }
        query = {'query': body, 'size': self.k}
        response = self.client.search(
            body=query, index=self.index_name, headers=es_util.headers)
        return [COEResult.from_es(i) for i in response['hits']['hits']
                if float(i['_score']) > threshold]


class COEChainRetriver(BaseExampleSelector):
    def __init__(self, type, var_names=['ind', 'desc', 'answer'], k=3):
        self.index_name = 'coe_analysis_experience'
        self.client = es_util.client
        self.type = type
        self.vector_field = 'search_embedding'
        self.k = k
        self.ind_name = var_names[0]
        self.desc_name = var_names[1] if len(var_names) > 1 else 'desc'
        self.ans_name = var_names[2] if len(var_names) > 2 else 'answer'
        self.search_name = 'query'
        self.cache = []

    def retrive(self, query: str) -> List[Experience]:
        if (self.k == 0):
            return []
        threshold = float(lion.config[f'{lion.app_name}.cot_threshold'])
        query_vector = embed.get_embedding(query)
        body = {
            "script_score": {
                "query": {"bool": {"must": [
                    {'term': {'type': self.type}},
                    {'term': {'is_marked': 'true'}},
                    # 必须存在 search_embedding，否则会报错
                    {"exists": {"field": "search_embedding"}}
                ]}},
                "script": {
                    "source": "cosineSimilarity(params.query_vector," +
                    f"'{self.vector_field}') + 1.0",
                    "params": {"query_vector": query_vector},
                }
            }
        }
        query = {'query': body, 'size': self.k}
        response = self.client.search(
            body=query, index=self.index_name, headers=es_util.headers)
        return [Experience.from_es(i) for i in response['hits']['hits']
                if float(i['_score']) > threshold]

    def add_example(self, example: Dict[str, str]) -> Any:
        """Add new example to store for a key."""
        # 不实现
        pass

    def select_examples(self, input_variables: Dict[str, str]) -> List[dict]:
        """Select which examples to use based on the inputs."""
        exp_list = self.retrive(input_variables[self.search_name])
        inps = []
        cache = []
        for ind, exp in enumerate(exp_list):
            inps.append({
                self.ind_name: ind,
                self.desc_name: exp.search_text,
                self.ans_name: exp.data[-1].content
            })
            cache.append(SimiliarCase(exp_id=exp.id))
        self.cache = cache
        return inps


EMBED_CACHE = {}


class COEChatRetriver(BaseRetriever):
    def __init__(self, min_token=1000, k=20, type=None):
        self.index_name = 'coe_crawler_data'
        self.client = es_util.client
        self.type = type
        self.k = k
        self.min_token = min_token
        self.vector_field = 'embedding'

    def get_relevant_documents(self, query: str, coe_id: str) -> List[Document]:
        """Get documents relevant for a query.

        Args:
            query: string to find relevant documents for

        Returns:
            List of relevant documents
        """
        if (self.k == 0 or self.min_token == 0):
            return []
        if query in EMBED_CACHE:
            query_vector = EMBED_CACHE[query]
        else:
            query_vector = embed.get_embedding(query)
            EMBED_CACHE[query] = query_vector
        must_inner = [
            {'term': {'is_activate': 'true'}},
            {'term': {'coe_id': coe_id}},
            {"exists": {"field": self.vector_field}}  # 必须存在 embedding，否则会报错
        ]
        if self.type is not None:
            must_inner.append({'term': {'type': self.type}})
        body = {
            "script_score": {
                "query": {"bool": {"must": must_inner}},
                "script": {
                    "source": "cosineSimilarity(params.query_vector," +
                    f"'{self.vector_field}') + 1.0",
                    "params": {"query_vector": query_vector},
                }
            }
        }
        query = {'query': body, 'size': self.k}
        response = self.client.search(
            body=query, index=self.index_name, headers=es_util.headers)
        docs = []
        token = 0
        for hit in response['hits']['hits']:
            # score = hit['_score']
            item = COECrawlerData.from_es(hit)
            doc = Document(
                page_content=item.get_text(),
                metadata=item.to_json_dict())
            add_token = count_token(doc.page_content)
            if token + add_token >= self.min_token:
                break
            token += add_token
            docs.append(doc)
        return docs[::-1]

    async def aget_relevant_documents(self, query: str, coe_id: str) -> List[Document]:
        """
        尚未实现并发
        """
        return self.get_relevant_documents(query, coe_id)
