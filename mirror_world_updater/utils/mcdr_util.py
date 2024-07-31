from abc import ABC

from mcdreforged.api.all import *
from typing import Union, Any


def tr(key: str, *args, **kwargs) -> RTextBase:
    from mirror_world_updater import constants
    return ServerInterface.si().rtr(constants.PLUGIN_ID + '.' + key, *args, **kwargs)


class TranslationContext(ABC):
    def __init__(self, base_key: str):
        self.__base_key = base_key

    def tr(self, key: str, *args, **kwargs) -> RTextBase:
        k = self.__base_key
        if len(key) > 0:
            k += '.' + key
        return tr(k, *args, **kwargs)


def reply_message(source: CommandSource, msg: Union[str, RTextBase], *, with_prefix: bool = True):
    if with_prefix:
        msg = RTextList(__make_message_prefix(), msg)
    source.reply(msg)


def __make_message_prefix() -> RTextBase:
    return RTextList(RText('[MWU]', RColor.dark_aqua).h('Mirror World Updater'), ' ')


def click_and_run(message: Any, text: Any, command: str) -> RTextBase:
    return RTextBase.from_any(message).h(text).c(RAction.run_command, command)


def mkcmd(s: str) -> str:
    from mirror_world_updater.config.config import Config
    cmd = Config.get().command.prefix
    if len(s) > 0:
        cmd += ' ' + s
    return cmd
