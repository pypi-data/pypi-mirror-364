from mssapi.s3.connection import S3Connection
import os
from service.file_config_reader import read_lion_file_config
from service.coe_analysis.config_reader import llmapp_s3_access_key, llmapp_s3_s_key

config = read_lion_file_config('mss_client.conf')
MACHINE_ENV = os.environ.get('Env', 'test')


class MssHHelper:
    def __init__(self):
        self.user_id = config['default']['user_id']
        self.endpoint = config['default']['Endpoint_Online'] if MACHINE_ENV == 'prod' else config['default']['Endpoint']
        self.conn = S3Connection(
            aws_access_key_id=llmapp_s3_access_key,
            aws_secret_access_key=llmapp_s3_s_key,
            is_secure=False,
            host=self.endpoint)

        self.bucket = self.conn.get_bucket(config['default']['Bucket'])

    def save_to_mss(self, file_name, target_name=None, headers=None):
        if os.path.exists(file_name):
            target = target_name if target_name else file_name
            f0 = self.bucket.new_key(target)
            f0.set_contents_from_filename(file_name, headers)
            url_prefix = self.endpoint.replace('vip.', '')+'/v1/'+self.user_id
            bucket = config['default']['Bucket']
            resource_url = f'http://{url_prefix}/{bucket}/{target_name}'
            return resource_url
        else:
            return False

    def download_from_mss(self, source, target):
        k0 = self.bucket.get_key(source)
        k0.get_contents_to_filename(target)


s3_client = MssHHelper()
