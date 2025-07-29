from dataclasses import dataclass, asdict, fields, field
import time
from typing import List, Optional
import uuid
from service.coe_analysis.crawler.crawler_data import CrawlerData
from service.lang_chain_utils.embedding import embed
from service.coe_analysis.crawler.ocr_api import get_ocr  # noqa
import re


@dataclass
class BaseDataClass:
    @classmethod
    def from_json(cls, input_json):
        if (input_json):
            allowed_fields = {field.name for field in fields(cls)}
            filtered_json = {k: v for k, v in input_json.items() if k in allowed_fields}
            return cls(**filtered_json)

    @classmethod
    def from_es(cls, es_answer_item):
        return cls.from_json(es_answer_item['_source'])

    def to_json_dict(self):
        def filter_none(obj):
            if isinstance(obj, dict):
                return {k: filter_none(v) for k, v in obj.items() if v is not None}
            elif isinstance(obj, list):
                return [filter_none(item) for item in obj]
            else:
                return obj

        return filter_none(asdict(self))


@dataclass
class CustomTemplateRequest(BaseDataClass):
    _id: int
    label: str
    key: str
    custom_domain_id: int
    custom: object
    default: str
    required: bool


@dataclass
class AutoFillRequest(BaseDataClass):
    incident_id: int
    custom_template: CustomTemplateRequest
    submitter: str = None

    @classmethod
    def from_json(cls, input_json):
        if 'custom_template' in input_json:
            input_json['custom_template'] = CustomTemplateRequest.from_json(input_json['custom_template'])
        return super().from_json(input_json)


@dataclass
class BaseSearch(BaseDataClass):
    task_id: List[str]
    coe_id: str
    type: str


@dataclass
class MetaMessage(BaseDataClass):
    role: str
    content: str = ''


@dataclass
class Tag(BaseDataClass):
    type: str
    analysis_result_id: str = None
    analysis_task_id: str = None
    analysis_result: str = None
    rd_result: str = None
    rd_reason: Optional[str] = None
    analysis_result_raw: str = None
    update_time: str = None
    trigger_fill_accepted: bool = None
    trigger_by_coe: bool = None


@dataclass
class MutiTag(BaseDataClass):
    type: str
    analysis_result: List[str] = None
    analysis_result_id: str = None
    analysis_task_id: str = None
    rd_result: List[str] = None
    update_time: str = None


@dataclass
class FundTag(BaseDataClass):
    type: str = 'fund_tag'
    update_time: str = None
    deal_loss_amount: str = None
    involved_amount: str = None
    actual_loss_amount: str = None
    financial_diff_amount: str = None
    is_fund_danger: Tag = None
    fund_aggr_classify: MutiTag = None
    mole_first_level_tag: str = None

    @classmethod
    def from_json(cls, input_json):
        tag_fields = ['is_fund_danger']
        for f in tag_fields:
            if f in input_json:
                input_json[f] = Tag.from_json(input_json[f])
        taglist_fields = ['fund_aggr_classify']
        for f in taglist_fields:
            if f in input_json:
                input_json[f] = MutiTag.from_json(input_json[f])
        return super(FundTag, cls).from_json(input_json)


@dataclass
class COEStoreageData(BaseDataClass):
    coe_id: str
    brief: str
    create_at: str
    create_by: str
    update_at: str
    org_id: str
    org_path: str
    category: str = None
    is_deleted: bool = False
    experience: str = None
    level: str = None
    coe_template_id: str = None
    coe_template_name: str = None
    all_tags_as_string: str = None

    # embeddings
    brief_embedding: List[float] = None
    cause_embedding: List[float] = None
    content_embedding: List[float] = None
    experience_embedding: List[float] = None

    # 六要两不要
    to_test: Optional[Tag] = None
    to_claim: Optional[Tag] = None
    to_check: Optional[Tag] = None
    to_grey: Optional[Tag] = None
    to_inspect: Optional[Tag] = None
    to_rollback: Optional[Tag] = None
    not_to_delay: Optional[Tag] = None
    not_to_illagle_change_data: Optional[Tag] = None

    # 资金安全
    fund_safety: Optional[FundTag] = None

    # 触发方式
    trigger_method: Optional[Tag] = None

    # 原因分析
    cause_analysis: Optional[Tag] = None

    @classmethod
    def from_json(cls, input_json):
        tag_fields = ['to_test', 'to_claim', 'to_check', 'to_grey', 'to_inspect', 'to_rollback',
                      'not_to_delay', 'not_to_illagle_change_data', 'trigger_method', 'cause_analysis']
        for f in tag_fields:
            if f in input_json:
                input_json[f] = Tag.from_json(input_json[f])
        if 'fund_safety' in input_json:
            input_json['fund_safety'] = FundTag.from_json(input_json['fund_safety'])
        return super(COEStoreageData, cls).from_json(input_json)


@dataclass
class Experience(BaseSearch):
    data: List[MetaMessage]
    id: str = None
    search_text: str = ''
    search_embedding: List[float] = None
    is_marked: bool = False
    brief: str = '缺失'
    level: str = ''
    pre_checked_passed: bool = True

    @classmethod
    def from_json(cls, experience_json):
        experience_json["data"] = [MetaMessage.from_json(meta_msg) for meta_msg in experience_json["data"]]
        return super(Experience, cls).from_json(experience_json)


@dataclass
class BaseCoeData(BaseDataClass):
    coe_id: str = None
    brief: str = None
    level: str = None

    @classmethod
    def from_json(cls, input_json):
        if ('_id' in input_json):
            input_json['coe_id'] = str(input_json['_id'])
        return super(BaseCoeData, cls).from_json(input_json)


@dataclass
class Arg(BaseDataClass):
    key: str
    value: str = None


@dataclass
class COEAnalysisTask(BaseDataClass):
    id: str
    name: str
    start_date: str
    end_date: str = None
    progress: str = "0/0"
    state: str = "未定义"
    source: str = "未定义"
    submitter: str = None
    sub_task_type_list: List[str] = None
    choosed_coe_list: List[BaseCoeData] = None
    is_active: bool = True
    extral_args: List[Arg] = field(default_factory=list)

    @classmethod
    def from_json(cls, input_json):
        if 'extral_args' in input_json:
            input_json['extral_args'] = [Arg.from_json(i) for i in input_json['extral_args']]
        if ('choosed_coe_list' in input_json):
            input_json["choosed_coe_list"] = [BaseCoeData.from_json(
                coe_data) for coe_data in input_json["choosed_coe_list"]]
        return super(COEAnalysisTask, cls).from_json(input_json)


@dataclass
class Answer(BaseDataClass):
    exp_id: str
    # data: List[MetaMessage] = None

    # @classmethod
    # def from_json(cls, input_json):
    #     input_json['data'] = [MetaMessage.from_json(meta_msg) for meta_msg in input_json['data']]
    #     return super(Answer,cls).from_json(input_json)


@dataclass
class SimiliarCase(BaseDataClass):
    # experience:List[MetaMessage] = None
    exp_id: str = None

    # @classmethod
    # def from_json(cls, input_json):
    #     input_json['experience'] = [MetaMessage.from_json(meta_msg) for meta_msg in input_json['experience']]
    #     return super(SimiliarCaseList,cls).from_json(input_json)


@dataclass
class ChangeLog(BaseDataClass):
    '''
    action = changeIndex , contentChange , reviewedTagChange
    '''
    action: str
    exp_index: int = None
    msg_index: int = None
    old_message: MetaMessage = None
    new_message: MetaMessage = None
    new_index_list: List[int] = None
    old_tag: bool = None
    new_tag: bool = None
    submitter: str = None

    @classmethod
    def from_json(cls, input_json):
        if ('old_message' in input_json):
            input_json['old_message'] = MetaMessage.from_json(input_json['old_message'])
        if ('new_message' in input_json):
            input_json['new_message'] = MetaMessage.from_json(input_json['new_message'])
        return super(ChangeLog, cls).from_json(input_json)


@dataclass
class COEResult(BaseSearch):
    id: str
    brief: str
    occur_time: str
    reason: str = None
    change_log: List[ChangeLog] = field(default_factory=list)
    search_vector: List[float] = None
    similiar_case_list: List[SimiliarCase] = field(default_factory=list)
    answer_message: List[Answer] = field(default_factory=list)
    message: List[MetaMessage] = field(default_factory=list)
    is_done: bool = False
    level: str = ''
    error: str = None
    is_reviewed: bool = False
    pre_checked_passed: bool = True
    is_reasonable: bool = True
    edit_time: str = None

    @classmethod
    def from_json(cls, coe_result_json):
        if ('error' in coe_result_json):
            if (isinstance(coe_result_json['error'], list)):
                coe_result_json['error'] = coe_result_json['error'][0]
        if ('answer_message' in coe_result_json):
            answer_message = coe_result_json.pop("answer_message")
            coe_result_json["answer_message"] = [
                Answer(
                    # data=[MetaMessage.from_json(meta_msg) for meta_msg in answer["data"]],
                    exp_id=answer['exp_id'] if "exp_id" in answer else None
                ) for answer in answer_message
            ]
        if ('similiar_case_list' in coe_result_json):
            similiar_case_list = coe_result_json.pop('similiar_case_list')
            coe_result_json['similiar_case_list'] = [
                SimiliarCase(exp_id=i['exp_id'] if 'exp_id' in i else None) for i in similiar_case_list
            ]
        if ('message' in coe_result_json):
            data_dict_list = coe_result_json.pop("message")
            coe_result_json['message'] = [
                MetaMessage.from_json(meta_msg) for meta_msg in data_dict_list
            ]
        if ('change_log' in coe_result_json):
            data_dict_list = coe_result_json.pop("change_log")
            coe_result_json['change_log'] = [
                ChangeLog.from_json(meta_msg) for meta_msg in data_dict_list
            ]
        return super(COEResult, cls).from_json(coe_result_json)


@dataclass
class TopicAnalysis(BaseDataClass):
    task_id: str
    query: str
    answer: str
    similar_coe_list: List[COEResult]

    @classmethod
    def from_json(cls, topic_analysis_json):
        coe_list_dict = topic_analysis_json.pop("similar_coe_list")
        topic_analysis_json["similar_coe_list"] = [
            COEResult.from_json(coe_data) for coe_data in coe_list_dict
        ]
        return super(TopicAnalysis, cls).from_json(topic_analysis_json)


@dataclass
class MetricsData(BaseDataClass):
    sequence_edit_rate: float = -1
    mean_edit_distance: float = -1
    total_edit_rate: float = -1
    accept_rate: float = -1
    reason_accept_rate: float = -1
    total: int = -1


def format_time(time: str):
    if time is None:
        return time
    pattern = re.compile(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}')
    if pattern.match(time):
        time = time.split(' ')
        time = time[0]+'T'+time[1]+'Z'
        return time
    return time


@dataclass
class COECrawlerData(BaseDataClass):
    sync_time: str
    id: str
    coe_id: str
    is_activate: bool = False
    embedding: List[float] = None
    data: str = None
    image_list: List[str] = None
    link_list: List[str] = None
    desc: str = None
    category: str = None
    time_stamp: str = None
    type: str = None

    @classmethod
    def from_crawler_data(cls, coe_id: str, sync_time: str, crawler_data: CrawlerData, need_embedding=False):
        id = str(uuid.uuid1().int)
        crawler_data.time_stamp = format_time(crawler_data.time_stamp)
        if need_embedding:
            emb = embed.get_embedding(crawler_data.get_text())
            time.sleep(1)  # 避免 embedding 超次数
            return cls(
                sync_time=sync_time,
                id=id,
                coe_id=coe_id,
                is_activate=True,
                data=crawler_data.data,
                embedding=emb,
                image_list=crawler_data.image_list,
                link_list=crawler_data.link_list,
                desc=crawler_data.desc,
                category=crawler_data.category,
                time_stamp=crawler_data.time_stamp,
            )
        else:
            return cls(
                sync_time=sync_time,
                id=id,
                coe_id=coe_id,
                is_activate=True,
                data=crawler_data.data,
                image_list=crawler_data.image_list,
                link_list=crawler_data.link_list,
                desc=crawler_data.desc,
                category=crawler_data.category,
                time_stamp=crawler_data.time_stamp,
            )

    def get_text(self):
        imgtxt = None
        # if (self.image_list and len(self.image_list) != 0):
        #     imgtxt = '截图文本如下:\n'
        #     for url in self.image_list:
        #         try:
        #             ocr = get_ocr(url)['data']['roi_text']
        #             ocr_text = []
        #             for item in ocr[:5]:
        #                 ocr_text.append(item['text'])
        #             imgtxt += f'{ocr_text}\n'
        #         except Exception:
        #             pass
        if (self.category):
            txt = f'{self.desc}\t[{self.category}]\n{self.data}\n'
        else:
            txt = f'{self.desc}\n{self.data}\n'
        if (imgtxt):
            txt = txt + imgtxt
        return txt + '\n'


def test_task():
    import json
    task_json = json.loads('''{
        "start_time":"111",
        "name":"a"
    }
    ''')
    task = COEAnalysisTask.from_json(task_json)
    print(task)


if __name__ == '__main__':
    test_task()
