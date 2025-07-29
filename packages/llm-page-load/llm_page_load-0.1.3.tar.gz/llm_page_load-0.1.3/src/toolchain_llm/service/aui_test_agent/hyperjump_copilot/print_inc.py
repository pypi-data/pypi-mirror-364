import json
import threading
import builtins
from utils import logger
from typing import List, Callable
from AUITestAgent.utils.utils import BLUE, END
import time


class PrintInterceptor:
    def __init__(self, send):
        self.original_print = builtins.print
        self.send = send
        self.sended = set()

    def __enter__(self):
        def custom_print(*args, **kwargs):
            self.original_print(*args, **kwargs)
            # 处理参数,确保字典使用双引号
            processed_args = []
            for arg in args:
                if isinstance(arg, dict):
                    processed_args.append(json.dumps(arg, ensure_ascii=False))
                else:
                    # 尝试解析JSON字符串
                    try:
                        json_obj = eval(arg)
                        processed_args.append(json.dumps(json_obj, ensure_ascii=False))
                    except Exception:
                        processed_args.append(str(arg))
            message = " ".join(processed_args)

            logger.info('[AUITestAgent]' + message)
            if message.startswith(BLUE) and message.endswith(END):
                m = message.replace(BLUE, '').replace(END, '')
                if m not in self.sended:
                    try:
                        self.send(m)
                        self.sended.add(m)
                    except Exception as e:
                        logger.error('拦截打印事件出错', e)
        builtins.print = custom_print

    def __exit__(self, exc_type, exc_val, exc_tb):
        builtins.print = self.original_print


class PrintEventListener:
    def __init__(self, callback: Callable, thread_id: int):
        self.callback = callback
        self.thread_id = thread_id


class GlobalPrintManager:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialize()
            return cls._instance

    def _initialize(self):
        self.listeners: List[PrintEventListener] = []
        self._original_print = builtins.print

        def monitored_print(*args, **kwargs):
            message = ' '.join(str(arg) for arg in args)
            current_thread_id = threading.get_ident()

            # 首先执行原始打印
            self._original_print(*args, **kwargs)

            # 通知相关的监听器
            for listener in self.listeners:
                if listener.thread_id == current_thread_id:
                    listener.callback(message)

        builtins.print = monitored_print

    def add_listener(self, callback: Callable) -> PrintEventListener:
        listener = PrintEventListener(callback, threading.get_ident())
        self.listeners.append(listener)
        return listener

    def remove_listener(self, listener: PrintEventListener):
        if listener in self.listeners:
            self.listeners.remove(listener)


class PrintInterceptorV2:
    def __init__(self, send: Callable):
        self.send = send
        self.manager = GlobalPrintManager()
        self.listener = None
        self.sended = set()

    def custom_print(self, *args, **kwargs):
        # 处理参数,确保字典使用双引号
        processed_args = []
        for arg in args:
            if isinstance(arg, dict):
                processed_args.append(json.dumps(arg, ensure_ascii=False))
            else:
                # 尝试解析JSON字符串
                try:
                    json_obj = eval(arg)
                    processed_args.append(json.dumps(json_obj, ensure_ascii=False))
                except Exception:
                    processed_args.append(str(arg))
        message = " ".join(processed_args)

        logger.info('[AUITestAgent]' + message)
        if message.startswith(BLUE) and message.endswith(END):
            m = message.replace(BLUE, '').replace(END, '')
            if m not in self.sended:
                try:
                    self.send(m)
                    self.sended.add(m)
                except Exception as e:
                    logger.error('拦截打印事件出错', e)

    def __enter__(self):
        self.listener = self.manager.add_listener(self.custom_print)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.listener:
            self.manager.remove_listener(self.listener)


# 测试代码
def test_multi_thread(PrintInterceptor):
    def worker(name: str):
        def callback(msg: str):
            pass

        print(f"线程 {name} 开始")

        with PrintInterceptor(callback):
            print(f"这是 {name} 的消息")
            # 模拟延迟
            time.sleep(3)
            print(f"这是 {name} 的另一条消息")

        print(f"线程 {name} 结束")

    threads = [
        threading.Thread(target=worker, args=(f"Thread-{i}",))
        for i in range(2)
    ]

    for t in threads:
        t.start()
        time.sleep(0.5)
    for t in threads:
        t.join()


if __name__ == "__main__":
    test_multi_thread(PrintInterceptorV2)
    print('------------------------------------------------------')
    test_multi_thread(PrintInterceptor)
