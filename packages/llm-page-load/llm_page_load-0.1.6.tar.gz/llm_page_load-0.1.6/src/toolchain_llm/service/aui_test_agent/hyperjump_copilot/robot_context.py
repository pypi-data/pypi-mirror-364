import os
from AUITestAgent import UITestRobot
from AUITestAgent.utils.PageEmbed import PageEmbed
from AUITestAgent.config.config import update_config
import shutil
from datetime import datetime


class NoEsRobot(UITestRobot):
    def __init__(self, platform="Android", drive_mode=0, driver=None,
                 root_dir="./logs", test_work_dir=None, single_step_image_path=None,
                 single_step_xml_path=None, llm_model="gpt-4o", business_config=None,
                 knowledge_mode=0, device_name="HUAWEIMATE40PRO", business="default",
                 grounding_mode=0):
        update_config(llm_model, business_config)
        self.platform = platform
        self.drive_mode = drive_mode

        # 确定当前driver
        self.driver = driver
        self.root_dir = root_dir

        # 单步交互决策使用
        self.wait_time = 5  # 默认值与父类相同
        self.max_interaction_num = 30  # 默认值与父类相同
        self.swipe_time = 2200  # 默认值与父类相同
        self.task_composer = None
        self.interaction_executor = None
        self.oracle_checker = None
        self.knowledge_manager = None
        self.page_embedding = PageEmbed()
        self.single_step_image_path = single_step_image_path
        self.single_step_xml_path = single_step_xml_path
        self.grounding_mode = grounding_mode

        # 如果work_dir存在，则直接使用work_dir
        # 如果work_dir不存在，则根据root_dir和timestamp生成work_dir
        if test_work_dir is None:
            time_name = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            self.work_dir = os.path.join(self.root_dir, time_name)
            os.makedirs(self.work_dir, exist_ok=True)
        else:
            self.work_dir = test_work_dir

        # 是否调用knowledge
        self.knowledge_mode = knowledge_mode

        # 当前设备名称
        self.device_name = device_name


class UITestRobotContextManager:
    def __init__(self, test_work_dir, drive_mode, driver):
        self.robot = NoEsRobot(
            test_work_dir=test_work_dir,
            drive_mode=drive_mode,
            driver=driver
        )
        self.work_dir = test_work_dir

    def __enter__(self):
        return self.robot

    def __exit__(self, exc_type, exc_val, exc_tb):
        # 删除 work_dir
        shutil.rmtree(self.work_dir, ignore_errors=True)
