import functools

from mcdreforged.api.all import Serializable
from typing import Optional

from mirror_world_updater.config.command_config import CommandConfig
from mirror_world_updater.config.path_config import Paths


class Config(Serializable):
    enabled: bool = True
    backup_before_update: bool = True
    command: CommandConfig = CommandConfig()
    paths: Paths = Paths()

    @classmethod
    def get(cls) -> 'Config':
        if _config is None:
            return cls.__get_default()
        return _config

    @classmethod
    @functools.lru_cache
    def __get_default(cls) -> 'Config':
        return Config.get_default()


_config: Optional[Config] = None
