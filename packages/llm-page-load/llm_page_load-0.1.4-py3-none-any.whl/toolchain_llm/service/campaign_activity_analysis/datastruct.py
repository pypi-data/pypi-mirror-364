from dataclasses import dataclass, asdict, fields, field
from typing import List, Dict


@dataclass
class BaseDataClass:
    @classmethod
    def from_json(cls, input_json):
        if (input_json):
            allowed_fields = {field.name for field in fields(cls)}
            filtered_json = {k: v for k,
                             v in input_json.items() if k in allowed_fields}
            return cls(**filtered_json)

    @classmethod
    def from_es(cls, es_answer_item):
        return cls.from_json(es_answer_item['_source'])

    def to_json_dict(self):
        return {k: v for k, v in asdict(self).items() if v is not None}


@dataclass
class CampaignEntity(BaseDataClass):
    entity_name: str
    id: str
    is_marked: bool = False
    edit_date: str = None


@dataclass
class CampaignRule(BaseDataClass):
    id: str
    entity_id_list: List[str]
    rule: str
    check: str = None
    type: str = 'stacking'
    is_marked: bool = False
    short_name: str = None
    edit_date: str = None
    is_deleted: bool = False

    @classmethod
    def from_json(cls, input_json):
        return super().from_json(input_json)


@dataclass
class ChangeLog(BaseDataClass):
    type: str  # 选项[REMOVE_CHILDREN, MARK_NODE, ADD_ANSWER_NODE, UPDATE_ANSWER_NODE]
    ref_node_id: str
    weight: int = 1
    old_content: str = None
    new_content: str = None
    old_children: List[str] = None
    new_children: List[str] = None


@dataclass
class TestCaseTreeNode(BaseDataClass):
    id: str
    task_id: str = None
    content: str = None
    answer_message: str = None
    embedding: List[float] = None
    parent_id: str = None
    children_id: List[str] = field(default_factory=list)
    type: str = None  # 选项[result, middle, query]
    is_marked: bool = False
    reference_rule_id_list: List[str] = None
    short_name: str = ' '
    edit_date: str = None
    change_log: List[ChangeLog] = field(default_factory=list)
    rule_type: str = None

    @classmethod
    def from_json(cls, json_data: dict):
        change_log_data = json_data.get('change_log')
        change_log = [ChangeLog.from_json(log) for log in change_log_data] if change_log_data else []
        json_data['change_log'] = change_log
        return super().from_json(json_data)


@dataclass
class TestCaseGenerationTask(BaseDataClass):
    id: str
    task_name: str
    rule_list: List[str] = field(default_factory=list)
    node_list: List[str] = field(default_factory=list)
    root_node: str = None
    status: str = None
    change_log: List[ChangeLog] = field(default_factory=list)
    progress: int = 0
    root_name: str = ' '
    user_name: str = None
    edit_date: str = None

    @classmethod
    def from_json(cls, json_data: dict):
        change_log_data = json_data.get('change_log')
        change_log = [ChangeLog.from_json(log) for log in change_log_data] if change_log_data else []
        json_data['change_log'] = change_log
        return super().from_json(json_data)


@dataclass
class DeepTask(TestCaseGenerationTask):
    tree_result: Dict = None
