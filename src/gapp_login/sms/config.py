import string
from importlib.metadata import entry_points

from authlib_gino.fastapi_session.gino_app import load_entry_point
from starlette.config import Config
from starlette.datastructures import CommaSeparatedStrings

config: Config = load_entry_point("config", Config)


def load_sms_provider(provider_name: str):
    for ep in entry_points()["sms.provider"]:
        if ep.name == provider_name:
            return ep.load()()

    return None


SMS_SUPPORTED_PREFIX = config(
    "SMS_SUPPORTED_PREFIX", cast=CommaSeparatedStrings, default=["+86"]
)
SMS_CODE_LENGTH = config("SMS_CODE_LENGTH", cast=int, default=6)
SMS_CODE_CHARS = config("SMS_CODE_CHARS", default=string.digits)
SMS_TTL = config("SMS_TTL", cast=int, default=300)  # 5 minutes
SMS_COOL_DOWN = config("SMS_COOL_DOWN", cast=int, default=60)  # 1 minute
SMS_PROVIDER = config("SMS_PROVIDER", cast=load_sms_provider, default=None)
