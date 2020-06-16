import enum
import logging

from authlib_gino.fastapi_session.api import auth
from authlib_gino.fastapi_session.models import User
from fastapi import APIRouter, HTTPException, Form, FastAPI
from starlette import status
from starlette.requests import Request

from .models import db, WeChatIdentity
from .utils import (
    MiniProgramUtil,
    NativeAppUtil,
    OpenWebUtil,
    WXWebUtil,
    WeChatAuthError,
)

log = logging.getLogger(__name__)
router = APIRouter()


class WeChatLoginType(enum.Enum):
    MINI_PROGRAM = "wxa"  # Mini Program
    NATIVE_APP = "app"  # Mobile Native App
    OPEN_WEB = "web"  # Website
    WX_WEB = "mp"  # WeChat Mini Web


WeChatLoginType.MINI_PROGRAM.idp_name = "WECHAT_WXA"
WeChatLoginType.NATIVE_APP.idp_name = "WECHAT_APP"
WeChatLoginType.OPEN_WEB.idp_name = "WECHAT_WEB"
WeChatLoginType.WX_WEB.idp_name = "WECHAT_MP"

WeChatLoginType.MINI_PROGRAM.openid_name = "wxa_openid"
WeChatLoginType.NATIVE_APP.openid_name = "app_openid"
WeChatLoginType.OPEN_WEB.openid_name = "web_openid"
WeChatLoginType.WX_WEB.openid_name = "mp_openid"

WeChatLoginType.MINI_PROGRAM.wechat_util = MiniProgramUtil
WeChatLoginType.NATIVE_APP.wechat_util = NativeAppUtil
WeChatLoginType.OPEN_WEB.wechat_util = OpenWebUtil
WeChatLoginType.WX_WEB.wechat_util = WXWebUtil


@router.post("/login/wechat")
async def login_wechat(
    request: Request, login_type: WeChatLoginType, code: str = Form(...)
):
    wechat_util = login_type.wechat_util()
    try:
        data = await wechat_util.auth(code=code)
    except WeChatAuthError as e:
        raise HTTPException(status.HTTP_403_FORBIDDEN, e.error)

    openid = data["openid"]

    async with db.transaction() as tx:
        result = await (
            WeChatIdentity.outerjoin(User)
            .select()
            .where(WeChatIdentity.sub == openid)
            .where(WeChatIdentity.idp == login_type.idp_name)
            .gino.load((WeChatIdentity, User))
            .first()
        )
        if result is None:
            user = await User.create(name=data.get("nickname"))
            await WeChatIdentity.create()
        else:
            identity, user = result

        identity_data = {
            "sub": openid,
            "idp": login_type.idp_name,
            "user_id": user.id,
            "unionid": data.get("unionid"),
            login_type.openid_name: openid,
            "session_key": data.get("session_key"),
            "refresh_token": data.get("refresh_token"),
            "nickname": data.get("nickname"),
            "headimgurl": data.get("headimgurl"),
            "sex": data.get("sex"),
        }
        await identity.update(**identity_data).apply()
        rv = await auth.create_authorization_response(request, user)
        if rv.status_code >= 400:
            tx.raise_rollback()
    return rv


def init_app(app: FastAPI):
    app.include_router(router, tags=["WeChat Login"])
