from mssapi.s3.connection import S3Connection
from src.toolchain_llm.service.coe_analysis.config_reader import llmapp_s3_access_key, llmapp_s3_s_key
from src.toolchain_llm.service.lang_chain_utils.lion_client import client as lion
import os


class MssHHelper:
    def __init__(self):
        self.user_id = lion.config.get(f'{lion.app_name}.s3_appid', '')
        self.endpoint = 's3plus.vip.sankuai.com'
        self.conn = S3Connection(
            aws_access_key_id=llmapp_s3_access_key,
            aws_secret_access_key=llmapp_s3_s_key,
            is_secure=False,
            host=self.endpoint)

        self.bucket = self.conn.get_bucket('compatibility')

    def save_to_mss(self, file_name, target_name=None, headers=None):
        if os.path.exists(file_name):
            target = target_name if target_name else file_name
            f0 = self.bucket.new_key(target)
            f0.set_contents_from_filename(file_name, headers)
            url_prefix = self.endpoint.replace('vip.', '')+'/v1/'+self.user_id
            resource_url = f'http://{url_prefix}/compatibility/{target_name}'
            return resource_url
        else:
            return False

    def download_from_mss(self, source, target):
        k0 = self.bucket.get_key(source)
        k0.get_contents_to_filename(target)


if __name__ == '__main__':
    client = MssHHelper()
    client.download_from_mss('agent_test/explore.png', 'test/data/explore.png')
