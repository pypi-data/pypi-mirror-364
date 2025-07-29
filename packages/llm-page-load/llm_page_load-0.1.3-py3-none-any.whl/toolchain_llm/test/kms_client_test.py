from kms_sdk.kms import Kms
from kms_sdk.utils.exceptions import KmsResultNullException
from utils import appkey
name = "FRIDAY_APPID"

try:
    s = Kms.get_by_name(appkey, name)
    print(s)
except KmsResultNullException as e:
    print(e.code)
    print(e.msg)
except Exception:
    pass
