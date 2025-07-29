from langchain import LLMChain, PromptTemplate
from llmcore_sdk.models.chatglm import ChatGLM
from llmcore_sdk.models.claude import Claude
from service.coe_analysis.config_reader import OPENAI_API_KEY, get_kms, OPENAI_API_BASE
from service.coe_analysis.data_structure import COEResult
from service.lang_chain_utils.lion_client import client as lion
from service.coe_analysis.runners.retriver import LLMCallback2, get_prompt
from langchain.chat_models import ChatOpenAI
from utils import GPT35NAME, GPT4NAME


def test_llm(llm):
    callback = LLMCallback2(COEResult(['1'], '1', '1', '1', '1', ''), '1')
    # llm = ChatOpenAI(model_name=GPT35NAME,
    #                  openai_api_base=OPENAI_API_BASE,
    #                  openai_api_key=OPENAI_API_KEY)
    lion.fetch_config()
    question = PromptTemplate.from_template('{text}')
    chain = LLMChain(verbose=True, prompt=question, llm=llm)
    ans = chain.predict(callbacks=[callback], text='你好')
    print(ans)
    # glm(question.format(text=''), callbacks=[callback])


if __name__ == '__main__':
    llm = ChatOpenAI(model_name=GPT4NAME,
                     openai_api_base=OPENAI_API_BASE,
                     openai_api_key=OPENAI_API_KEY,
                     request_timeout=120,
                     max_retries=6)
    test_llm(llm)
    # auth_token = get_kms('FRIDAY_APPID')
    # glm = ChatGLM(temperature=0.01, verbose=True)
    # claude = Claude(auth_token=auth_token, model='anthropic.claude-v2', temperature=0.01, verbose=True)
    # test_llm(claude)
    # test_llm(glm)
