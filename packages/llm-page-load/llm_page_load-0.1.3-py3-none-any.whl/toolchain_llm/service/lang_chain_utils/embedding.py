import threading
from llmcore_sdk.embeddings.embedding import LLMEmbeddings
from langchain.embeddings import OpenAIEmbeddings
from llmcore_sdk.embeddings.m3embedding import M3Embedding
import os

os.environ["OPENAI_API_KEY"] = '1637640609647026246'
os.environ['OPENAI_API_BASE'] = 'https://aigc.sankuai.com/v1/openai/native'

embed = LLMEmbeddings()
m3embed = M3Embedding()

Env = os.getenv('Env', 'dev')
if Env != 'pord':
    m3embed.host = 'https://aiengineering.sankuai.com/bypass/embedding/embedding/m3e/moka_ai/base'

if __name__ == '__main__':
    m3embed.host = 'http://localhost:8002/bypass/embedding/embedding/m3e/moka_ai/base'
    ans = m3embed.get_embedding('text')
    print(ans)
