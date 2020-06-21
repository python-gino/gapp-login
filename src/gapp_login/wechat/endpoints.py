import base64
import json
import logging
from urllib import parse

from authlib_gino.fastapi_session.api import (
    auth,
    login_context,
    require_user,
)
from authlib_gino.fastapi_session.models import User
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.padding import PKCS7
from fastapi import APIRouter, HTTPException, Form, FastAPI, Depends, Security
from starlette import status
from starlette.requests import Request

from . import config
from .models import db, WeChatIdentity
from .clients import WeChatAuthError

log = logging.getLogger(__name__)
router = APIRouter()


@router.put("/login/wechat")
async def login_wechat(
    request: Request, code: str = Form(...), ctx=Depends(login_context)
):
    idp = ctx["idp"]
    idp_params = dict(parse.parse_qsl(ctx["idp_params"]))
    appid = idp_params.get("appid")
    if not appid or appid not in config.WECHAT_CLIENTS:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Wrong wechat AppID")

    client = config.WECHAT_CLIENTS[appid]
    try:
        data = await client.request_token(code)
    except WeChatAuthError as e:
        raise HTTPException(status.HTTP_403_FORBIDDEN, e.error)

    scope = idp_params.get("scope")
    user_info = {}
    if scope in {"snsapi_userinfo", "snsapi_login"}:
        try:
            user_info = await client.get_user_info(
                access_token=data["access_token"], openid=data["openid"]
            )
        except WeChatAuthError as e:
            raise HTTPException(status.HTTP_403_FORBIDDEN, e.error)

    openid = data["openid"]
    unionid = data.get("unionid")
    async with db.transaction() as tx:
        result = await (
            WeChatIdentity.outerjoin(User)
            .select()
            .with_for_update(of=WeChatIdentity)
            .where(WeChatIdentity.sub == openid)
            .where(WeChatIdentity.idp == idp)
            .gino.load((WeChatIdentity, User))
            .first()
        )
        identity_data = dict(
            wechat_unionid=unionid,
            wechat_session_key=data.get("session_key"),
            wechat_refresh_token=data.get("refresh_token"),
            wechat_user_info=user_info,
        )
        if result is None:
            user = None
            if unionid:
                user = await (
                    User.query.select_from(WeChatIdentity.outerjoin(User))
                    .where(WeChatIdentity.wechat_unionid == unionid)
                    .where(db.func.starts_with(WeChatIdentity.idp, "WECHAT"))
                    .gino.first()
                )
            if not user:
                user = await User.create(name=user_info.get("nickname") or openid)
            await WeChatIdentity.create(
                sub=openid,
                idp=idp,
                user_id=user.id,
                wechat_app_id=appid,
                **identity_data,
            )
        else:
            identity, user = result
            await identity.update(**identity_data).apply()

        rv = await auth.create_authorization_response(request, user, ctx)
        if rv.status_code >= 400:
            tx.raise_rollback()
        rv_location = rv.headers["location"]
        if rv_location.startswith("wxa://"):
            return dict(parse.parse_qs(rv_location.split("?", 1)[1]))
    return rv


@router.post("/users/update/wxa")
async def update_wechat_account_info(
    user: User = Security(require_user),
    encrypted_data: str = Form(...),
    iv: str = Form(...),
    app_id: str = Form(...),
):
    encrypted_data = base64.b64decode(encrypted_data)
    iv = base64.b64decode(iv)
    identity = await (
        WeChatIdentity.query.select_from(User.outerjoin(WeChatIdentity))
        .where(User.id == user.id)
        .where(WeChatIdentity.wechat_app_id == app_id)
        .where(db.func.starts_with(WeChatIdentity.idp, "WECHAT"))
        .gino.first()
    )
    if not identity:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User is not found")

    wechat_session_key = identity.profile.get("wechat_session_key")
    session_key = base64.b64decode(wechat_session_key)
    decryptor = Cipher(
        algorithms.AES(session_key), modes.CBC(iv), backend=default_backend(),
    ).decryptor()
    data = decryptor.update(encrypted_data) + decryptor.finalize()
    unpadder = PKCS7(algorithms.AES.block_size).unpadder()
    data = unpadder.update(data) + unpadder.finalize()
    data = json.loads(data)
    wm = data.pop("watermark")
    if wm["appid"] != app_id:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Bad wechat AppID")

    await identity.update(wechat_user_info=data).apply()
    return dict(data=data)


def init_app(app: FastAPI):
    @app.on_event("shutdown")
    async def shutdown():
        for app_id, client in config.WECHAT_CLIENTS.items():
            log.info("Closing wechat client connection: " + app_id)
            await client.client.aclose()
            log.info("Closed wechat client  connection: " + app_id)

    app.include_router(router, tags=["WeChat Login"])
