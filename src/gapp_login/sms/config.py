import json
import importlib
import string

from authlib_gino.fastapi_session.gino_app import load_entry_point
from starlette.config import Config
from starlette.datastructures import CommaSeparatedStrings

config: Config = load_entry_point("config", Config)


def get_sms_provider(settings: str):
    """Configs used to create a SMS provider instance. Sample:
    {
        "params": {
            "secret_id": "xxx",
            "secret_key": "xxx",
            "sms_app_id": "234123",
            "sms_template_id": "123456"
            "sms_sign": "HiDay"
        },
        "type": "gapp_login.sms.provider.Tencent"
    }
    """
    settings = json.loads(settings)

    module, cls_name = settings.get("type", "").rsplit(".", 1)
    params = settings.get("params", {})

    return getattr(importlib.import_module(module), cls_name)(**params)


SMS_SUPPORTED_PREFIX = config(
    "SMS_SUPPORTED_PREFIX", cast=CommaSeparatedStrings, default=["+86"]
)
SMS_CODE_LENGTH = config("SMS_CODE_LENGTH", cast=int, default=6)
SMS_CODE_CHARS = config("SMS_CODE_CHARS", default=string.digits)
SMS_TTL = config("SMS_TTL", cast=int, default=300)  # 5 minutes
SMS_COOL_DOWN = config("SMS_COOL_DOWN", cast=int, default=60)  # 1 minute
SMS_PROVIDER = config("SMS_PROVIDER", cast=get_sms_provider, default=None)
