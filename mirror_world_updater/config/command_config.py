from mcdreforged.api.all import Serializable


class CommandPermissions(Serializable):
    root: 0
    help: 1
    sync: 3


class CommandConfig(Serializable):
    prefix: str = "!!mwu"
    permissions: CommandPermissions = CommandPermissions()

