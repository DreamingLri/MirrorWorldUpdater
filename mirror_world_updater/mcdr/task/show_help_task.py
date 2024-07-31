from abc import ABC
from typing import Union, Optional

from mcdreforged.api.all import *

from mirror_world_updater.mcdr.task import help_message_utils
from mirror_world_updater.mcdr.task.basic_task import _BasicTask


class ShowHelpTask(_BasicTask[None], ABC):
    COMMANDS_WITH_DETAILED_HELP = [
        'help',
        'sync'
    ]

    @property
    def id(self) -> str:
        return 'help'

    @property
    def __cmd_prefix(self) -> str:
        return self.config.command.prefix

    def __init__(self, source: CommandSource, what: Optional[str] = None):
        super().__init__(source)
        self.what = what

    def __has_permission(self, literal: str) -> bool:
        return self.source.has_permission(self.config.command.permission.get(literal))

    def __reply_help(self, msg: RTextBase, hide_for_permission: bool = False):
        for h in help_message_utils.parse_help_message(msg):
            if hide_for_permission and h.is_help() and not self.source.has_permission(h.permission):
                continue
            self.reply(h.text)

    def reply(self, msg: Union[str, RTextBase], *, with_prefix: bool = False):
        super().reply(msg, with_prefix=with_prefix)

    def run(self) -> None:
        if self.what is None:
            self.reply(self.tr('commands.title').set_color(RColor.blue))
            self.__reply_help(self.tr('commands.content', prefix=self.__cmd_prefix), True)

        elif self.what in self.COMMANDS_WITH_DETAILED_HELP:
            if not self.__has_permission(self.what):
                self.reply_tr('permission_denied', RText(self.what, RColor.gray))
                return
        else:
            raise ValueError(self.what)
