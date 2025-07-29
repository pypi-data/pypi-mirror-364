from service.aui_test_agent.es_importer import es_util, RECORDED_INSTRUCTION_WEB_INDEX
from utils import logger
from service.aui_test_agent.mock_driver import upload_image


class TokenData:
    def __init__(self, completion: str, prompt: str, total: int):
        self.completion = completion
        self.prompt = prompt
        self.total = total

    @classmethod
    def from_json(cls, data: dict):
        return cls(
            completion=data.get("completion"),
            prompt=data.get("prompt"),
            total=data.get("total"),
        )

    def as_dict(self, exclude_paths=None):
        exclude_paths = exclude_paths or []
        result = {
            "completion": self.completion,
            "prompt": self.prompt,
            "total": self.total,
        }
        return {k: v for k, v in result.items() if k not in exclude_paths}


class ExplainData:
    def __init__(self, content: str, cost: float, notice: str, tokens: TokenData):
        self.content = content
        self.cost = cost
        self.tokens = tokens
        self.notice = notice

    @classmethod
    def from_json(cls, data: dict):
        return cls(
            content=data.get("content"),
            cost=data.get("cost"),
            notice=data.get('notice'),
            tokens=TokenData.from_json(
                data.get("tokens")) if data.get("tokens") else None,
        )

    def as_dict(self, exclude_paths=None):
        exclude_paths = exclude_paths or []
        result = {
            "content": self.content,
            "cost": self.cost,
            'notice': self.notice,
            "tokens": self.tokens.as_dict(exclude_paths) if self.tokens else None
        }
        return {k: v for k, v in result.items() if k not in exclude_paths}


class RectData:
    def __init__(self, height: int, width: int, x: int, y: int):
        self.height = height
        self.width = width
        self.x = x
        self.y = y

    @classmethod
    def from_json(cls, data: dict):
        return cls(
            height=data.get("height"),
            width=data.get("width"),
            x=data.get("x"),
            y=data.get("y"),
        )

    def as_dict(self, exclude_paths=None):
        exclude_paths = exclude_paths or []
        result = {
            "height": self.height,
            "width": self.width,
            "x": self.x,
            "y": self.y,
        }
        return {k: v for k, v in result.items() if k not in exclude_paths}


class ScreenshotData:
    def __init__(self, content: str, somContent: str, rect: RectData, scale: float):
        self.content = content
        self.rect = rect
        self.scale = scale
        self.somContent = somContent

    @classmethod
    def from_json(cls, data: dict):
        return cls(
            content=data.get("content"),
            rect=RectData.from_json(
                data.get("rect")) if data.get("rect") else None,
            scale=data.get("scale"),
            somContent=data.get('somContent')
        )

    def save_to_s3(self):
        self.content = upload_image(self.content)
        self.somContent = upload_image(self.somContent)

    def as_dict(self, exclude_paths=None):
        exclude_paths = exclude_paths or []
        result = {
            "content": self.content,
            "rect": self.rect.as_dict(exclude_paths) if self.rect else None,
            "scale": self.scale,
            'somContent': self.somContent
        }
        return {k: v for k, v in result.items() if k not in exclude_paths}


class TargetData:
    def __init__(self, className: str, cssPath: str, devicePixelRatio: float, id: str, index: int,
                 name: str, screenshotData: ScreenshotData, tagName: str,
                 title: str, value: str, xpath: str, dom: str, rect: RectData):
        self.className = className
        self.cssPath = cssPath
        self.devicePixelRatio = devicePixelRatio
        self.id = id
        self.index = index
        self.name = name
        self.screenshotData = screenshotData
        self.tagName = tagName
        self.title = title
        self.value = value
        self.xpath = xpath
        self.dom = dom
        self.rect = rect

    @classmethod
    def from_json(cls, data: dict):
        return cls(
            className=data.get("className"),
            cssPath=data.get("cssPath"),
            devicePixelRatio=data.get("devicePixelRatio"),
            id=data.get("id"),
            index=data.get("index"),
            name=data.get("name"),
            screenshotData=ScreenshotData.from_json(data.get("screenshotData")) if data.get("screenshotData") else None,  # noqa
            tagName=data.get("tagName"),
            title=data.get("title"),
            value=data.get("value"),
            xpath=data.get("xpath"),
            dom=data.get("dom"),
            rect=RectData.from_json(data.get("rect")) if data.get("rect") else None,
        )

    def as_dict(self, exclude_paths=None):
        exclude_paths = exclude_paths or []
        screenshotExclude = [i.replace('screenshotData.', '')
                             for i in exclude_paths if 'screenshotData.' in i]
        rectExclude = [i.replace('rect.', '') for i in exclude_paths if 'rect.' in i]
        result = {
            "className": self.className,
            "cssPath": self.cssPath,
            "devicePixelRatio": self.devicePixelRatio,
            "id": self.id,
            "index": self.index,
            "name": self.name,
            "screenshotData": self.screenshotData.as_dict(screenshotExclude) if self.screenshotData else None,
            "tagName": self.tagName,
            "title": self.title,
            "value": self.value,
            "xpath": self.xpath,
            "dom": self.dom,
            "rect": self.rect.as_dict(rectExclude) if self.rect else None
        }
        return {k: v for k, v in result.items() if k not in exclude_paths}


class RecordedData:
    def __init__(self, target: TargetData, explain: ExplainData, timestamp: int,
                 type: str, url: str, id: str, record_id: int, loop_version: int,
                 deltaX: int, deltaY: int, deltaMode: str, record_task_id: str,
                 key: str, x: int, y: int, scrollWidth: int, scrollHeight: int,
                 value: str, groundingOK: bool, **kargs):
        self.target = target
        self.explain = explain
        self.timestamp = timestamp
        self.type = type
        self.url = url
        self.loop_version = loop_version
        self.record_task_id = record_task_id
        self.id = id
        self.record_id = record_id
        self.deltaX = deltaX
        self.deltaY = deltaY
        self.deltaMode = deltaMode
        self.x = x
        self.y = y
        self.key = key
        self.scrollWidth = scrollWidth
        self.scrollHeight = scrollHeight
        self.value = value
        self.groundingOK = groundingOK

    @classmethod
    def from_json(cls, data: dict):
        return cls(
            target=TargetData.from_json(
                data.get("target")) if data.get("target") else None,
            explain=ExplainData.from_json(
                data.get("explain")) if data.get("explain") else None,
            timestamp=data.get("timestamp"),
            type=data.get("type"),
            url=data.get("url"),
            loop_version=data.get("loop_version", 0),
            id=data.get('id'),
            record_task_id=data.get('record_task_id'),
            record_id=data.get('record_id'),
            deltaX=data.get("deltaX", 0),
            deltaY=data.get("deltaY", 0),
            deltaMode=data.get("deltaMode", ""),
            x=data.get("x", 0),
            y=data.get("y", 0),
            key=data.get("key", ""),
            scrollWidth=data.get("scrollWidth", 0),
            scrollHeight=data.get("scrollHeight", 0),
            value=data.get('value'),
            groundingOK=data.get('groundingOK', None)
        )

    def as_dict(self, exclude_paths=['explain', 'target.dom',
                                     'target.screenshotData.content',
                                     'target.screenshotData.somContent']):
        exclude_paths = exclude_paths or []
        target_exclude = [i.replace('target.', '')
                          for i in exclude_paths if 'target.' in i]
        explain_exclude = [i.replace('explain.', '')
                           for i in exclude_paths if 'explain.' in i]
        result = {
            "target": self.target.as_dict(target_exclude) if self.target else None,
            "explain": self.explain.as_dict(explain_exclude) if self.explain else None,
            "timestamp": self.timestamp,
            "type": self.type,
            "url": self.url,
            "loop_version": self.loop_version,
            "id": self.id,
            'record_task_id': self.record_task_id,
            "record_id": self.record_id,
            "deltaX": self.deltaX,
            "deltaY": self.deltaY,
            "deltaMode": self.deltaMode,
            "x": self.x,
            "y": self.y,
            "key": self.key,
            "scrollWidth": self.scrollWidth,
            "scrollHeight": self.scrollHeight,
            'value': self.value,
            'groundingOK': self.groundingOK
        }
        return {k: v for k, v in result.items() if k not in exclude_paths}

    def update_to_es(self):
        if self.target.screenshotData.content.startswith('data:image'):
            self.target.screenshotData.save_to_s3()
        data = self.as_dict(exclude_paths=[])  # 全部保存，不需要排除任何路径
        data = {"doc": data}
        es_util.update(RECORDED_INSTRUCTION_WEB_INDEX, id=self.id, body=data)

    def save_to_es(self):
        if self.target.screenshotData.content.startswith('data:image'):
            self.target.screenshotData.save_to_s3()
        data = self.as_dict(exclude_paths=[])  # 全部保存，不需要排除任何路径
        es_util.index(RECORDED_INSTRUCTION_WEB_INDEX, body=data, id=self.id)

    @classmethod
    def read_from_es(cls, record_id, record_task_id):
        data = es_util.search(RECORDED_INSTRUCTION_WEB_INDEX, query={
            "query": {"bool": {"must": [
                {"term": {"record_id": record_id}},
                {"term": {"record_task_id": record_task_id}}
            ]}},
            "sort": [{"timestamp": {"order": "desc"}}],
            "size": 5
        })
        assert len(data) > 0, '没有找到对应的 record'
        return cls.from_json(data[0]['_source'])


ES_INIT_MAPPER = {
    "mappings": {
        "properties": {
            "target": {
                "properties": {
                    "className": {"type": "keyword"},
                    "cssPath": {"type": "keyword"},
                    "devicePixelRatio": {"type": "float"},
                    "id": {"type": "keyword"},
                    "index": {"type": "integer"},
                    "name": {"type": "keyword"},
                    "screenshotData": {
                        "properties": {
                            "content": {"type": "text"},
                            "rect": {
                                "properties": {
                                    "height": {"type": "integer"},
                                    "width": {"type": "integer"},
                                    "x": {"type": "integer"},
                                    "y": {"type": "integer"}
                                }
                            },
                            "scale": {"type": "float"},
                            "somContent": {"type": "text"}
                        }
                    },
                    "tagName": {"type": "keyword"},
                    "title": {"type": "keyword"},
                    "value": {"type": "keyword"},
                    "xpath": {"type": "keyword"},
                    "dom": {"type": "text"},
                    "rect": {
                        "type": "nested",
                        "properties": {
                            "height": {"type": "integer"},
                            "width": {"type": "integer"},
                            "x": {"type": "integer"},
                            "y": {"type": "integer"}
                        }
                    }
                }
            },
            "explain": {
                "properties": {
                    "content": {"type": "text"},
                    "cost": {"type": "float"},
                    "notice": {"type": "text"},
                    "tokens": {
                        "properties": {
                            "completion": {"type": "integer"},
                            "prompt": {"type": "integer"},
                            "total": {"type": "integer"}
                        }
                    }
                }
            },
            "timestamp": {"type": "date", "format": "epoch_millis||epoch_second"},
            "type": {"type": "keyword"},
            "url": {"type": "keyword"},
            "loop_version": {"type": "integer"},
            "id": {"type": "keyword"},
            "record_task_id": {"type": "keyword"},
            "record_id": {"type": "integer"},
            "deltaX": {"type": "integer"},
            "deltaY": {"type": "integer"},
            "deltaMode": {"type": "keyword"},
            "x": {"type": "integer"},
            "y": {"type": "integer"},
            "key": {"type": "keyword"},
            "scrollWidth": {"type": "integer"},
            "scrollHeight": {"type": "integer"},
            'value': {'type': 'text'},
            'groundingOK': {'type': 'boolean'}
        }
    }
}


if __name__ == '__main__':
    try:
        index_name = RECORDED_INSTRUCTION_WEB_INDEX
        # 检查索引是否已存在
        if es_util.client.indices.exists(index=index_name):
            logger.info(f"Index '{index_name}' already exists.")
        else:
            # 创建索引并设置 mapping
            es_util.client.indices.create(index=index_name, body=ES_INIT_MAPPER)
            logger.info(f"Index '{index_name}' created successfully with mapping.")
    except Exception as e:
        logger.error(f"Error creating index '{index_name}': {e}")
