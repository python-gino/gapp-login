import importlib
import json

from authlib_gino.fastapi_session.gino_app import load_entry_point
from starlette.config import Config

config: Config = load_entry_point("config", Config)


def get_wechat_clients(value: str):
    """A list of WeChat clients, the value can be a JSON string like this:
    [
        {
            "AppID": "...",
            "AppSecret": "...",
            "Type": "gapp_login.wechat.MiniProgramClient"
        }
    ]
    """
    clients = json.loads(value)
    return {
        client["AppID"]: (
            lambda module, cls_name: getattr(importlib.import_module(module), cls_name)(
                client["AppID"], client["AppSecret"]
            )
        )(*client["Type"].rsplit(".", 1))
        for client in clients
    }


WECHAT_CLIENTS = config("WECHAT_CLIENTS", cast=get_wechat_clients, default="")
