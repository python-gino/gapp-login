from authlib_gino.fastapi_session.gino_app import load_entry_point
from authlib_gino.fastapi_session.models import Identity
from gino import Gino

db = load_entry_point("db", Gino)


class WeChatIdentity(Identity):
    wechat_unionid = db.StringProperty()
    wechat_session_key = db.StringProperty()
    wechat_refresh_token = db.StringProperty()
    wechat_user_info = db.ObjectProperty()

    @db.declared_attr
    def wechat_unionid_idx(cls):
        return db.Index(
            "identities_wechat_unionid_idx",
            cls.wechat_unionid,
            postgresql_where=(db.func.starts_with(cls.idp, "WECHAT")),
        )
