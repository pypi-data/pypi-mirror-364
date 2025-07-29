import time
from service.aui_test_agent.es_importer import es_util, SOCKET_STORAGET_INDEX
from utils import logger
from typing import List

SOCKET_INOF_DICT = {}  # 全局存储到内存
HISTORY_LIMIT = 30


class SocketEvent:
    def __init__(self, event_name, event_data: str, timestamp=None, direction=None):
        self.event_name = event_name  # 事件名称
        self.event_data = event_data  # 事件数据
        self.timestamp = timestamp  # 时间戳
        self.direction = direction  # 方向，包括 Frontend2Service、Service2Device 这些
        if timestamp is None:
            timestamp = int(time.time()*1000)

    @classmethod
    def from_json(cls, data: dict):
        return cls(
            event_name=data.get("event_name"),
            event_data=data.get("event_data"),
            timestamp=data.get("timestamp", int(time.time()*1000)),
            direction=data.get("direction"),
        )

    def as_dict(self, exclude_paths=None):
        exclude_paths = exclude_paths or []
        result = {
            "event_name": self.event_name,
            "event_data": self.event_data,
            "timestamp": self.timestamp,
            "direction": self.direction,
        }
        return {k: v for k, v in result.items() if k not in exclude_paths and v is not None}


class ChatMessage:
    def __init__(self, role, content, image_path=None):
        self.role = role
        self.content = content
        self.image_path = image_path

    @classmethod
    def from_json(cls, data: dict):
        return cls(
            role=data.get("role"),
            content=data.get("content"),
            image_path=data.get("image_path"),
        )

    def as_dict(self, exclude_paths=None):
        exclude_paths = exclude_paths or []
        result = {
            "role": self.role,
            "content": self.content,
            "image_path": self.image_path,
        }
        return {k: v for k, v in result.items() if k not in exclude_paths and v is not None}


class MetaAgentAction:
    def __init__(self, plan, action, oracle, result, url_scheme):
        self.plan = plan
        self.action = action
        self.oracle = oracle
        self.result = result
        self.url_scheme = url_scheme

    @classmethod
    def from_json(cls, data: dict):
        return cls(
            plan=data.get("plan"),
            action=data.get("action"),
            oracle=data.get("oracle"),
            result=data.get("result"),
            url_scheme=data.get("url_scheme"),
        )

    def as_dict(self, exclude_paths=None):
        exclude_paths = exclude_paths or []
        result = {
            "plan": self.plan,
            "action": self.action,
            "oracle": self.oracle,
            "result": self.result,
            "url_scheme": self.url_scheme,
        }
        return {k: v for k, v in result.items() if k not in exclude_paths and v is not None}


class StateMemory:
    def __init__(self, actions: List[MetaAgentAction] = [], platform='Android', app='Meituan', generated_cases='{}',sceneid=None,params={}
                 ):
        self.actions = actions
        self.platform = platform
        self.app = app
        self.generated_cases = generated_cases
        self.sceneid=sceneid
        self.params=params

    @classmethod
    def from_json(cls, data: dict):
        return cls(
            actions=[MetaAgentAction.from_json(
                action) for action in data.get("actions", [])],
            platform=data.get("platform", 'Android'),
            app=data.get("app", 'Meituan'),
            generated_cases=data.get('generated_cases', '{}'),
            sceneid=data.get('sceneid'),
            params=data.get('params', {})
        )

    def as_dict(self, exclude_paths=None):
        exclude_paths = exclude_paths or []
        actions_exclude = [i.replace('actions.', '')
                           for i in exclude_paths if 'actions.' in i]
        result = {
            "actions": [action.as_dict(actions_exclude) for action in self.actions],
            "platform": self.platform,
            "app": self.app,
            'generated_cases': self.generated_cases,
            'sceneid': self.sceneid,
            'params': self.params
        }
        return {k: v for k, v in result.items() if k not in exclude_paths and v is not None}


class SocketStorage:
    def __init__(self, sid, namespace, start_time, remote_addr, user_token,
                 thread_id, events: List[SocketEvent] = [], peer_sid=None, end_time=None,
                 chat_history: List[ChatMessage] = [], state_memory: StateMemory = None, is_end=False):
        self.sid = sid
        self.namespace = namespace
        self.start_time = start_time
        self.remote_addr = remote_addr
        self.user_token = user_token
        self.end_time = end_time
        self.thread_id = thread_id
        self.events = events
        self.peer_sid = peer_sid
        self.chat_history = chat_history
        self.state_memory = state_memory if state_memory else StateMemory()
        self.is_end = is_end

    @classmethod
    def from_json(cls, data: dict):
        return cls(
            sid=data.get("sid"),
            namespace=data.get("namespace"),
            start_time=data.get("start_time", int(time.time()*1000)),
            remote_addr=data.get("remote_addr"),
            user_token=data.get("user_token"),
            end_time=data.get("end_time"),
            thread_id=data.get("thread_id"),
            events=[SocketEvent.from_json(event)
                    for event in data.get("events", [])],
            peer_sid=data.get("peer_sid"),
            chat_history=[ChatMessage.from_json(
                msg) for msg in data.get("chat_history", [])],
            state_memory=StateMemory.from_json(
                data.get("state_memory")) if data.get("state_memory") else None,
            is_end=data.get('is_end')
        )

    def get_history_message(self):
        h = []
        for i in self.chat_history:
            h.append(i.as_dict())
        return h[-HISTORY_LIMIT:]

    def as_dict(self, exclude_paths=None):
        exclude_paths = exclude_paths or []
        events_exclude = [i.replace('events.', '')
                          for i in exclude_paths if 'events.' in i]
        chat_history_exclude = [
            i.replace('chat_history.', '') for i in exclude_paths if 'chat_history.' in i]
        state_memory_exclude = [
            i.replace('state_memory.', '') for i in exclude_paths if 'state_memory.' in i]
        result = {
            "sid": self.sid,
            "namespace": self.namespace,
            "start_time": self.start_time,
            "remote_addr": self.remote_addr,
            "user_token": self.user_token,
            "end_time": self.end_time,
            "thread_id": self.thread_id,
            "events": [event.as_dict(events_exclude) for event in self.events],
            "peer_sid": self.peer_sid,
            "chat_history": [msg.as_dict(chat_history_exclude) for msg in self.chat_history],
            "state_memory": self.state_memory.as_dict(state_memory_exclude) if self.state_memory else None,
            'is_end': self.is_end
        }
        return {k: v for k, v in result.items() if k not in exclude_paths and v is not None}

    def save_to_es(self):
        data = self.as_dict(exclude_paths=[])  # 全部保存
        # 使用内存保存
        SOCKET_INOF_DICT[self.sid] = data
        # 使用es保存
        # es_util.index(SOCKET_STORAGET_INDEX, body=data, id=self.sid)
        # es_util.client.indices.refresh(SOCKET_STORAGET_INDEX)

    @classmethod
    def read_from_es(cls, sid):
        # 使用内存保存
        if sid not in SOCKET_INOF_DICT:
            return None
        return cls.from_json(SOCKET_INOF_DICT[sid])
        # 使用es保存
        # data = es_util.search(SOCKET_STORAGET_INDEX, query={
        #     "query": {"term": {"sid": sid}},
        #     "size": 1
        # })
        # assert len(data) > 0, '没有找到对应的记录'
        # return cls.from_json(data[0]['_source'])

    def update_to_es(self):
        data = self.as_dict(exclude_paths=[])  # 全部保存
        data0 = SOCKET_INOF_DICT.get(self.sid, {})
        data0.update(data)
        SOCKET_INOF_DICT[self.sid] = data0
        # data = {"doc": data}
        # es_util.update(SOCKET_STORAGET_INDEX, id=self.sid, body=data)

    def delete_(self):
        if self.sid in SOCKET_INOF_DICT:
            del SOCKET_INOF_DICT[self.sid]
        # es 不用删
        # pass

    @staticmethod
    def has_sid(sid):
        return sid in SOCKET_INOF_DICT


ES_INIT_MAPPER = {
    "mappings": {
        "properties": {
            "sid": {"type": "keyword"},
            "namespace": {"type": "keyword"},
            "start_time": {"type": "date", "format": "epoch_millis||epoch_second"},
            "remote_addr": {"type": "keyword"},
            "user_token": {"type": "keyword"},
            "end_time": {"type": "date", "format": "epoch_millis||epoch_second"},
            "thread_id": {"type": "keyword"},
            "peer_sid": {"type": "keyword"},
            "events": {
                "type": "nested",
                "properties": {
                    "event_name": {"type": "keyword"},
                    "event_data": {"type": "text"},
                    "timestamp": {"type": "date", "format": "epoch_millis||epoch_second"},
                    "direction": {"type": "keyword"}
                }
            },
            "chat_history": {
                "type": "nested",
                "properties": {
                    "role": {"type": "keyword"},
                    "content": {"type": "text"},
                    "image_path": {"type": "keyword"}
                }
            },
            "state_memory": {
                "type": "object",
                "properties": {
                    "actions": {
                        "type": "nested",
                        "properties": {
                            "plan": {"type": "text"},
                            "action": {"type": "text"},
                            "oracle": {"type": "text"},
                            "result": {"type": "text"},
                            "url_scheme": {"type": "keyword"}
                        }
                    },
                    "platform": {"type": "keyword"},
                    "app": {"type": "keyword"},
                    'generated_cases': {"type": "text"},
                    'sceneid': {"type": "keyword"},
                    'params': {"type": "text"}
                }
            }
        }
    }
}


if __name__ == '__main__':
    try:
        index_name = SOCKET_STORAGET_INDEX
        # 检查索引是否已存在
        if es_util.client.indices.exists(index=index_name):
            logger.info(f"Index '{index_name}' already exists.")
        else:
            # 创建索引并设置 mapping
            es_util.client.indices.create(index=index_name, body=ES_INIT_MAPPER)
            logger.info(f"Index '{index_name}' created successfully with mapping.")
    except Exception as e:
        logger.error(f"Error creating index '{index_name}': {e}")
