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
    @functools.lru_cache
    def __get_default(cls) -> 'Config':
        return Config.get_default()

    @classmethod
    def get(cls) -> 'Config':
        if _config is None:
            print('default config')
            return cls.__get_default()
        return _config


_config: Optional[Config] = None


def set_config_instance(cfg: Config):
    global _config
    _config = cfg
