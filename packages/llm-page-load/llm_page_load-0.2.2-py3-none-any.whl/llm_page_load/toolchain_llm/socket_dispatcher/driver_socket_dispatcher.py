from functools import partial
import time
from service.aui_test_agent.hyperjump_copilot.es_storaget import SocketEvent, SocketStorage
from service.aui_test_agent.hyperjump_copilot.message_server import manage_event
from socket_dispatcher.base_socket_dispatcher import BaseSocketDispatcher
from socket_dispatcher.queue_config import GLOBAL_QUEUES
from utils import logger
import threading
from flask import request
from queue import Queue
from service.aui_test_agent.hyperjump_copilot.ui_message_server import shared_data
from service.aui_test_agent.hyperjump_copilot.message_server import ChatResponseManager
from service.aui_test_agent.hyperjump_copilot.ui_message_server import CaseGenerateResponseManager


class DriverSocketDispatcher(BaseSocketDispatcher):
    '''
    聊天消息的Socket Dispatcher
    每个 DriverSocketDispatcher 实例确实对应一个唯一的 socket.sid，这是由 Flask-SocketIO 的 request.sid 机制保证的。
    '''

    def __init__(self, s, namespace):
        super().__init__(s, namespace)

    def get_current_storage(self):
        current_socket_id = request.sid
        current_storage = SocketStorage.read_from_es(current_socket_id)
        return current_storage

    def on_disconnect(self):
        super().on_disconnect()
        storaget = self.get_current_storage()
        if SocketStorage.has_sid(storaget.peer_sid):
            peer_storage = SocketStorage.read_from_es(storaget.peer_sid)
            thread_queue = GLOBAL_QUEUES.get(peer_storage.sid)
            event = SocketEvent(event_name='chat', event_data='设备连接已断开，需要告诉用户，并回到最初的开场白1', direction='Device2Server')
            self.socket.start_background_task(manage_event, peer_storage, None,
                                              event, self.socket, thread_queue)
        storaget.is_end = True
        storaget.update_to_es()
        storaget.delete_()

    def on_connect(self):
        super().on_connect()
        current_sid = request.sid
        storage = SocketStorage(
            current_sid, self.namespace, start_time=int(time.time()*1000), remote_addr=request.remote_addr,
            user_token=None, thread_id=threading.get_ident(), events=[], peer_sid=None)
        storage.save_to_es()

    def on_message(self, message):
        '''收到消息时的处理逻辑'''
        logger.info('Thread ID: {}, Session ID: {}, Received Message: {}'.format(
            threading.get_ident(), request.sid, message))
        storage = self.get_current_storage()
        event = SocketEvent.from_json(message)
        storage.events.append(event)
        storage.update_to_es()
        if event.direction == 'Device2Server' and event.event_name == 'peer':
            # peer 请求用于匹配对端，需要准备对端，不放在 manage_message 中
            current_sid = request.sid
            peer_sid = event.event_data
            # 对端保存 es 数据
            try:
                peer_storage = SocketStorage.read_from_es(peer_sid)
                if peer_storage.is_end:
                    self.socket.emit('error', "Peer Socket Not Exist", to=current_sid, namespace=self.namespace)
                    self.socket.emit('action', 'stop', namespace='/hyperjump/copilot/driver', to=current_sid)  # 直接回收设备
                else:
                    peer_storage.peer_sid = current_sid
                    peer_storage.update_to_es()
                    thread_queue = GLOBAL_QUEUES.get(peer_storage.sid)
                    # peer 请求会被认为连接成功
                    self.socket.start_background_task(manage_event, peer_storage, storage,
                                                      event, self.socket, thread_queue)
            except Exception as e:
                logger.error('DriverSocketDispatcher Error', e)
                self.socket.emit('error', repr(e), to=current_sid, namespace=self.namespace)
            # 保存当前端
            storage.peer_sid = peer_sid
            storage.update_to_es()

        elif event.direction == 'Device2Server' and event.event_name == 'ready':
            logger.info('收到执行机发来的ready信息')
            print('收到执行机发来的ready信息')
            print('group_id:' + shared_data['lyrebird_group_id'])
            # 发送lyrebird_group_id给执行机
            self.socket.emit('lyrebird_group_id',shared_data['lyrebird_group_id'],namespace='/hyperjump/copilot/driver',to=request.sid)
            print('已发送lyrebird_group_id给执行机')
            # self.send_device_message()
            logger.info('已发送lyrebird_group_id给执行机')

            # 创建ChatResponseManager实例并发送消息
            if storage.peer_sid:
                try:
                    peer_storage = SocketStorage.read_from_es(storage.peer_sid)
                    chat_manager = ChatResponseManager(peer_storage, storage, self.socket, GLOBAL_QUEUES.get(peer_storage.sid))
                    case_manager = CaseGenerateResponseManager(peer_storage,storage,self.socket,GLOBAL_QUEUES.get(peer_storage.sid))
                    chat_manager.send_chat_message('设备连接成功，即将开始投屏，请观察右侧的页面。若符合预期，请回答【符合预期】，将自动执行用例保存，若不符预期，请回答【不符合预期】，将清除临时用例')
                    case_manager.send_chat_message('设备连接成功，即将开始投屏，请观察右侧的页面。若符合预期，请回答【符合预期】，将自动执行用例保存，若不符预期，请回答【不符合预期】，将清除临时用例')
                    print('查看前端页面')
                except Exception as e:
                    logger.error(f"发送消息到聊天前端失败: {e}")
                    print('发送消息到对话页面失败')

        # else:
        #     # 使用线程锁来保证消息处理的顺序
        #     if not hasattr(self, '_lock'):
        #         self._lock = threading.Lock()
        #     # 其他请求统一由 manage_message 处理
        #     current_sid = request.sid
        #     thread_queue = GLOBAL_QUEUES.get(current_sid)
        #     try:
        #         with self._lock:  # 加锁，确保当前任务完成前不会处理其他消息
        #             peer = SocketStorage.read_from_es(storage.peer_sid) if storage.peer_sid else None
        #             self.socket.start_background_task(manage_event, storage, peer, event, self.socket, thread_queue)
        #     except Exception as e:
        #         logger.error('DriverSocketDispatcher Error', e)
        #         self.socket.emit('error', repr(e), namespace=self.namespace, to=request.sid)

    def on_screenrecord(self, data):
        '''透传所有录屏请求到chat前端'''
        # logger.info('Thread ID: {}, Session ID: {}, ScreenRecord Pass'.format(threading.get_ident(), request.sid))
        storage = self.get_current_storage()
        current_sid = storage.sid
        peer_sid = storage.peer_sid
        try:
            peer_storage = SocketStorage.read_from_es(peer_sid)
            if peer_storage.is_end:
                self.socket.emit('error', "Peer Socket Not Exist", to=current_sid, namespace=self.namespace)
                self.socket.emit('action', 'stop', namespace='/hyperjump/copilot/driver', to=current_sid)  # 直接回收设备
            else:
                self.socket.emit('screenrecord', data, namespace='/hyperjump/copilot/chat', to=peer_sid)
                self.socket.emit('screenrecord', data, namespace='/hyperjump/copilot/case_generate', to=peer_sid)
        except Exception as e:
            logger.error('DriverSocketDispatcher Error', e)
            self.socket.emit('error', repr(e), to=current_sid, namespace=self.namespace)

    def on_action(self, message):
        logger.info('Thread ID: {}, Session ID: {}, Driver Action Done {}'.format(
            threading.get_ident(), request.sid, message))
        storage = self.get_current_storage()
        queue: Queue = GLOBAL_QUEUES[storage.peer_sid]
        queue.put(message, block=True, timeout=10)
        logger.info('done put')

    @classmethod
    def bind_socket(cls, socket, namespace):
        dispatcher = super().bind_socket(socket, namespace)
        dispatcher.socket.on_event('screenrecord', partial(dispatcher.on_screenrecord), namespace=dispatcher.namespace)
        dispatcher.socket.on_event('action', partial(dispatcher.on_action), namespace=dispatcher.namespace)
