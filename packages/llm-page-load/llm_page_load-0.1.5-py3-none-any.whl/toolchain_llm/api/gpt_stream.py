import json
from flask import request, Response, jsonify
from flask import Blueprint
import time
import openai
import requests
from service.coe_analysis.config_reader import friday_client_id, friday_client_secret
from llmcore_sdk.models.friday import Friday

gpt_stream = Blueprint('gpt_stream', __name__)

cache = {}


def get_token(key='friday_token', timeout=3600):
    if key in cache:
        data, timestamp = cache[key]
        if time.time() - timestamp < timeout:
            return data
    return None


def set_token(key='friday_token'):
    url = 'https://auth-ai.vip.sankuai.com/oauth/v2/token'
    payload = {
        'grant_type': 'client_credentials',
        'client_id': friday_client_id,
        'client_secret': friday_client_secret
    }
    res = requests.request('POST', url=url, data=payload)
    res = json.loads(res.text)
    if res['errcode'] == 0:
        value = res['data']['access_token']
    else:
        value = res['errmsg']
    cache[key] = (value, time.time())


@gpt_stream.route('', methods=['POST'])
def get_gpt_response():
    user_query = request.json.get('user_query')
    model = request.json.get('model', 'gpt-4o-mini')
    temperature = request.json.get('temperature', 0.1)
    business = request.json.get('business', '')
    assert len(business) > 0
    messages = [{
        'role': 'user',
        'content': user_query
    }]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        stream=True,
        temperature=temperature,
        timeout=20
    )
    friday = Friday(model=model, direction=business)
    start_time = time.time()

    def generate():
        for chunk in response:
            if chunk['lastOne']:
                friday._calculate_cost_(model, chunk, start_time)
            if 'choices' in chunk:
                yield chunk['choices'][0].delta.get("content", '')

    return Response(generate(), mimetype="text/event-stream")


@gpt_stream.route('/friday_token', methods=['GET'])
def get_friday_token():
    token = get_token()
    if not token:
        set_token()
        token = get_token()
    return jsonify({'token': token})
