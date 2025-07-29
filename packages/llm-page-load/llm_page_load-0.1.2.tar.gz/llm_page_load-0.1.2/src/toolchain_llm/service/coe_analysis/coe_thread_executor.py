from concurrent.futures import ThreadPoolExecutor
import functools
import logging

from service.coe_analysis.config_reader import get_config

logger = logging.getLogger('llmeval')


def auto_print_error(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.exception(f"函数 {func.__name__} 报错：{str(e)}")
            raise e
    return wrapper


class AutoExceptionThreadPoolExecutor(ThreadPoolExecutor):
    def submit(self, fn, /, *args, **kwargs):
        decorated_fn = auto_print_error(fn)
        return super().submit(decorated_fn, *args, **kwargs)


coe_executor = AutoExceptionThreadPoolExecutor(max_workers=int(get_config('thread_max_num')))
coe_es_writer = AutoExceptionThreadPoolExecutor(max_workers=1, thread_name_prefix='coe_es_writer')
