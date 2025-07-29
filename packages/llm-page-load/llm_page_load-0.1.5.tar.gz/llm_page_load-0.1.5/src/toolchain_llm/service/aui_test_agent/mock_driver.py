import shutil
from typing import Dict, Tuple, Union
from AUITestAgent.utils.driver.abc_driver import ABCDriver
import requests
import os
import uuid
from datetime import datetime
from AUITestAgent.config.config import env_config
from mssapi.s3.connection import S3Connection
import base64
from io import BytesIO


DEV_SIZE_TYPE = Union[Tuple[int, int], Tuple[None, None]]


def upload_image(image_base64_url: str):
    """上传图片到S3"""
    def save_to_mss(image_base64_url: str, target_name, uid):
        # 移除 Base64 前缀
        if image_base64_url.startswith("data:image"):
            image_base64_url = image_base64_url.split(",", 1)[1]
        elif image_base64_url.startswith('http'):
            return image_base64_url
        else:
            raise Exception('传图片的时候必须是以 data:image 开头的 base64 字符串')
        binary_data = base64.b64decode(image_base64_url)
        file_obj = BytesIO(binary_data)
        target = target_name
        f0 = bucket.new_key(target)
        f0.set_contents_from_file(
            file_obj, headers={'Content-Type': 'image/png'})
        url_prefix = endpoint.replace('vip.', '') + '/v1/' + uid
        resource_url = f'http://{url_prefix}/vision-image/{target_name}'
        print(f"The current image is: {resource_url}")
        return resource_url

    time_stamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    s3_config = env_config['s3_config']
    endpoint, user_id, AK, SK = s3_config['endpoint'], s3_config['user_id'], s3_config['AK'], s3_config['SK']

    conn = S3Connection(
        aws_access_key_id=AK,
        aws_secret_access_key=SK,
        is_secure=False,
        host=endpoint)

    bucket = conn.get_bucket('vision-image')
    name = uuid.uuid1().__str__()
    target_name = save_to_mss(
        image_base64_url, f'agent_online/{time_stamp}/{name}.png', user_id)
    return target_name


def save_to_local(image_base64_url: str, image_save_path: str):
    # 移除 Base64 前缀
    if image_base64_url.startswith("data:image"):
        image_base64_url = image_base64_url.split(",", 1)[1]
    elif image_base64_url.startswith('http'):
        return image_base64_url
    else:
        raise Exception('传图片的时候必须是以 data:image 开头的 base64 字符串')
    binary_data = base64.b64decode(image_base64_url)
    # 确保目标路径的父目录存在
    os.makedirs(os.path.dirname(image_save_path), exist_ok=True)
    # 将解码后的数据写入本地文件
    with open(image_save_path, 'wb') as file:
        file.write(binary_data)
    print(f"Image saved to: {image_save_path}")
    return image_save_path


class MockWebDriver(ABCDriver):
    """这个类用于模拟driver，但是我们只需要截图，而且不需要进行操作"""
    @staticmethod
    def download_image(url: str, save_path: str) -> None:
        """
        从HTTP URL下载图片到本地
        """
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            with open(save_path, 'wb') as file:
                for chunk in response.iter_content(1024):
                    file.write(chunk)
        else:
            raise Exception(f"Failed to download image from {url}, status code: {response.status_code}")

    def __init__(self, device_size: DEV_SIZE_TYPE = [1280, 720], screenshot: str = '', xml: dict = {}):
        super().__init__()
        self.device_size = device_size
        self.screenshot_path = screenshot
        self.xml = xml

    def get_device_size(self) -> Union[Tuple[int, int], Tuple[None, None]]:
        """获取屏幕尺寸"""
        return self.device_size

    def screenshot(self, save_path: str) -> str:
        """把截图保存到对应位置"""
        if len(self.screenshot_path) == 0:
            return
        # 确保父目录存在
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        if self.screenshot_path.startswith('http'):
            # 如果是 http 类型的地址，那么默认下载后保存图片
            self.download_image(self.screenshot_path, save_path)
        elif self.screenshot_path.startswith('data:image'):
            save_to_local(self.screenshot_path, save_path)
        else:
            # 如果是本地的图片，那么把图片复制到save_path
            shutil.copy(self.screenshot_path, save_path)

    def to_init_page(self):
        pass

    def get_xml(self, save_path: str) -> Dict:
        """获取xml"""
        return self.xml

    def go_back(self) -> Dict:
        """不实现返回"""
        pass

    def click(self, x: int, y: int) -> Dict:
        """不实现点击"""
        pass

    def long_click(self, x: int, y: int) -> Dict:
        """不实现长按"""
        pass

    def scroll(self, x1: int, y1: int, x2: int, y2: int, duration: int = 500) -> Dict:
        """不实现滑动操作"""
        pass

    def type(self, x: int, y: int, text: str) -> Dict:
        """不实现输入操作"""
        pass
