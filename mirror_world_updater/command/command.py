from typing import Optional
from mcdreforged.api.all import *
from mirror_world_updater.config.config import Config
from mirror_world_updater.utils.mcdr_util import *

COMMAND_HELP_LIST = ['help', 'sync']


class CommandManager:
    def __init__(self, server: PluginServerInterface):
        self.server = server
        self.config = Config.get()

    def cmd_help(self, source: CommandSource, context: dict):
        what = context.get('what')
        if what is not None and what not in COMMAND_HELP_LIST:
            reply_message(source, tr('help.unknown_help', RText(f'!!mwu {what}', RColor.red)))
            return
        else:
            self.help_info(source, what)

    @classmethod
    def help_info(cls, source: CommandSource, what: Optional[str]):
        reply_message(source, tr('help.help_header'))
        if what is None:
            reply_message(source, tr('help.help', RText(what, RColor.red)))
            reply_message(source, tr('help.sync', RText(what, RColor.red)))
        else:
            reply_message(source, tr('help.' + what, RText(what, RColor.red)))

    def register_commands(self):
        builder = SimpleCommandBuilder()
        builder.command('help', self.cmd_help)
        builder.command('help <what>', self.cmd_help)

        root = (
            Literal('!!mam')
            .runs(self.cmd_help)
        )
        builder.add_children_for(root)

        self.server.register_command(root)
