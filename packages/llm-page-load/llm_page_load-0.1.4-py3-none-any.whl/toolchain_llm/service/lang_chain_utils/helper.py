from langchain import LLMChain
from langchain.schema.messages import HumanMessage, SystemMessage, AIMessage, BaseMessage
from llmcore_sdk.models.friday import Friday
from service.coe_analysis.runners.retriver import LLMCallback
from typing import List
from langchain.schema import LLMResult, Generation


def make_dict_message(msgs: List[BaseMessage]):
    messages = []
    for m in msgs:
        if isinstance(m, HumanMessage):
            role = 'user'
        elif isinstance(m, AIMessage):
            role = 'assistant'
        elif isinstance(m, SystemMessage):
            role = 'system'
        messages.append({
            'role': role, 'content': m.content
        })
    return messages


def friday_chat(model: Friday, messages: List[BaseMessage], callback: LLMCallback):
    callback.on_chat_model_start(serialized={}, messages=[messages], run_id=None)
    ans = model.complex_chat(make_dict_message(messages))
    result = LLMResult(generations=[[Generation(text=ans)]])
    callback.on_llm_end(result, run_id=None)
    return ans


class FridayChain(LLMChain):
    def predict(self, callbacks, **kargs):
        prompts, stop = self.prep_prompts([kargs])
        prompts = [i.to_messages() for i in prompts]
        prompt = prompts[0]
        return friday_chat(model=self.llm, messages=prompt, callback=callbacks[0])
