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
    client_mapping = {}
    for app_id, client_conf in {client["AppID"]: client for client in clients}.items():
        module, cls_name = client_conf["Type"].rsplit(".", 1)
        client_cls = getattr(importlib.import_module(module), cls_name)
        client_mapping[app_id] = client_cls(app_id, client_conf["AppSecret"])
    return client_mapping


WECHAT_CLIENTS = config("WECHAT_CLIENTS", cast=get_wechat_clients, default="")
