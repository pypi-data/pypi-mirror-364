import requests
CLIENT_COMMON_API = 'http://clientcommon.hotel.test.sankuai.com'


def send_dx_message(group: str, message: str):
    url = CLIENT_COMMON_API + f'/client/message/group/{group}'
    params = {'message': message}
    resp = requests.post(url, json=params)
    if not resp.status_code == 200:
        raise Exception(f'发送大象消息失败 {resp.text}')
    return


def send_dx_message_to_person(mis: str, message: str):
    url = CLIENT_COMMON_API + f'/client/message/person/{mis}'
    params = {'message': message}
    resp = requests.post(url, json=params, timeout=30)
    if not resp.status_code == 200:
        raise Exception(f'发送大象消息失败 {resp.text}')
    return
