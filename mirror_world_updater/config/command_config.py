from mcdreforged.api.all import Serializable
from mirror_world_updater import constants


class CommandPermissions(Serializable):
    root: int = 0
    help: int = 1
    sync: int = 3

    def get(self, literal: str) -> int:
        if literal.startswith('_'):
            raise KeyError(literal)
        return getattr(self, literal, constants.DEFAULT_COMMAND_PERMISSION_LEVEL)

    def items(self):
        return self.serialize().items()


class CommandConfig(Serializable):
    prefix: str = "!!mwu"
    permissions: CommandPermissions = CommandPermissions()

