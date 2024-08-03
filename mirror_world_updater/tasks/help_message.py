from abc import ABC
from typing import Optional, Union

from mcdreforged.api.all import *

from mirror_world_updater.tasks.task import Task
from mirror_world_updater.utils.utils import reply_message, tr, mk_cmd
from mirror_world_updater.utils import utils

COMMANDS_WITH_DETAILED_HELP = [
    'upstream'
]


def show_help(what: Optional[str] = None):
    if what is None:
        utils.reply_message()


class HelpMessage(Task, ABC):
    def __init__(self, source: CommandSource):
        super().__init__(source)

    def id(self) -> str:
        return 'help'

    def show_help_message(self, context: CommandContext):
        what = context.get('what')
        if what is not None and what not in COMMANDS_WITH_DETAILED_HELP:
            reply_message(self.source, tr('command.help.no_help', RText(mk_cmd(what), RColor.red)))
        else:
            show_help(what)
