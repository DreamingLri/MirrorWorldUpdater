from abc import ABC
from typing import Optional, Union

from mcdreforged.api.all import *

from mirror_world_updater.tasks.task import Task
from mirror_world_updater.utils.utils import reply_message, tr, mk_cmd
from mirror_world_updater.utils import utils, help_message_utils


class HelpMessage(Task, ABC):
    COMMANDS_WITH_DETAILED_HELP = [
        'upstream'
    ]

    def __init__(self, source: CommandSource):
        super().__init__(source)

    def id(self) -> str:
        return 'help'

    def reply(self, msg: Union[str, RTextBase], *, with_prefix: bool = False):
        super().reply(msg, with_prefix=with_prefix)

    def __reply_help(self, msg: RTextBase, hide_for_permission: bool = False):
        for h in help_message_utils.parse_help_message(msg):
            if hide_for_permission and h.is_help() and not self.source.has_permission(h.permission):
                continue
            self.reply(h.text)

    @property
    def __cmd_prefix(self) -> str:
        return self.config.prefix

    def show_help_message(self, context: CommandContext):
        what = context.get('what')
        if what is not None and what not in self.COMMANDS_WITH_DETAILED_HELP:
            reply_message(self.source, tr('command.help.no_help', RText(mk_cmd(what), RColor.red)))
        else:
            self.show_help(what)

    def show_help(self, what: Optional[str] = None):
        with self.source.preferred_language_context():
            if what is None:
                self.reply(self.tr('commands.title').set_color(RColor.light_purple))
                self.__reply_help(self.tr('commands.content', prefix=self.__cmd_prefix), True)

            elif what == 'upstream':
                self.reply(self.tr('node_help.title').set_color(RColor.light_purple))
                self.__reply_help(self.tr("node_help.upstream", prefix=self.__cmd_prefix), True)
            else:
                raise ValueError(what)
