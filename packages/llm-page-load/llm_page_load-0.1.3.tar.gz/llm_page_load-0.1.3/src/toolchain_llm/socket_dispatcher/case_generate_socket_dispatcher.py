import time
from service.aui_test_agent.hyperjump_copilot.es_storaget import ChatMessage, SocketEvent, SocketStorage
from socket_dispatcher.base_socket_dispatcher import BaseSocketDispatcher
from utils import logger
import threading
from flask import request
from service.aui_test_agent.hyperjump_copilot.ui_message_server import manage_event
from queue import Queue
from socket_dispatcher.queue_config import GLOBAL_QUEUES


class CaseGenerateSocketDispatcher(BaseSocketDispatcher):
    '''
    聊天消息的Socket Dispatcher
    每个 CaseGenerateSocketDispatcher 实例确实对应一个唯一的 socket.sid，这是由 Flask-SocketIO 的 request.sid 机制保证的。
    '''

    def __init__(self, socket, namespace):
        super().__init__(socket, namespace)

    def get_current_storage(self):
        current_socket_id = request.sid
        current_storage = SocketStorage.read_from_es(current_socket_id)
        return current_storage

    def on_message(self, message):
        '''收到消息时的处理逻辑'''
        logger.info('Thread ID: {}, Session ID: {}, Received Message: {}'.format(
            threading.get_ident(), request.sid, message))
        event = SocketEvent.from_json(message)
        storage = self.get_current_storage()
        storage.events.append(event)
        # 使用线程锁来保证消息处理的顺序
        current_sid = request.sid
        thread_queue = GLOBAL_QUEUES.get(current_sid)
        try:
            peer = None
            if storage.peer_sid:
                peer = SocketStorage.read_from_es(storage.peer_sid)
            self.socket.start_background_task(manage_event, storage, peer, event, self.socket, thread_queue)
        except Exception as e:
            logger.error('CaseGenerateSocketDispatcher Error', e)
            self.socket.emit('error', repr(e), namespace=self.namespace, to=request.sid)

    def on_disconnect(self):
        super().on_disconnect()
        event = SocketEvent(event_name='chat', direction='Server2Frontend', event_data='感谢使用')
        storage = self.get_current_storage()
        storage.is_end = True
        storage.update_to_es()
        self.send_message(event.as_dict())
        current_sid = request.sid
        if current_sid in GLOBAL_QUEUES:
            del GLOBAL_QUEUES[current_sid]
        if storage.peer_sid is not None:  # 强制回收设备
            self.socket.emit('action', 'stop', namespace='/hyperjump/copilot/driver', to=storage.peer_sid)
        storage.delete_()

    def on_connect(self):
        super().on_connect()
        current_sid = request.sid
        event = SocketEvent(
            event_name='chat', direction='Server2Frontend', event_data='请向我提问，可以说“帮我生成个客户端视觉用例，页面scheme是imeituan://home，direction是dzu”')
        storage = SocketStorage(
            current_sid, self.namespace, start_time=int(time.time()*1000), remote_addr=request.remote_addr,
            user_token=None, thread_id=threading.get_ident(), events=[event], peer_sid=None)
        storage.chat_history.append(ChatMessage(role='assistant', content=event.event_data))
        storage.save_to_es()
        self.send_message(event.as_dict())
        GLOBAL_QUEUES[current_sid] = Queue()

    def send_message(self, message):
        self.socket.emit('complete', message, namespace=self.namespace, to=request.sid)
