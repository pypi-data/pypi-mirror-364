from kms_sdk.kms import Kms
import json
import base64
import hashlib
import hmac
import time


def get_oceanus_auth_header(server_appkey, client_appkey, token=None):
    s1_json = {
        "algo": "0001",
        "type": "patriot",
        "time": str(round(time.time() * 1000))
    }
    s2_json = {
        "ns": client_appkey,
        "name": server_appkey
    }
    s1 = base64.b64encode(json.dumps(s1_json).encode()).decode()
    s2 = base64.b64encode(json.dumps(s2_json).encode()).decode()

    token = token or json.loads(Kms.get_by_name(client_appkey, "auth_client_" + server_appkey))[0]
    secret = hmac.new(token.encode(), s2.encode(), hashlib.sha1).hexdigest().upper()

    return {
        'oceanus-auth': f'{s1}.{s2}.{secret}'
    }

