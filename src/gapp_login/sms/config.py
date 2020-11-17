import string

from authlib_gino.fastapi_session.gino_app import load_entry_point
from starlette.config import Config
from starlette.datastructures import CommaSeparatedStrings

config: Config = load_entry_point("config", Config)

DEBUG = config("DEBUG", cast=bool, default=True)
SMS_SUPPORTED_PREFIX = config(
    "SMS_SUPPORTED_PREFIX", cast=CommaSeparatedStrings, default=["+86"]
)
SMS_CODE_LENGTH = config("SMS_CODE_LENGTH", cast=int, default=6)
SMS_CODE_CHARS = config("SMS_CODE_CHARS", default=string.digits)
SMS_TTL = config("SMS_TTL", cast=int, default=300)  # 5 minutes
SMS_COOL_DOWN = config("SMS_COOL_DOWN", cast=int, default=60)  # 1 minute
SMS_PROVIDER = config("SMS_PROVIDER", default=None)
SMS_APP_ID = config("SMS_APP_ID", default=None)
SMS_TEMPLATE_ID = config("SMS_TEMPLATE_ID", default=None)
SMS_SIGN = config("SMS_SIGN", default=None)
SMS_DEMO_CODE = config("SMS_DEMO_CODE", default="888888")
SMS_DEMO_ACCOUNTS = config("SMS_DEMO_ACCOUNTS", cast=CommaSeparatedStrings, default=[])
