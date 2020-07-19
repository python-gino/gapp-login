from __future__ import annotations

import logging
import time
from importlib.metadata import entry_points
from typing import Optional

import httpx
from authlib.common.security import generate_token
from authlib_gino.fastapi_session.api import auth, login_context
from authlib_gino.fastapi_session.models import User
from fastapi import APIRouter, HTTPException, Form, FastAPI, Depends
from starlette import status
from starlette.requests import Request

from . import config
from .errors import SMSError
from .models import db, LoginSMS, SMSIdentity

IDP_NAME = "SMS"
log = logging.getLogger(__name__)
router = APIRouter()
provider: Optional[SMSBaseProvider] = None


class SMSBaseProvider:
    def __init__(self, app_id, template_id, sign):
        self.client = httpx.AsyncClient()
        self.sms_app_id = app_id
        self.sms_template_id = template_id
        self.sms_sign = sign

    async def send_login_code(self, phone_num: str, code: str, ttl: int):
        raise NotImplementedError

    async def close(self):
        await self.client.aclose()


@router.post("/login/sms")
async def request_sms(prefix: str, number: str, ctx=Depends(login_context)):
    if prefix not in config.SMS_SUPPORTED_PREFIX:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"{prefix} not supported.")

    code = generate_token(config.SMS_CODE_LENGTH, config.SMS_CODE_CHARS)
    sms = await LoginSMS.create(prefix=prefix, number=number, code=code)
    if provider:
        try:
            await provider.send_login_code(f"{prefix}{number}", code, config.SMS_TTL)
        except SMSError as error:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, error.code)
    else:
        log.critical("No SMS provider! Send %s to %s%s", code, prefix, number)
    return dict(id=sms.id, ttl=config.SMS_TTL, cool_down=config.SMS_COOL_DOWN)


@router.put("/login/sms/{sms_id}")
async def submit_sms(
    sms_id: str, request: Request, code: str = Form(...), ctx=Depends(login_context)
):
    async with db.transaction() as tx:
        now = int(time.time())
        result = await (
            LoginSMS.outerjoin(
                SMSIdentity,
                db.and_(
                    SMSIdentity.sub == LoginSMS.prefix + LoginSMS.number,
                    SMSIdentity.idp == IDP_NAME,
                ),
            )
            .outerjoin(User)
            .select()
            .with_for_update(of=LoginSMS)
            .where(LoginSMS.id == sms_id)
            .where(LoginSMS.code == code)
            .where(LoginSMS.created_at + config.SMS_TTL > now)
            .where(LoginSMS.consumed_at.is_(None))
            .gino.load((LoginSMS, User.load(current_identity=SMSIdentity)))
            .first()
        )
        if result is None:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Bad SMS code.")
        sms, user = result
        await sms.update(consumed_at=now).apply()
        if user is None:
            user = await User.create(name=sms.prefix + sms.number)
            user.current_identity = await SMSIdentity.create(
                sub=sms.prefix + sms.number,
                idp=IDP_NAME,
                user_id=user.id,
                sms_prefix=sms.prefix,
                sms_number=sms.number,
                created_at=user.created_at,
            )
        rv = await auth.create_authorization_response(request, user, ctx)
        if rv.status_code >= 400:
            tx.raise_rollback()
    return rv


def init_app(app: FastAPI):
    global provider
    if config.SMS_PROVIDER and provider is None:
        for ep in entry_points()["sms.providers"]:
            if ep.name == config.SMS_PROVIDER:
                log.critical("Loading SMS provider: %s", config.SMS_PROVIDER)
                provider = getattr(ep.load(), "create")(app)
                if provider:

                    @app.on_event("shutdown")
                    async def shutdown():
                        await provider.close()

                break
        else:
            log.critical("SMS provider not found: %s", config.SMS_PROVIDER)

    if config.DEBUG or provider:
        app.include_router(router, tags=["SMS Login"])
