from tiktoken.core import Encoding
from tiktoken.load import load_tiktoken_bpe
from tiktoken_ext.openai_public import ENDOFPROMPT,ENDOFTEXT,FIM_MIDDLE,FIM_PREFIX,FIM_SUFFIX
import tiktoken

def cl100k_base():
    mergeable_ranks = load_tiktoken_bpe(
        'token_count/cl100k_base.tiktoken'
    )
    special_tokens = {
        ENDOFTEXT: 100257,
        FIM_PREFIX: 100258,
        FIM_MIDDLE: 100259,
        FIM_SUFFIX: 100260,
        ENDOFPROMPT: 100276,
    }
    return {
        "name": "cl100k_base",
        "pat_str": r"""(?i:'s|'t|'re|'ve|'m|'ll|'d)|[^\r\n\p{L}\p{N}]?\p{L}+|\p{N}{1,3}| ?[^\s\p{L}\p{N}]+[\r\n]*|\s*[\r\n]+|\s+(?!\S)|\s+""",
        "mergeable_ranks": mergeable_ranks,
        "special_tokens": special_tokens,
    }

encoding = Encoding(**cl100k_base())
tiktoken.registry.ENCODINGS['cl100k_base'] = encoding  # 强行注册 cl100k_base ，llmcore-sdk的tiktoken都会用我们初始化的encoding

def count_token(text:str)->int:
    return len(encoding.encode(text))