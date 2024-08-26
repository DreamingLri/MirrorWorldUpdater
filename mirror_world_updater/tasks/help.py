from typing import Optional, Union

from mcdreforged.api.all import *

from mirror_world_updater.tasks.__init__ import Task
from mirror_world_updater.utils.utils import reply_message, tr, mk_cmd
from mirror_world_updater.utils import help_message_utils


class HelpMessage(Task):
    COMMANDS_WITH_DETAILED_HELP = [
        'upstream', 'update', 'region'
    ]

    def __init__(self, source: CommandSource):
        super().__init__(source)

    @property
    def id(self) -> str:
        return 'help'

    def reply(self, msg: Union[str, RTextBase], *, with_prefix: bool = False):
        super().reply(msg, with_prefix=with_prefix)

    def __reply_help(self, msg: RTextBase, hide_for_permission: bool = False):
        for h in help_message_utils.parse_help_message(msg):
            if hide_for_permission and h.is_help() and not self.source.has_permission(h.permission):
                continue
            self.reply(h.text)

    def __has_permission(self, literal: str) -> bool:
        return self.source.has_permission(self.config.permission.get(literal))

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
                self.reply(self.tr('commands.title').set_color(RColor.dark_aqua))
                self.__reply_help(self.tr('commands.content', prefix=self.__cmd_prefix), True)

            elif what in self.COMMANDS_WITH_DETAILED_HELP:
                if not self.__has_permission(what):
                    self.reply_tr('permission_denied', RText(what, RColor.gray))
                    return

                kwargs = {'prefix': self.__cmd_prefix}
                self.__reply_help(self.tr(f'node_help.{what}', **kwargs))

            else:
                raise ValueError(what)
