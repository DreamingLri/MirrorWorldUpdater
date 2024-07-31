import functools

from mcdreforged.api.all import Serializable
from mirror_world_updater.config.command_config import CommandConfig
from typing import Optional


class Config(Serializable):
    enabled: bool = True
    backup_before_update: bool = True
    command: CommandConfig = CommandConfig()

    @classmethod
    def get(cls) -> 'Config':
        if _config is None:
            return cls.__get_default()

    @classmethod
    @functools.lru_cache
    def __get_default(cls) -> 'Config':
        return Config.get_default()


_config = Optional[Config] = None
