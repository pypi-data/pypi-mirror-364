import json
import logging.config
import socket
import time
import openpyxl
from openpyxl.utils.escape import escape
import os
import re
from datetime import datetime
appkey = os.getenv('APPKEY', 'com.sankuai.aiengineering.llmapp')
MACHINE_ENV = os.environ.get('Env', 'dev')


GPT35NAME = 'gpt-3.5-turbo-16k'
GPT4NAME = 'gpt-4o-2024-08-06'


class CustomLogRecord(logging.LogRecord):
    def __init__(self, *args, **kwargs):
        self.hostname = kwargs.pop('hostname', socket.gethostname())
        self.appkey = kwargs.pop('appkey', appkey)
        super().__init__(*args, **kwargs)


logging.setLogRecordFactory(CustomLogRecord)
if MACHINE_ENV == 'dev':
    try:
        logging.config.fileConfig('config/record-dev.conf')
    except Exception as e:
        print(f"[Logging]{repr(e)}")
else:
    logging.config.fileConfig('config/record.conf')
logger = logging.getLogger("fileAndConsole")
test_logger = logging.getLogger('test')


def diff_time_string(time1, time2):
    # 将时间字符串转换为datetime对象
    dt1 = datetime.strptime(time1, "%Y-%m-%dT%H:%M:%SZ")
    dt2 = datetime.strptime(time2, "%Y-%m-%dT%H:%M:%SZ")
    # 计算时间差
    diff = dt1 - dt2
    # 返回时间差
    return diff


def timestring_to_TZ(time: str):
    '''输入YYYY-MM-DD mm-ss-SSS'''
    time_str = time.split(' ')
    return time_str[0]+'T'+time_str[1]+'Z'


def get_now_str():
    time_stamp = time.time()
    now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.localtime(time_stamp))
    return now


def read_json(file):
    with open(file, 'r', encoding='utf8') as f:
        return json.load(f)


def write_json(file, data):
    with open(file, 'w', encoding='utf8') as f:
        json.dump(data, f, ensure_ascii=False, default=lambda obj: obj.__dict__())


def write_io(filename, data_list):
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    current_line = 1
    col_idx = 65  # A
    colnames = []
    for colname, cell in data_list[0].items():
        colnames.append(colname)
        sheet[f'{chr(col_idx)}{current_line}'] = colname
        col_idx += 1
    for item in data_list:
        current_line += 1
        col_idx = 65
        for colname in colnames:
            if (colname not in item):
                continue
            try:
                sheet[f'{chr(col_idx)}{current_line}'] = escape(str(item[colname]))
            except Exception:
                logger.error('escape转换失败', exc_info=True)

            col_idx += 1
    workbook.save(filename)


def merge_lines(text):
    if not text or text == '':
        return []
    lines = text.split('\n')
    lines = [line for line in lines if line.strip() != '']
    previousLine = ''
    result = []
    regex = re.compile(r'([^0-9:：]+)[:：]([^\n]*)')
    for line in lines:
        match = regex.match(line)
        if match:
            key = match.group(1).strip()
            value = match.group(2).strip()
            result.append({'key': key, 'value': value})
            previousLine = line
        else:
            if previousLine != '':
                previousMatch = regex.match(previousLine)
                if previousMatch:
                    value = previousMatch.group(2).strip() + line
                    result[-1]['value'] = value
    return result
