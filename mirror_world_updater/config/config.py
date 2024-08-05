import functools
from typing import Optional, List

from mcdreforged.api.all import *

from mirror_world_updater.config.permission_config import PermissionConfig


class ServerInfo(Serializable):
    server: str
    server_path: str


class Config(Serializable):
    upstream: str = 'survival'
    upstream_server_path: str = '../survival/server'
    upstream_list: List[ServerInfo] = [
        ServerInfo(server='survival', server_path='../survival/server'),
        ServerInfo(server='mirror', server_path='../mirror/server'),
        ServerInfo(server='creative', server_path='../creative/server'),
    ]
    self_server_path: str = './server'
    world_names: List[str] = ['world']
    count_down: int = 10
    backup_before_sync: bool = True
    ignore_session_lock: bool = True
    prefix: str = '!!sync'
    permission: PermissionConfig = PermissionConfig()

    # func
    @classmethod
    @functools.lru_cache
    def __get_default(cls) -> 'Config':
        return Config.get_default()

    @classmethod
    def get(cls) -> 'Config':
        if _config is None:
            return cls.__get_default()
        return _config


def set_config_instance(cfg: Config):
    global _config
    _config = cfg


_config: Optional[Config] = None
