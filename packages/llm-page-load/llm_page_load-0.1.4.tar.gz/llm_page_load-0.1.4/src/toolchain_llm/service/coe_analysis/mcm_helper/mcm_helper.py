from tools.oceanus_auth import get_oceanus_auth_header
from utils import appkey
import requests
from kms_sdk.kms import Kms
from service.coe_analysis.mcm_helper.mcm_data import MCMPlan


def get_mcm_plan(plan_id, env='prod'):
    token = Kms.get_by_name(appkey, f"sankuai.cf.plan.server.{env}")
    url = f'http://mcm.tbd.test.sankuai.com/open/api/v1/cf/plan/{plan_id}'
    if env == 'prod':
        url = f'http://mcm.vip.sankuai.com/open/api/v1/cf/plan/{plan_id}'
    auth = get_oceanus_auth_header("com.sankuai.cf.plan.server", appkey, token=token)
    headers = {'Content-Type': 'application/json'}
    headers.update(auth)
    response = requests.get(url, headers=headers)
    return MCMPlan(**response.json()['data'])
