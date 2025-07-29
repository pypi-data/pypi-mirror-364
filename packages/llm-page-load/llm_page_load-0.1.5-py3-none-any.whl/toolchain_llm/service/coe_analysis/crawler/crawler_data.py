from dataclasses import dataclass,asdict
from typing import *
import re
from service.coe_analysis.crawler.abstract_data import AbstractData
from service.coe_analysis.crawler.ocr_api import get_ocr
from scenetivity.replacer import replace

# 用于替换 HTML 标签中的 style 属性
def replaceStyle(content):
    if content is None or len(content) == 0:
        return content
    regEx = " style=\"(.*?)\""
    p = re.compile(regEx)
    content = p.sub("", content)
    return content

# 将html文本中的所有标签的属性都去掉
def remove_html_attrs(html):
    # 匹配HTML标签中的属性
    pattern = re.compile(r'<[^>]+?(\s+[\w-]+(?:=[\'"].*?[\'"])*)+>')
    # 将匹配到的属性替换为空字符串
    return pattern.sub(lambda m: re.sub(r'\s+[\w-]+(?:=[\'"].*?[\'"])', '', m.group(0)), html)

# 获取<img>标签中的图像链接
def extract_img_urls(html):
    # 匹配HTML中的img标签
    pattern = re.compile(r'<img.*?src=[\'"](.*?)[\'"].*?>')
    # 提取img标签中的src属性值（即图像链接）
    return pattern.findall(html)

# 获取<a>标签中的url
def extract_links(html):
    # 匹配HTML中的a标签
    pattern = re.compile(r'<a.*?href=[\'"](.*?)[\'"].*?>')
    # 提取a标签中的href属性值（即URL）
    return pattern.findall(html)

# 去除json文本中的html标签
def removeHtml(str):
    return re.sub('<[^<]+?>', '', str).replace('\n', '').strip()

# 移除换行<br/>
def removeBrTag(content):
    if content is None or len(content) == 0:
        return content

    content = str(content).replace("<br/>", "")
    return content


def format_text(text, scenetivity=True):
    text = remove_html_attrs(text)
    if scenetivity:
        text = replace(text)
    return text


@dataclass(order=True)
class CrawlerData(AbstractData):
    data : str = None
    image_list : List[str] = None
    link_list : List[str] = None
    desc : str = None
    category:str = None
    time_stamp:str = None

    @classmethod
    def get_from_text(cls,html,desc, scenetivity=True):
        obj = cls()
        obj.link_list = extract_links(html)
        obj.image_list = extract_img_urls(html)
        obj.data = format_text(html, scenetivity)
        obj.desc = desc
        return obj
    
    @classmethod
    def get_from_timeline(cls,timeline, scenetivity=True):
        html = timeline['content']
        time_stamp = timeline['time']
        key = timeline['key']
        obj = cls()
        obj.link_list = extract_links(html)
        obj.image_list = extract_img_urls(html)
        obj.data = f'{time_stamp}\n{format_text(html,scenetivity)}'
        obj.desc = '[时间线信息]'
        obj.category = key
        obj.time_stamp = time_stamp
        return obj

    @classmethod
    def get_from_causes(cls,cause, scenetivity=True):
        question = cause['question']
        answer = cause['answer']
        create_at = cause['create_at']
        update_at = cause['update_at']
        contributors_show = cause['contributors_show']
        last_modified = cause['last_modified']
        answer_person = last_modified
        if contributors_show:
            for man in contributors_show:
                id, name = man.split('/')
                if last_modified == id:
                    answer_person = name
        if scenetivity:
            answer_person = replace(answer_person)
        category = cause['category']
        obj = cls()
        obj.link_list = extract_links(question)+extract_links(answer)
        obj.image_list = extract_img_urls(question) + extract_img_urls(answer)
        obj.data = f'提问:\n{format_text(question,scenetivity)}\n「{answer_person}」的回答:\n{format_text(answer,scenetivity)}'
        obj.category = category
        if ('是否违反“六要两不要”' in obj.data):
            obj.desc = '[六要两不要分析]'
        else:
            obj.desc = '[原因分析信息]'
        return obj

    def get_text(self):
        imgtxt = None
        # if(self.image_list and len(self.image_list)!=0):
        #     imgtxt = '截图文本如下:\n'
        #     for url in self.image_list:
        #         try:
        #             ocr = get_ocr(url)['data']['roi_text']
        #             ocr_text = []
        #             for item in ocr[:5]:
        #                 ocr_text.append(item['text'])
        #             imgtxt+=f'{ocr_text}\n'
        #         except:
        #             pass
        if (self.category):
            txt = f'{self.desc}\t[{self.category}]\n{self.data}\n'
        else:
            txt = f'{self.desc}\n{self.data}\n'
        if (imgtxt):
            txt = txt + imgtxt
        return txt + '\n'

    def __dict__(self):
        return asdict(self)
