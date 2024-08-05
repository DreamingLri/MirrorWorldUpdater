from mcdreforged.utils.serializer import Serializable

from mirror_world_updater import constants


class PermissionConfig(Serializable):
    root: int = 0

    upstream: int = 1
    update: int = 1
    abort: int = 1
    confirm: int = 1

    def get(self, literal: str) -> int:
        if literal.startswith('_'):
            raise KeyError(literal)
        return getattr(self, literal, constants.DEFAULT_COMMAND_PERMISSION_LEVEL)
