from abc import abstractmethod

import httpx

from . import config


class WeChatAuthError(Exception):
    def __init__(self, error: str = None) -> None:
        self.error = error

    def __repr__(self) -> str:
        return f"WeChatAuthError(error={self.error!r})"


class WeChatUtil:
    TOKEN_EP = "https://api.weixin.qq.com/sns/oauth2/access_token"
    REFRESH_TOKEN_EP = "https://api.weixin.qq.com/sns/oauth2/refresh_token"
    USER_INFO_EP = "https://api.weixin.qq.com/sns/userinfo"
    AUTH_CODE_NAME = "code"
    AUTH_RESP_FIELDS = {
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

    @property
    @abstractmethod
    def appid(self):
        pass

    @property
    @abstractmethod
    def secret(self):
        pass

    async def auth(self, code: str = None, refresh_token: str = None):
        if not (code or refresh_token):
            raise RuntimeError()

        async with httpx.AsyncClient() as client:
            if code:
                response = await client.get(
                    f"{self.TOKEN_EP}",
                    params={
                        "appid": self.appid,
                        "secret": self.secret,
                        self.AUTH_CODE_NAME: code,
                        "grant_type": "authorization_code",
                    },
                )
            else:
                response = await client.get(
                    f"{self.REFRESH_TOKEN_EP}",
                    params=dict(
                        access_token=self.appid,
                        grant_type="refresh_token",
                        refresh_token=refresh_token,
                    ),
                )
        data = response.json()
        if not self.AUTH_RESP_FIELDS <= set(data.keys()):
            raise WeChatAuthError(data)

        if data.get("scope") in {"snsapi_userinfo", "snsapi_login"}:
            user_info = await self.get_user_info(data["access_token"], data["openid"])

            if not self.USER_RESP_FIELDS <= set(user_info.keys()):
                raise WeChatAuthError(user_info)

            data.update(user_info)

        return data

    async def get_user_info(self, access_token: str, openid: str):
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.USER_INFO_EP}",
                params=dict(access_token=access_token, openid=openid, lang="zh_CN"),
            )
        return response.json()


class MiniProgramUtil(WeChatUtil):
    TOKEN_EP = "https://api.weixin.qq.com/sns/jscode2session"
    AUTH_CODE_NAME = "jscode"
    AUTH_RESP_FIELDS = {
        "openid",
        "session_key",
    }

    @property
    def appid(self):
        return config.WXA_APP_ID

    @property
    def secret(self):
        return config.WXA_APP_SECRET


class NativeAppUtil(WeChatUtil):
    @property
    def appid(self):
        return config.NATIVE_APP_ID

    @property
    def secret(self):
        return config.NATIVE_APP_SECRET


class OpenWebUtil(WeChatUtil):
    @property
    def appid(self):
        return config.OPEN_WEB_APP_ID

    @property
    def secret(self):
        return config.OPEN_WEB_APP_SECRET


class WXWebUtil(WeChatUtil):
    @property
    def appid(self):
        return config.WX_WEB_APP_ID

    @property
    def secret(self):
        return config.WX_WEB_SECRET
