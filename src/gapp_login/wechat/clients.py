import json
from typing import Optional

import httpx

WXA_TOKEN_EP = "https://api.weixin.qq.com/sns/jscode2session"
WXA_AUTH_RESP_FIELDS = {
    "openid",
    "session_key",
}

OAUTH2_TOKEN_EP = "https://api.weixin.qq.com/sns/oauth2/access_token"
OAUTH2_REFRESH_TOKEN_EP = "https://api.weixin.qq.com/sns/oauth2/refresh_token"
USER_INFO_EP = "https://api.weixin.qq.com/sns/userinfo"
OAUTH2_AUTH_RESP_FIELDS = {
    "access_token",
    "expires_in",
    "refresh_token",
    "openid",
    "scope",
}
USER_RESP_FIELDS = {
    "nickname",
    "headimgurl",
    "sex",
}


class WeChatAuthError(Exception):
    def __init__(self, error: Optional[str] = None) -> None:
        self.error = error

    def __repr__(self) -> str:
        return f"WeChatAuthError(error={self.error!r})"


class WeChatBaseClient:
    def __init__(self, appid: str, secret: str):
        self.appid = appid
        self.secret = secret
        self.client = httpx.AsyncClient()


class OAuth2WeChatClient(WeChatBaseClient):
    async def request_token(self, code: str) -> dict:
        response = await self.client.get(
            OAUTH2_TOKEN_EP,
            params=dict(
                appid=self.appid,
                secret=self.secret,
                code=code,
                grant_type="authorization_code",
            ),
        )
        data = response.json()
        if not OAUTH2_AUTH_RESP_FIELDS <= set(data.keys()):
            raise WeChatAuthError(data)
        return data

    async def refresh_token(self, refresh_token: str) -> dict:
        response = await self.client.get(
            OAUTH2_REFRESH_TOKEN_EP,
            params=dict(
                appid=self.appid,
                grant_type="refresh_token",
                refresh_token=refresh_token,
            ),
        )
        data = response.json()
        if not OAUTH2_AUTH_RESP_FIELDS <= set(data.keys()):
            raise WeChatAuthError(data)
        return data

    async def get_user_info(self, access_token: str, openid: str) -> dict:
        response = await self.client.get(
            USER_INFO_EP,
            params=dict(access_token=access_token, openid=openid, lang="zh_CN"),
        )
        content = response.content.decode("utf-8")
        data = json.loads(content)
        if not USER_RESP_FIELDS <= set(data.keys()):
            raise WeChatAuthError(data)
        return data


class MiniProgramClient(WeChatBaseClient):
    async def request_token(self, code: str) -> dict:
        response = await self.client.get(
            WXA_TOKEN_EP,
            params=dict(
                appid=self.appid,
                secret=self.secret,
                js_code=code,
                grant_type="authorization_code",
            ),
        )
        data = response.json()
        if not WXA_AUTH_RESP_FIELDS <= set(data.keys()):
            raise WeChatAuthError(data)
        return data
