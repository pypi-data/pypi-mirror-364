from dataclasses import dataclass
from typing import List
from flask_socketio import SocketIO
from utils import logger
import threading
from flask import request
from functools import partial


@dataclass
class BaseSocketDispatcher:
    '''
    主要类,作为websocket的获取
    使用方法是:
    socket_dispatcher = BaseSocketDispatcher.bind_socket(socket,namespace)
    '''
    socket: SocketIO
    namespace: str

    def on_message(self, message):
        logger.info('Thread ID: {}, Session ID: {}, Message'.format(
            threading.get_ident(), request.sid))

    def on_connect(self):
        logger.info('Thread ID: {}, Session ID: {}, Connected'.format(
            threading.get_ident(), request.sid))

    def on_disconnect(self):
        logger.info('Thread ID: {}, Session ID: {}, Dis Connect'.format(
            threading.get_ident(), request.sid))

    @classmethod
    def bind_socket(cls, socket: SocketIO, namespace: str):
        dispatcher = cls(socket, namespace)
        dispatcher.socket.on_event('disconnect', partial(
            dispatcher.on_disconnect), namespace=dispatcher.namespace)
        dispatcher.socket.on_event('connect', partial(
            dispatcher.on_connect), namespace=dispatcher.namespace)
        dispatcher.socket.on_event('message', partial(
            dispatcher.on_message), namespace=dispatcher.namespace)
        DISPATCHER_LIST.append(dispatcher)
        return dispatcher


'''
管理所有dispatcher
'''
DISPATCHER_LIST: List[BaseSocketDispatcher] = []
