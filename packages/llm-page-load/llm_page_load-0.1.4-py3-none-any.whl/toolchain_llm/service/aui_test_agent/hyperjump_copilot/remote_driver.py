import json
import os
from queue import Queue
import shutil
from typing import Dict, Tuple, Union
from AUITestAgent.utils.driver.abc_driver import ABCDriver
from flask_socketio import SocketIO
import requests
from service.aui_test_agent.hyperjump_copilot.es_storaget import SocketEvent, SocketStorage
from service.aui_test_agent.mock_driver import save_to_local
from utils import logger


class RemoteDriver(ABCDriver):
    def __init__(self, task_queue: Queue, socket: SocketIO,
                 chat_storage: SocketStorage, device_storage: SocketStorage):
        super().__init__()
        self.task_queue = task_queue
        self.socket = socket
        self.chat_storage = chat_storage
        self.device_storage = device_storage
        self.timeout = 60

    @staticmethod
    def download_content(url: str, save_path: str) -> None:
        """
        从HTTP URL下载图片到本地
        """
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            with open(save_path, 'wb') as file:
                for chunk in response.iter_content(1024):
                    file.write(chunk)
        else:
            raise Exception(f"Failed to download image from {url}, status code: {response.status_code}")

    def emit_action(self, func, kargs):
        logger.info(f'Driver Emit Action {func}({kargs})')
        self.socket.emit('action', SocketEvent(
            func, event_data=json.dumps(kargs), direction='Server2Device'
        ).as_dict(), namespace='/hyperjump/copilot/driver', to=self.device_storage.sid)

    def wait_for_result(self):
        try:
            ans = self.task_queue.get(block=True, timeout=self.timeout)
            logger.info(f'Driver Task Queue Received {ans}')
            return ans
        except Exception as e:
            logger.error('Driver没有收到消息', e)
            raise e

    def to_init_page(self):
        """到原始页面"""
        self.emit_action('to_init_page', {})
        ans = self.wait_for_result()
        event = SocketEvent(event_name='done', event_data=ans)
        return event.event_data

    def get_device_size(self) -> Union[Tuple[int, int], Tuple[None, None]]:
        """获取屏幕尺寸"""
        self.emit_action('get_device_size', {})
        ans = self.wait_for_result()
        event = SocketEvent(event_name='done', event_data=ans)
        return eval(event.event_data)

    def screenshot(self, save_path: str) -> str:
        """截图"""
        self.emit_action('screenshot', {"save_path": save_path})
        ans = self.wait_for_result()
        event = SocketEvent(event_name='done', event_data=ans)
        # 确保父目录存在
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        if event.event_data.startswith('http'):
            # 如果是 http 类型的地址，那么默认下载后保存图片
            self.download_content(event.event_data, save_path)
        elif event.event_data.startswith('data:image'):
            save_to_local(event.event_data, save_path)
        else:
            # 如果是本地的图片，那么把图片复制到save_path
            shutil.copy(event.event_data, save_path)
        return save_path

    def get_xml(self, save_path: str) -> str:
        """获取xml"""
        try:
            self.emit_action('get_xml', {"save_path": save_path})
            ans = self.wait_for_result()
            event = SocketEvent(event_name='done', event_data=ans)
            # 确保父目录存在
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            if event.event_data.startswith('http'):
                # 如果是 http 类型的地址，那么默认下载后保存图片
                self.download_content(event.event_data, save_path)
            else:
                # 如果是本地的图片，那么把图片复制到save_path
                shutil.copy(event.event_data, save_path)
        except Exception as e:
            logger.warning('get xml 失败', e)
        return save_path

    def go_back(self) -> Dict:
        """返回"""
        self.emit_action('go_back', {})
        ans = self.wait_for_result()
        event = SocketEvent(event_name='done', event_data=ans)
        return event.event_data

    def click(self, x: int, y: int) -> Dict:
        """点击"""
        self.emit_action('click', {'x': x, 'y': y})
        ans = self.wait_for_result()
        event = SocketEvent(event_name='done', event_data=ans)
        return event.event_data

    def long_click(self, x: int, y: int) -> Dict:
        """长按"""
        self.emit_action('long_click', {'x': x, 'y': y})
        ans = self.wait_for_result()
        event = SocketEvent(event_name='done', event_data=ans)
        return event.event_data

    def scroll(self, x1: int, y1: int, x2: int, y2: int, duration: int = 500) -> Dict:
        """滑动操作"""
        self.emit_action('scroll', {'x1': x1, 'y1': y1, 'x2': x2, 'y2': y2, 'duration': duration})
        ans = self.wait_for_result()
        event = SocketEvent(event_name='done', event_data=ans)
        return event.event_data

    def type(self, x: int, y: int, text: str) -> Dict:
        """输入操作"""
        self.emit_action('type', {'x': x, 'y': y, 'text': text})
        ans = self.wait_for_result()
        event = SocketEvent(event_name='done', event_data=ans)
        return event.event_data

    def delete_text(self, x1: int, y1: int):
        """删除文字操作"""
        self.emit_action('delete_text', {'x1': x1, 'y1': y1})
        ans = self.wait_for_result()
        event = SocketEvent(event_name='done', event_data=ans)
        return event.event_data
