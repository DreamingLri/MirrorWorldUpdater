from abc import ABC
from typing import Any, Union

from mcdreforged.api.all import *


def tr(key: str, *args, **kwargs) -> RTextBase:
    from mirror_world_updater import constants
    return ServerInterface.si().rtr(constants.PLUGIN_ID + '.' + key, *args, **kwargs)


def mk_cmd(s: str) -> str:
    from prime_backup.config.config import Config
    cmd = Config.get().command.prefix
    if len(s) > 0:
        cmd += ' ' + s
    return cmd


def click_and_run(message: Any, text: Any, command: str) -> RTextBase:
    return RTextBase.from_any(message).h(text).c(RAction.run_command, command)


def __make_message_prefix() -> RTextBase:
    return RTextList(RText('[MWU]', RColor.dark_aqua).h('Mirror World Updater'), ' ')


def reply_message(source: CommandSource, msg: Union[str, RTextBase], *, with_prefix: bool = True):
    if with_prefix:
        msg = RTextList(__make_message_prefix(), msg)
    source.reply(msg)


def broadcast_message(msg: Union[str, RTextBase], *, with_prefix: bool = True):
    if with_prefix:
        msg = RTextList(__make_message_prefix(), msg)
    from mirror_world_updater import mcdr_globals
    mcdr_globals.server.broadcast(msg)


class TranslationContext(ABC):
    def __init__(self, base_key):
        self.__base_key = base_key

    def tr(self, key: str, *args, **kwargs) -> RTextBase:
        k = self.__base_key
        if len(key) > 0:
            k += '.' + key
        return tr(k, *args, **kwargs)
