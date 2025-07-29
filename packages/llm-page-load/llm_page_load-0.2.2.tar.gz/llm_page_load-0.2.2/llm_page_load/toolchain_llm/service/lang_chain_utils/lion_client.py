# -*- coding: utf-8 -*-

import hashlib
import hmac
import json
import re
from base64 import encodebytes
from datetime import datetime
from urllib.parse import urlparse
from kms_sdk.kms import Kms
from utils import appkey
import requests
from langchain import PromptTemplate
LLM_COE_LION_PREFIX = f'{appkey}.llm.coe.prompt_template'


def date_handler(obj):
    if isinstance(obj, datetime):
        return str(obj)


class Lion:
    """
        client_id:      从lion那边申请到的ba id
        client_secret:  从lion那边申请到的ba token
        env:            环境[dev,test,ppe,staging,prod]
        app_name:       项目名
    """

    def __init__(self, client_id, client_secret, env, app_name):
        self.client_id = str(client_id)
        self.client_secret = str(client_secret)
        self.env = env
        self.app_name = app_name
        self.config = dict()
        self.fetch_config()

    def fetch_config(self):
        lion_api = self.gen_url(self.env, self.app_name)

        self.config = self.http(lion_api, headers=self.auth(lion_api)).json().get('result')

    @staticmethod
    def http(url, method='get', **kwargs):
        request_param = dict(
            headers=kwargs.get('headers', {}),
            cookies=kwargs.get('cookie', {}),
            timeout=kwargs.get('timeout', 30)
        )

        if method in ['post', 'put', 'delete']:
            if kwargs.get('json'):
                result = getattr(requests, method)(url, json=kwargs.get('json'), **request_param)
            elif kwargs.get('data'):
                result = getattr(requests, method)(url, data=kwargs.get('data'), **request_param)
            else:
                result = getattr(requests, method)(url, **request_param)
        else:
            result = requests.get(url, **request_param)

        return result

    def auth(self, url, method='GET'):

        gmt_time = datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')

        string2sign = "%s %s\n%s" % (method, urlparse(url).path, gmt_time)

        signature = encodebytes(
            hmac.new(bytes(self.client_secret, 'utf-8'), string2sign.encode('utf-8'), hashlib.sha1).digest()).replace(
            b"\n", b"")

        return dict(Date=gmt_time, Authorization="MWS " + self.client_id + ":" + signature.decode('utf-8'))

    @staticmethod
    def gen_url(env, appname):
        if env.lower() in ('prod', 'product', 'staging'):
            api = 'http://lion.vip.sankuai.com/config2/get?env={0}&prefix={1}'
        else:
            api = 'http://lion-api.inf.test.sankuai.com/config2/get?env={0}&prefix={1}'

        return api.format(env, appname)

    @staticmethod
    def beauty_json(data):

        return json.dumps(data, indent=4, default=date_handler)

    def get_prompt(self, type: str, template: str):
        pattern = r'\{([a-zA-Z_]+)\}'
        text = self.config[f'{LLM_COE_LION_PREFIX}.{type}.{template}']
        variables = re.findall(pattern, text)
        return PromptTemplate(template=text, input_variables=variables)


client_id = 'llm_test'
client_secret =  Kms.get_by_name(appkey, 'LION_CLIENT_SECRET')
client = Lion(client_id, client_secret, 'test', appkey)
# 待剩余test环境的lion配置迁移到线上，修改这里环境入参的写法
client_prod = Lion(client_id, client_secret, 'prod', appkey)


def main():
    print(client.get_prompt(type='6to2not_classifier', template='summary_next'))


def write_config(appkey: str, group: str, env: str, configs):
    if env.lower() in ('prod', 'product', 'staging'):
        api = f'http://lion.vip.sankuai.com/v3/configs/envs/{env}/appkeys/{appkey}/key'
    else:
        api = f'http://lion-api.inf.test.sankuai.com/v3/configs/envs/{env}/appkeys/{appkey}/key'
    valid_fields = ['key', 'env', 'set', 'group', 'swimlane', 'grouptags',
                    'region', 'desc', 'value', 'rank']
    for config in configs:
        config['key'] = config['name']
        config = {k: v for k, v in config.items() if k in valid_fields}
        result = client.http(api, method='post', json=config,
                             headers=client.auth(api, method='POST')).json().get('result')
        print(result)


def read_config(appkey: str, env: str, group: str):
    if env.lower() in ('prod', 'product', 'staging'):
        api = f'http://lion.vip.sankuai.com/v3/configs/appkeys/{appkey}/keyDetail'
    else:
        api = f'http://lion-api.inf.test.sankuai.com/v3/configs/appkeys/{appkey}/keyDetail'
    data = {
        "env": env,
        "group": group,
        "pageNum": 1,
        "pageSize": 100,
    }
    ans = client.http(api, method='post', json=data, headers=client.auth(api, method="POST")).json()['result']['datas']
    print(ans)
    return ans


if __name__ == '__main__':
    main()
