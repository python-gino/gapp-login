import json
import typing

from authlib_gino.fastapi_session.gino_app import load_entry_point
from starlette.config import Config

from . import utils

config: Config = load_entry_point("config", Config)


class WeChatClients:
    """A list of WeChat clients, the value can be a JSON string like this:
    [
        {
            "AppID": "...",
            "AppSecret": "...",
            "Type": "gapp_login.wechat.MiniProgramClient"
        }
    ]
    """

    def __init__(self, value: str):
        clients = json.loads(value)
        self._clients = clients
        self._client_mapping = {client["AppID"]: client for client in clients}

    def __len__(self) -> int:
        return len(self._clients)

    def __getitem__(self, appid: str) -> utils.WeChatBaseClient:
        client_conf = self._client_mapping.get(appid)
        client_cls = client_conf["Type"].split(".")[-1]
        return getattr(utils, client_cls)(appid, client_conf["AppSecret"])

    def __contains__(self, appid: str) -> bool:
        return appid in self._client_mapping

    def __iter__(self) -> typing.Iterator[str]:
        return iter([f"{c['Type']}({c['AppID']})" for c in self._clients])

    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        items = [item for item in self]
        return f"{class_name}({items!r})"

    def __str__(self) -> str:
        return ", ".join([repr(item) for item in self])


WECHAT_CLIENTS = config("WECHAT_CLIENTS", cast=WeChatClients, default="")
