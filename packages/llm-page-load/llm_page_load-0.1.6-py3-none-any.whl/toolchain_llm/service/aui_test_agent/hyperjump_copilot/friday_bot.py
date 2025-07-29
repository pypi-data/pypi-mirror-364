import requests
import json
from utils import logger


class FridayBot:
    def __init__(self, user_login='jinhailiang'):
        self.friday_token = ''
        self.user_query = ''
        self.chat_bot_messages = []
        self.bot_typing = False
        self.stop_generating = False
        self.user_login = user_login

    def get_friday_token(self):
        try:
            response = requests.get("https://aiengineering.sankuai.com/gpt_stream/friday_token")
            response.raise_for_status()
            self.friday_token = response.json().get('token', '')
        except requests.RequestException as error:
            logger.error(f"Error fetching Friday token: {error}", error)

    def bot_send_message(self, value):
        self.user_query = value
        self.chat_bot_messages.append({
            'agent': 'user',
            'type': 'text',
            'text': self.user_query
        })
        self.bot_typing = True
        query_prompt = self.user_query

        headers = {'Content-Type': 'application/json'}
        body = {
            'appId': '1677275525413957683',
            'userId': self.user_login,
            'userType': 'MIS',
            'utterances': [query_prompt],
            'stream': True,
            'accessToken': self.friday_token
        }

        try:
            response = requests.post(
                'https://aigc.sankuai.com/conversation/v2/openapi',
                headers=headers,
                data=json.dumps(body),
                stream=True
            )
            response.raise_for_status()

            text_show = ''
            for line in response.iter_lines():
                if self.stop_generating:
                    break
                if line:
                    res_text = line.decode('utf-8')
                    if res_text.startswith('data:'):
                        res_text = res_text[5:]
                    if len(res_text) > 2:
                        res_obj = json.loads(res_text)
                        content_text = ''
                        for content in res_obj['data']['contents']:
                            if content['type'] == 'TEXT' and content['text'] != '[DONE]':
                                content_text += content['text']
                            if content['type'] == 'LINK':
                                content_text += content['href']
                        if content_text:
                            text_show = content_text

            if self.chat_bot_messages[-1]['agent'] == 'user' and text_show:
                self.bot_typing = False
                self.chat_bot_messages.append({
                    'agent': 'bot',
                    'type': 'text',
                    'text': text_show,
                    'disableInput': True
                })
            else:
                self.chat_bot_messages[-1]['text'] = text_show

            logger.info('chat completion')
            self.chat_bot_messages[-1]['disableInput'] = False
        except requests.RequestException as error:
            logger.error(f"Error during bot message sending: {error}", error)
