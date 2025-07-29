from service.lang_chain_utils.lion_client import client as lion
import configparser


def read_lion_file_config(config_name, env='test', group='default'):
    mss_client_conf_file_url = f'http://lion-api.inf.test.sankuai.com/fileconfig/env/{env}/appkey/{lion.app_name}/group/{group}/file/{config_name}/content'  # noqa
    config = configparser.ConfigParser()
    config.read_string(lion.http(mss_client_conf_file_url, method='get', headers=lion.auth(mss_client_conf_file_url)).text)
    return config
