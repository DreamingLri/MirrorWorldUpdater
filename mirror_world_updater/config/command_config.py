from mcdreforged.api.all import Serializable
from mirror_world_updater import constants


class CommandPermissions(Serializable):
    root: 0
    help: 1
    sync: 3

    def get(self, literal: str) -> int:
        if literal.startswith('_'):
            raise KeyError(literal)
        return getattr(self, literal, constants.DEFAULT_COMMAND_PERMISSION_LEVEL)


class CommandConfig(Serializable):
    prefix: str = "!!mwu"
    permissions: CommandPermissions = CommandPermissions()

