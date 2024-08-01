import functools
from typing import Optional, Callable
from mirror_world_updater.config.config import Config
from mirror_world_updater.mcdr.task.show_help_task import ShowHelpTask
from mirror_world_updater.mcdr.task.sync_world_task import SyncWorldTask
from mirror_world_updater.mcdr.task.upstream_task import UpstreamTask
from mirror_world_updater.utils.mcdr_util import *
from mirror_world_updater.mcdr.task.show_welcome_task import ShowWelcomeTask

COMMAND_HELP_LIST = ['sync', 'list']


class CommandManager:
    def __init__(self, server: PluginServerInterface):
        self.server = server
        self.config = Config.get()

    def cmd_help(self, source: CommandSource, context: dict):
        what = context.get('what')
        if what is not None and what not in COMMAND_HELP_LIST:
            reply_message(source, tr('command.help.no_help', RText(f'!!mwu {what}', RColor.red)))
            return
        else:
            help_task = ShowHelpTask(source, what)
            help_task.run()

    def cmd_welcome(self, source: CommandSource, context: CommandContext):
        show_welcome = ShowWelcomeTask(source)
        show_welcome.run()

    def sync_world(self, source: CommandSource, _):
        sync_task = SyncWorldTask(source)
        sync_task.run()

    def list_upstream(self, source: CommandSource, _):
        upstream_task = UpstreamTask(source)
        upstream_task.list_upstreams()

    def set_upstream(self, source: CommandSource, context: CommandContext):
        server_name = context.get('server_name')
        server_list = self.config.paths.server_list
        if server_name not in server_list:
            reply_message(source, tr('command.upstream.no_server', RText(server_name, RColor.red)))
        else:
            upstream_task = UpstreamTask(source)
            upstream_task.set_upstream(server_name)

    def register_commands(self):
        permissions = self.config.command.permissions

        def get_permission_checker(literal: str) -> Callable[[CommandSource], bool]:
            return functools.partial(CommandSource.has_permission, level=permissions.get(literal))

        def get_permission_denied_text():
            return tr('error.permission_denied').set_color(RColor.red)

        builder = SimpleCommandBuilder()
        self.server.register_help_message(self.config.command.prefix, tr('command.help.help'))

        # help
        builder.command('help', self.cmd_help)
        builder.command('help <what>', self.cmd_help)

        builder.arg('what', Text).suggests(lambda: COMMAND_HELP_LIST)

        # sync
        builder.command('sync', self.sync_world)

        builder.arg('backup_id', Integer)
        builder.arg('server_name', Text)

        # check
        builder.command('upstream', self.cmd_help)
        builder.command('upstream list', self.list_upstream)
        builder.command('upstream set <server_name>', self.set_upstream)

        builder.arg('server_name', Text)

        root = (
            Literal(self.config.command.prefix).
            requires(get_permission_checker('root'), get_permission_denied_text)
            .runs(self.cmd_welcome)
        )
        builder.add_children_for(root)

        self.server.register_command(root)