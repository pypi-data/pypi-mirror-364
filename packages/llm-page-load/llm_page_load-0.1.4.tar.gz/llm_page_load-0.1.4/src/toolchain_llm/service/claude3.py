from llmcore_sdk.models import Friday


def claude_completion(message, system='', model="anthropic.claude-3-haiku", temperature=0.1, max_tokens=1024):
    friday = Friday(model, max_tokens, temperature=temperature, system=system, direction='LLMAPP')
    return friday(message)


def _test_():
    messages = [{'role': "user", 'content': "你好"}]
    ans = claude_completion(messages)
    print(ans)


if __name__ == '__main__':
    _test_()
