import os
import shutil
from AUITestAgent import UITestRobot
from service.aui_test_agent.mock_driver import MockWebDriver
from service.aui_test_agent.ui_instruction_analysis.es_storage import RecordedData, ExplainData
from service.aui_test_agent.ui_instruction_analysis.analysis_loop import AnalysisLoop
import uuid
from service.aui_test_agent.es_importer import es_util, RECORDED_INSTRUCTION_WEB_INDEX
from concurrent.futures import ThreadPoolExecutor
import threading
from utils import logger

# 创建全局队列和线程池
executor = ThreadPoolExecutor(max_workers=2)  # 设置线程池最大线程数
executor_lock = threading.Lock()


class UITestAgentRobotTriggerError(Exception):
    def __init__(self, *args):
        super().__init__(*args)


def trigger_agent(driver_args: dict, method_name: str, **kargs):
    robot = UITestRobot(
        test_work_dir=os.path.join('./log', 'aui_test_agent-' + str(uuid.uuid1())),
        drive_mode=1, driver=MockWebDriver(
            screenshot=driver_args.get('screenshot', ''),
            xml=driver_args.get('xml', {}),
            device_size=driver_args.get('device_size', [None, None])
        ))
    method = robot.__getattribute__(method_name)
    if not callable(method):
        raise ValueError(f"The method '{method_name}' is not callable.")
    try:
        messages = method(**kargs)
        return messages
    except Exception as e:
        method_doc = method.__doc__ or f"{method_name} 缺失描述文档"
        error_message = f"{str(e)}\n\nMethod Help:\n{method_doc}"
        raise UITestAgentRobotTriggerError(error_message) from e
    finally:
        work_dir = robot.work_dir
        # 删除 work_dir
        shutil.rmtree(work_dir, ignore_errors=True)


def init_record(record_data_json: dict, record_task_id: str, record_id: int):
    record_data = RecordedData.from_json(record_data_json)
    record_data.loop_version = -1
    event = record_data
    event_type_messages = {
        'click': lambda e: f'坐标: ({e.x}, {e.y})',
        'input': lambda e: f'输入值: {e.value}',
        'scroll': lambda e: f'滚动位置: ({e.x}, {e.y}) 滚动宽度: {e.scrollWidth} 滚动高度: {e.scrollHeight}',
        'wheel': lambda e: f'滚轮位置: ({e.x}, {e.y}) 滚轮增量: ({e.deltaX}, {e.deltaY})',
        'navigate': lambda e: f'跳转地址: {e.url}'
    }
    content = event_type_messages.get(event.type, lambda _: '无详细信息')(event)
    record_data.explain = ExplainData(content=content, cost=0, tokens=None, notice=None)
    record_data.record_id = record_id
    record_data.record_task_id = record_task_id
    record_data.id = uuid.uuid1().__str__()
    record_data.save_to_es()  # 首次保存到 es
    return record_data


def explain_record(record_data: RecordedData):
    """将任务提交到线程池中异步执行"""
    def task(record_data: RecordedData):
        try:
            loop = AnalysisLoop(record_data, platform='Android',
                                work_dir=os.path.join('./log', 'aui_test_agent-' + str(uuid.uuid1())))
            loop.run()
        except Exception as e:
            # 处理异常
            logger.error('explain_record 线程异常', e)
        finally:
            shutil.rmtree(loop.work_dir, ignore_errors=True)

    # 提交任务到线程池
    with executor_lock:
        executor.submit(task, record_data)


def search_record(record_task_id: str):
    data = es_util.search(RECORDED_INSTRUCTION_WEB_INDEX, query={
        "query": {"bool": {"must": [
            {"term": {"record_task_id": record_task_id}}
        ]}},
        "sort": [{"record_id": {"order": "asc"}}],
        "size": 1000
    })
    return [RecordedData.from_json(i['_source']).as_dict(exclude_paths=['target.dom']) for i in data]
