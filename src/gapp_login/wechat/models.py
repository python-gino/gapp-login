from authlib_gino.fastapi_session.gino_app import load_entry_point
from authlib_gino.fastapi_session.models import Identity
from gino import Gino

db = load_entry_point("db", Gino)


class WeChatIdentity(Identity):
    wxa_openid = db.StringProperty()
    app_openid = db.StringProperty()
    web_openid = db.StringProperty()
    mp_openid = db.StringProperty()
    unionid = db.StringProperty()
    session_key = db.StringProperty()
    refresh_token = db.StringProperty()
    nickname = db.StringProperty()
    headimgurl = db.StringProperty()
    sex = db.StringProperty()
