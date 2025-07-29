# -*- coding: utf-8 -*-
import re
import json
from typing import Dict, List
import requests
import time
from datetime import datetime
from service.coe_analysis.crawler.crawler_data import CrawlerData
from service.coe_analysis.crawler.summary_data import SummaryData
from utils import read_json, write_json, logger
from bs4 import BeautifulSoup
from service.coe_analysis.config_reader import get_config, get_kms
from service.lang_chain_utils.lion_client import client as lion
from service.coe_analysis.data_structure import BaseCoeData


token = get_kms('COE_ACCESS_TOKEN')
agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_0_0) AppleWebKit/537.36 " +\
        "(KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36"


HTML_TAG_PATTERN = re.compile("<[a-zA-Z]+.*?>([\\s\\S]*?)</[a-zA-Z]*?>")

PING_TAI_JI_SHU_BU = json.loads(lion.config[f'{lion.app_name}.coe.PING_TAI_JI_SHU_BU'])

COE_API_HOST = get_config('COE_API_HOST')

CATEGORY_DICT = {
    'app': '大前端故障',
    'backend': '后台事故',
    'data': '大数据事故',
    'security': '安全事故',
    'non-technical': '非技术类事故',
    'drill': '故障演练'
}


def put_custom_instance(_id, value, trigger_fill_accepted, value_hover_html, fill_value):
    headers = {"Authorization": "Bearer %s" % token,
               "User-Agent": agent}
    body = {
        "_id": _id,
        "value": value,
        "trigger_fill_accepted": trigger_fill_accepted,
        "value_hover_html": value_hover_html,
        "fill_value": fill_value
    }
    resp = requests.put(f"{COE_API_HOST}/custom/instance", headers=headers, json=body)
    return resp


def getId(create_start, create_end, level, orgList=None, coe_template_id=None, sort_by="update_at"):
    '''
    获取COE的ID列表
    :param orgList: list，要查询的部门的org编号,
    :param create_start: str，最早创建时间，格式形如"2020-01-01"
    :param create_end: str，最晚创建时间
    :param level: list，线上问题的定级，["S1","S2","S3","S4","S9","E",""]
    :return: list，返回需要的COE文档的ID列表
    '''
    if orgList is None:
        lion.fetch_config()
        orgList = json.loads(lion.config[f'{lion.app_name}.coe.PING_TAI_JI_SHU_BU'])
    headers = {"Authorization": "Bearer %s" % token,
               "User-Agent": agent}

    params = {
        "key": "",
        "category": [

        ],
        "orgs": orgList,
        "level": level,
        "level_standard_category": [

        ],
        "level_standard_id": [

        ],
        "sort_by": "create_at",
        "sort": "desc",
        "list_type": "all",
        "page": 1,
        "page_size": 1000,
        "tags": [

        ],
        "appkey": "",
        "locators": "",
        "finders": "",
        "owt": "",
        "reason": [

        ],
        "duty_owt": [

        ],
        "is_contain": "包含",
        "occur_start": "",
        "occur_end": "",
        "create_start": create_start,
        "create_end": create_end,
    }
    if (coe_template_id):
        params['coe_template_id'] = coe_template_id
    if (sort_by):
        params['sort_by'] = sort_by
    url = f'{COE_API_HOST}/query/incidents'
    id_list = []
    item_dict: Dict[str, BaseCoeData] = {}
    for org in orgList:
        params['orgs'] = [org]
        res = requests.post(url=url, timeout=25, json=params, headers=headers)
        page = res.content
        responseReportJson = json.loads(page)
        # print(responseReportJson)
        for incident in responseReportJson['incidents']:
            item = BaseCoeData(
                coe_id=str(incident['_id']),
                brief=incident['brief'],
                level=incident['level']
            )
            item_dict[incident['_id']] = item
            id_list.append(incident['_id'])

    return id_list, item_dict


def get_datetime(date_str):
    if len(date_str) == 10:
        return datetime.strptime(date_str, '%Y-%m-%d')
    else:
        return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')


def getLatestId(create_start, create_end, update_start: str, level, orgList=None,
                update_end=None, filter_light_template=False, **kargs):
    '''
    获取COE的ID列表
    这个基本都是 crane 任务使用的
    按照更新期限来定
    update_start 应该是 %Y-%m-%d 10个字符
    '''
    if orgList is None:
        lion.fetch_config()
        orgList = json.loads(lion.config[f'{lion.app_name}.coe.PING_TAI_JI_SHU_BU'])
    headers = {"Authorization": "Bearer %s" % token,
               "User-Agent": agent,
               }
    update_start = get_datetime(update_start)
    if update_end is None:
        update_end = datetime.max
    else:
        update_end = get_datetime(update_end)

    params = {
        "key": "",
        "category": [

        ],
        "orgs": orgList,
        "level": level,
        "level_standard_category": [

        ],
        "level_standard_id": [

        ],
        "sort_by": "update_at",
        "sort": "desc",
        "list_type": "all",
        "page": 1,
        "page_size": 1000,
        "tags": [

        ],
        "appkey": "",
        "locators": "",
        "finders": "",
        "owt": "",
        "reason": [

        ],
        "duty_owt": [

        ],
        "is_contain": "包含",
        "occur_start": "",
        "occur_end": "",
        "create_start": create_start,
        "create_end": create_end,
    }
    params.update(kargs)
    url = f'{COE_API_HOST}/query/incidents'
    id_list = []
    item_dict: Dict[str, BaseCoeData] = {}
    for org in orgList:
        params['orgs'] = [org]
        res = requests.post(url=url, timeout=25, json=params, headers=headers)
        page = res.content
        responseReportJson = json.loads(page)
        for incident in responseReportJson['incidents']:
            _id = str(incident['_id'])
            update_at = get_datetime(incident['update_at'])
            if update_at < update_start or update_at > update_end:
                continue
            coe_template = incident.get('coe_template', {})
            if filter_light_template and coe_template and coe_template.get('name', '') == '轻量记录':
                continue
            item = BaseCoeData(
                coe_id=_id,
                brief=incident['brief'],
                level=incident['level']
            )
            item_dict[_id] = item
            id_list.append(_id)

    return id_list, item_dict


def getCoeAsItemDict(create_start, create_end, level, orgList=None):
    '''
    获取COE的ID列表
    按照更新期限来定
    update_start 应该是 %Y-%m-%d 10个字符
    '''
    if orgList is None:
        lion.fetch_config()
        orgList = json.loads(lion.config[f'{lion.app_name}.coe.PING_TAI_JI_SHU_BU'])
    headers = {"Authorization": "Bearer %s" % token,
               "User-Agent": agent,
               }

    params = {
        "key": "",
        "category": [

        ],
        "orgs": orgList,
        "level": level,
        "level_standard_category": [

        ],
        "level_standard_id": [

        ],
        "sort_by": "update_at",
        "sort": "desc",
        "list_type": "all",
        "page": 1,
        "page_size": 1000,
        "tags": [

        ],
        "appkey": "",
        "locators": "",
        "finders": "",
        "owt": "",
        "reason": [

        ],
        "duty_owt": [

        ],
        "is_contain": "包含",
        "occur_start": "",
        "occur_end": "",
        "create_start": create_start,
        "create_end": create_end,
    }
    url = f'{COE_API_HOST}/query/incidents'
    id_list = []
    item_dict: Dict[str, BaseCoeData] = {}
    params['orgs'] = orgList
    res = requests.post(url=url, timeout=25, json=params, headers=headers)
    page = res.content
    responseReportJson = json.loads(page)
    for incident in responseReportJson['incidents']:
        _id = str(incident['_id'])
        item = incident
        item_dict[_id] = item
        id_list.append(_id)

    return id_list, item_dict


def simple_get_coe(start, end, level=''):
    PING_TAI_JI_SHU_BU = json.loads(lion.config[f'{lion.app_name}.coe.PING_TAI_JI_SHU_BU'])
    id_list, item_dic = getId(start, end, level, PING_TAI_JI_SHU_BU)
    qing_liang, _ = getId(start, end, level, PING_TAI_JI_SHU_BU, 30)
    id_set = set(id_list) - set(qing_liang)
    id_list = list(id_set)
    return id_list, [item_dic[id] for id in id_list]


def getCoeJson(category, id):
    '''
    :param category: 要查询的文本类型，共4种，概览数据 ""，时间线 "time_lines"，原因分析 "causes"，待办任务 "improvements"
    :param id: COE文档的ID
    :return: 接口返回的json文件
    '''
    url = f'{COE_API_HOST}/incidents/{id}'
    if (len(category) > 0):
        url += '/' + category

    headers = {
        "User-Agent": agent,
        "Authorization": "Bearer %s" % token,
    }
    # print(url)
    session = requests.session()
    session.headers = headers
    # requests.utils.add_dict_to_cookiejar(session.cookies, load_cookies()) # 已废弃
    response = session.get(url)

    page = response.content
    # print(page)
    data = json.loads(page)   # 若报错page不符合json字符串形式，则需要更新cookie

    return data

# 判断COE文档是否有权限访问，无权限访问的文档在概览数据接口中的['error']不为None
# 或者来源是km_auto，这类文档的文本内容都在time_line接口的['incident']['process']中，且没有causes和improvements接口


def isAuthorized(id):
    Json = getCoeJson('', id)
    if Json['error'] is None and Json['incident']['_from'] == "COE":
        return True
    else:
        return False

# 获取基本文本


def getBriefText(id: int, scenetivity=True) -> List[CrawlerData]:
    briefJson = getCoeJson('', id)
    briefText = []

    tagList = ['occur_time', 'brief', 'appearance', 'impact_detail', 'category',
               'experience', 'correct_action', 'handle_time']  # 标题、现象、客户影响、经验教训、正确做法
    tag_desc = ['[发生时间]', '[标题]', '[现象]', '[客户影响]', '[故障类型]', '[经验教训]', '[正确做法]', '[开始处理时间]']
    # tagList = ['brief', 'appearance', 'impact_detail']
    # tag_desc = ['[标题]','[现象]','[客户影响]']
    for tag, desc in zip(tagList, tag_desc):
        if (tag not in briefJson['incident']):
            continue
        str = briefJson['incident'][tag]
        if str is None:
            continue
        if tag == 'category':
            str = CATEGORY_DICT.get(str, str)
        briefText.append(CrawlerData.get_from_text(str, desc, scenetivity))
    return briefText

# 获取时间线中的文本


def getTimeLineText(id, scenetivity=True) -> List[CrawlerData]:
    timeLineJson = getCoeJson('time_lines', id)
    timeline_list = []
    for item in timeLineJson['time_line']:
        str = item['content']
        if str is not None:
            timeline_list.append(CrawlerData.get_from_timeline(item, scenetivity))
    return timeline_list

# 获取原因分析中的文本


def getCausesText(id, scenetivity=True) -> List[CrawlerData]:
    causesJson = getCoeJson('causes', id)
    causesText = []
    for item in causesJson['causes']:
        aStr = item['answer']
        if aStr is None or len(aStr) == 0:
            continue
        causesText.append(CrawlerData.get_from_causes(item, scenetivity))
    return causesText

# 获取待办任务中的文本


def getToDoText(id) -> List[CrawlerData]:
    toDoJson = getCoeJson('improvements', id)
    todo_list = []
    if len(toDoJson['improvements']) > 0:
        for ind, item in enumerate(toDoJson['improvements']):
            brief = item['brief']
            status = item['status']
            category = item['category']
            text = f'第{ind+1}个待办事项: {brief}\n处理状态为:{status}\n类别为:{category}'
            todo_list.append(CrawlerData.get_from_text(text, '[TODO]'))
    return todo_list

# 将DataFrame保存到本地的json文件中


def save_data(data):
    now = time.strftime("%Y-%m-%d-%H_%M", time.localtime(time.time()))
    fname = "data/" + now + ".json"
    write_json(fname, data)


def generate_filename(endder):
    now = time.strftime("%Y-%m-%d-%H_%M", time.localtime(time.time()))
    fname = "data/" + now + endder
    return fname

# 根据所要查询的ID列表生成csv文件


def get_COE_info(id_list):
    data = []
    for id in id_list:
        # 可能出现没有权限访问的文档，需要跳过
        if not isAuthorized(id):
            print(str(id) + " no authorization or from km_auto")
            continue
        briefText = getBriefText(id)
        timeLineText = getTimeLineText(id)
        causesText = getCausesText(id)
        # toDoText = getToDoText(id)
        item = {
            'coe_id': id,
            'data': briefText+timeLineText+causesText+briefText,  # 需要有顺序
        }
        data.append(item)
        time.sleep(3)
    # save_data(data)
    return data


def get_COE_tag(id_list):
    data = []
    from tqdm import tqdm
    for id in tqdm(id_list):
        # if not isAuthorized(id):
        # print(str(id) + " no authorization or from km_auto")
        # continue
        try:
            tag_json = getCoeJson('custom', id)
            item = {}
            for instance in tag_json['custom']['instances']:
                key = instance['custom_template']['label']
                value = instance['value']
                item[key] = str(value)

            data.append(item)
        except Exception:
            logger.info(f'coe-{id},没有分类信息')
            data.append({})
    return data


def get_tag(coe_id):
    try:
        tag_json = getCoeJson('custom', coe_id)
        item = {}
        for instance in tag_json['custom']['instances']:
            key = instance['custom_template']['label']
            value = instance['value']
            item[key] = str(value)
        return item
    except Exception:
        logger.info(f'coe-{coe_id},没有分类信息')
        return {}


def get_template(coe_id):
    try:
        tag_json = getCoeJson('custom', coe_id)
        template = tag_json['custom']['coe_template']
        template_id = tag_json['custom']['coe_template_id']
        return template['name'], template_id
    except Exception:
        logger.info(f'coe-{coe_id},没有模板')
        return None, None


def get_COE_summary(file_name):
    js = read_json(file_name)
    data = []
    for coe in js:
        coe_id = coe['coe_id']
        summary = coe['abstract']
        answer = coe['answer']
        data.append(SummaryData(summary=summary, answer=answer, coe_id=coe_id))
    return data


def get_6to2notto(coe_id):
    causesJson = getCoeJson('causes', coe_id)
    for item in causesJson['causes']:
        if (item['custom_config'] is None):
            continue
        if (item['custom_config']['label'] not in ['六要两不要']):
            continue
        html = item['answer']
        soup = BeautifulSoup(html, 'html.parser')
        table = soup.find('table')
        data = []
        rowspans = [1, 1, 1]
        prev_row_td = [None, None, None]
        for tr in table.find_all('tr')[1:]:
            row_td = tr.find_all('td')
            if len(row_td) >= 4:
                # 有时候表头也写成td了，这样跳过第一列，取后面三列
                row_td = row_td[1:]
            inserted = [False, False, False]
            for ind in range(len(rowspans)):
                if (rowspans[ind] > 1):
                    row_td.insert(ind, prev_row_td[ind])
                    inserted[ind] = True
                    rowspans[ind] -= 1
            for ind in range(len(inserted)):
                if (not inserted[ind]):
                    rowspans[ind] = int(row_td[ind].get('rowspan', 1))
            prev_row_td = row_td
            row = [None, None, None]
            row[0] = row_td[0].text
            row[1] = row_td[1].text
            payload = row_td[2]
            img_tags = payload.find_all('img')
            imgs = []
            for img_tag in img_tags:
                origin = img_tag.get('data-origin', '')
                small = img_tag.get('data-small', '')
                src = img_tag.get('data-src', '')
                if len(origin) > 5:
                    imgs.append(origin)
                if len(small) > 5:
                    imgs.append(small)
                if len(src) > 5:
                    imgs.append(src)
            lnks = []
            for lnk in payload.find_all('a'):
                lnks.append(lnk.get('href'))
            row[2] = {
                'text': payload.text,
                'image': imgs,
                'link': lnks
            }
            data.append(row)
        return data
    return []


if __name__ == "__main__":
    tag_dict = get_tag('242930')
    print(tag_dict)
    print(tag_dict['线上问题触发条件'])
    print(tag_dict.get('变更来源系统', None))
