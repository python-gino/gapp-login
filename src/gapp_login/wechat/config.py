from authlib_gino.fastapi_session.gino_app import load_entry_point
from starlette.config import Config
from starlette.datastructures import Secret

config: Config = load_entry_point("config", Config)

########################################################################################
# Mini Program
WXA_APP_ID = config("WXA_APP_ID", cast=None, default=None)
WXA_APP_SECRET = config("WXA_APP_SECRET", cast=Secret, default=None)


########################################################################################
# Mobile Native App
NATIVE_APP_ID = config("NATIVE_APP_ID", cast=None, default=None)
NATIVE_APP_SECRET = config("NATIVE_APP_SECRET", cast=Secret, default=None)


########################################################################################
# Website
OPEN_WEB_APP_ID = config("OPEN_WEB_APP_ID", cast=None, default=None)
OPEN_WEB_APP_SECRET = config("OPEN_WEB_APP_SECRET", cast=Secret, default=None)


########################################################################################
# WeChat Mini Web
WX_WEB_APP_ID = config("WX_WEB_APP_ID", cast=None, default=None)
WX_WEB_SECRET = config("WX_WEB_SECRET", cast=Secret, default=None)
