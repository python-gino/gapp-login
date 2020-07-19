from authlib_gino.fastapi_session.gino_app import load_entry_point
from starlette.config import Config


config: Config = load_entry_point("config", Config)


TENCENT_SECRET_ID = config("TENCENT_SECRET_ID", default=None)
TENCENT_SECRET_KEY = config("TENCENT_SECRET_KEY", default=None)
SMS_APP_ID = config("SMS_APP_ID", default=None)
SMS_TEMPLATE_ID = config("SMS_TEMPLATE_ID", default=None)
SMS_SIGN = config("SMS_SIGN", default=None)
