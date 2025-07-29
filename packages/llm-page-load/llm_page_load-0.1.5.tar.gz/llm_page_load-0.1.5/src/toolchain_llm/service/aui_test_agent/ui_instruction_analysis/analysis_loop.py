import json
import os
from AUITestAgent.Agent import UITestRobot, InteractionExecutor
from llmcore_sdk.models.friday import FridayVision
from service.aui_test_agent.mock_driver import MockWebDriver
from service.aui_test_agent.ui_instruction_analysis.es_storage import ExplainData, RecordedData
from service.aui_test_agent.ui_instruction_analysis.prompt import ReflectionPrompt
from utils import logger


class AnalysisLoop:
    def __init__(self, recorded_data: RecordedData, platform: str, work_dir: str):
        self.recorded_data = recorded_data
        self.previous_recorded_data = None
        if recorded_data.record_id > 0:
            self.previous_recorded_data = RecordedData.read_from_es(recorded_data.record_id-1,
                                                                    recorded_data.record_task_id)
        # 现在fridayVision默认的处理逻辑就是只支持http和本地文件，不支持dataUrl/base64编码图片，所以要先传s3
        self.driver = MockWebDriver(
            screenshot=recorded_data.target.screenshotData.content,
            xml=recorded_data.target.dom,
            device_size=[1628, 3072])
        self.UIAgent = UITestRobot(platform=platform, driver=self.driver, drive_mode=1, test_work_dir=work_dir)
        self.work_dir = work_dir
        self.loop = 3
        self.vllm = FridayVision(model='gpt-4o-2024-08-06')

    def make_explain(self, notice: str):
        event = self.recorded_data.as_dict()
        event = json.dumps(event, ensure_ascii=False)
        if self.previous_recorded_data is not None:
            basic_info_desc = ReflectionPrompt.DOUBLE_IMAGE
            prompt = ReflectionPrompt.BASIC_EXPLAIN.format(basic_desc=basic_info_desc, notice=notice, event=event)
            ans = self.vllm.complex_chat(messages=[
                {'role': 'user', 'content': '用户交互前截图',
                 'image_url': self.previous_recorded_data.target.screenshotData.content},
                {'role': 'user', 'content': '用户交互后截图',
                 'image_url': self.recorded_data.target.screenshotData.somContent},
                {'role': 'user', 'content': prompt}
            ])
        else:
            basic_info_desc = ReflectionPrompt.SINGLE_IMAGE
            prompt = ReflectionPrompt.BASIC_EXPLAIN.format(basic_desc=basic_info_desc, notice=notice, event=event)
            ans = self.vllm.complex_chat(messages=[
                {'role': 'user', 'content': prompt, 'image_url': self.recorded_data.target.screenshotData.somContent}
            ])
        return ans

    def is_action_right(self, target):
        scale = self.recorded_data.target.devicePixelRatio
        bounds = target
        rect = self.recorded_data.target.rect
        truth = [int(rect.x * scale), int(rect.y * scale),
                 int((rect.x + rect.width)*scale), int((rect.y + rect.height) * scale)]
        # bounds形式与turth一致，都是[x, y, x+width, y+height]，计算bounds与truth重合的区域面积占bounds本身面积的比重
        img_path = os.path.join(self.work_dir, 'is_action_right_img.png')
        self.interaction_executor.user_proxy.draw_rectangle(img_path=self.interaction_executor.image_path,
                                                            img_save_path=img_path, positions=bounds)
        self.interaction_executor.user_proxy.draw_rectangle(img_path=img_path,
                                                            img_save_path=img_path, positions=truth,
                                                            thickness=5)
        # 检查bounds中心点是否在truth内部
        bounds_center_x = (bounds[0] + bounds[2]) / 2
        bounds_center_y = (bounds[1] + bounds[3]) / 2
        if (truth[0] <= bounds_center_x <= truth[2] and truth[1] <= bounds_center_y <= truth[3]):
            return True

        # 计算重叠区域的边界
        overlap_left = max(bounds[0], truth[0])
        overlap_top = max(bounds[1], truth[1])
        overlap_right = min(bounds[2], truth[2])
        overlap_bottom = min(bounds[3], truth[3])
        # 如果没有重叠区域，直接返回 False
        if overlap_left >= overlap_right or overlap_top >= overlap_bottom:
            return False
        # 计算重叠区域面积
        overlap_area = (overlap_right - overlap_left) * (overlap_bottom - overlap_top)
        bounds_area = (bounds[2] - bounds[0]) * (bounds[3] - bounds[1])
        overlap_ratio = overlap_area / bounds_area
        # 判断重叠比例是否达到阈值（假设阈值为 0.25，可以根据需求调整）
        return overlap_ratio >= 0.25

    def make_reflaction(self, content):
        if self.previous_recorded_data:
            basic_info_desc = ReflectionPrompt.DOUBLE_IMAGE
            prompt = ReflectionPrompt.REFLECTION_NOTICE.format(basic_desc=basic_info_desc, content=content)
            ans = self.vllm.complex_chat(messages=[
                {'role': 'user', 'content': '用户交互前截图',
                 'image_url': self.previous_recorded_data.target.screenshotData.content},
                {'role': 'user', 'content': '用户交互后截图', 'image_url':
                 self.recorded_data.target.screenshotData.somContent},
                {'role': 'user', 'content': prompt}
            ])
        else:
            basic_info_desc = ReflectionPrompt.SINGLE_IMAGE
            prompt = ReflectionPrompt.REFLECTION_NOTICE.format(basic_desc=basic_info_desc, content=content)
            ans = self.vllm.complex_chat(messages=[
                {'role': 'user', 'content': prompt, 'image_url': self.recorded_data.target.screenshotData.somContent}
            ])
        return ans

    def run(self):
        if self.recorded_data.type in ['wheel', 'scroll', 'navigate']:
            return self.recorded_data.explain.content

        self.interaction_executor = InteractionExecutor(
            '', self.UIAgent.work_dir, self.UIAgent.driver, self.UIAgent.drive_mode, self.UIAgent.platform,
            self.UIAgent.knowledge_mode, self.UIAgent.device_name, self.UIAgent.grounding_mode)
        notice = ''  # 上一次失败的经验
        if self.previous_recorded_data:  # 优先使用交互前的截图
            self.interaction_executor.image_path = self.previous_recorded_data.target.screenshotData.content
        else:
            self.interaction_executor.image_path = self.recorded_data.target.screenshotData.content

        self.recorded_data.explain = ExplainData(None, 0, None, None) if self.recorded_data.explain is None else self.recorded_data.explain  # noqa
        for i in range(self.loop):
            # 改进一次操作计划
            self.recorded_data.explain.content = self.make_explain(notice)
            self.recorded_data.loop_version = i
            self.recorded_data.update_to_es()
            # 执行一次操作计划，获取 plan 和 action
            if i == 0:
                self.interaction_executor.observe()  # 第一次操作需要observe
            self.interaction_executor.local_task = self.recorded_data.explain.content
            self.interaction_executor.plan_and_action_list = []
            plan_and_action = self.interaction_executor.first_action_plan_action()
            self.interaction_executor.plan_and_action_list.append(plan_and_action)
            action = self.interaction_executor.select_action(plan_and_action)
            # 反思操作计划是否需要改进
            is_pass = self.is_action_right(target=action['target'])
            if is_pass:
                self.recorded_data.groundingOK = True
                self.recorded_data.update_to_es()
                break
            self.recorded_data.groundingOK = False
            if i == self.loop - 1:
                logger.info('循环终止')
                self.recorded_data.update_to_es()
                break
            notice = self.make_reflaction(self.recorded_data.explain.content)
            self.recorded_data.explain.notice = notice
            logger.info('反思过程:' + notice)
            self.recorded_data.update_to_es()
        return self.recorded_data.explain.content


if __name__ == '__main__':
    with open('service/aui_test_agent/web-record-2025-02-26T08_29_10.958Z.json') as f:
        data = json.load(f)
    recorded_data = RecordedData.from_json(data['recordedEvents'][1])
    recorded_data.target.screenshotData.save_to_s3()
    loop = AnalysisLoop(recorded_data, platform='Android')
    loop.run()
