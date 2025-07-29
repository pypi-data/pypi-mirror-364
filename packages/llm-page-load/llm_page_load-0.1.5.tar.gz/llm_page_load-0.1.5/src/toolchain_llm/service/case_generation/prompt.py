class Prompt:    
    @classmethod
    def get_single_image_case_generation_prompt(cls, checklist: str) -> str:
        return f"""
你是一个专业的前端测试工程师，我会给你一张截图和对应的相关需要进行前端检查的checklist。请你基于checklist和截图的页面特征生成测试用例。

<checklist>
{checklist}
</checklist>

请按照以下格式返回,返回一个python json.loads能够解析的结构：
{{
    "cases": [
        {{
            "case_name": "测试用例名称",
            "case_urlscheme": "",
            "case_info": "交互任务：交互动作描述。校验任务：验证目标和标准描述。"
        }},
        ...
    ]
}}

注意：
- 1.确保每个测试用例严格对应于checklist中的检查点，并确保覆盖所有测试点。
- 2.测试用例应基于checklist的规则而不是截图中的具体数据。
- 3.确保交互任务和校验任务的区分清晰，交互相关内容只能放在交互任务部分。
- 5.涉及到交互检查的检查点，不要将多个交互-检查放到一个case中，要分开执行，不然会错乱。
- 4.只回复cases，不要回复其他内容。
        """
        
    @classmethod
    def set_user_prompt(cls, prompt):
        cls.user_prompt = prompt
        
    @classmethod
    def set_assistant_prompt(cls, prompt):
        cls.assistant_prompt = prompt
        
    @classmethod
    def get_system_prompt(cls):
        return cls.system_prompt
        
    @classmethod
    def get_user_prompt(cls):
        return cls.user_prompt
        
    @classmethod
    def get_assistant_prompt(cls):
        return cls.assistant_prompt
        
    @classmethod
    def get_all_prompts(cls):
        return {
            "system": cls.system_prompt,
            "user": cls.user_prompt,
            "assistant": cls.assistant_prompt
        }
