import functools
from typing import Optional, Callable
from mcdreforged.api.all import *
from mirror_world_updater.config.config import Config
from mirror_world_updater.utils.mcdr_util import *
from mirror_world_updater.task.show_welcome_task import ShowWelcomeTask

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

    def sync_world(self, source: CommandSource, context: dict):
        pass

    def cmd_welcome(self, source: CommandSource, _: CommandSource):
        welcome_msg = ShowWelcomeTask(source)
        welcome_msg.run()

    def register_commands(self):
        permissions = self.config.command.permissions

        def get_permission_checker(literal: str) -> Callable[[CommandSource], bool]:
            return functools.partial(CommandSource.has_permission, level=permissions.get(literal))

        def get_permission_denied_text():
            return tr('error.permission_denied').set_color(RColor.red)

        builder = SimpleCommandBuilder()

        # help
        builder.command('help', self.cmd_help)
        builder.command('help <what>', self.cmd_help)

        builder.arg('what', Text).suggests(lambda: COMMAND_HELP_LIST)

        # sync
        builder.command('sync <pb file>', self.sync_world)

        root = (
            Literal(self.config.command.prefix).
            requires(get_permission_checker('root'), get_permission_denied_text)
            .runs(self.cmd_welcome)
        )
        builder.add_children_for(root)

        self.server.register_command(root)
