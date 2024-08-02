import functools
from typing import Optional, Callable
from mirror_world_updater.config.config import Config
from mirror_world_updater.mcdr.task.show_help_task import ShowHelpTask
from mirror_world_updater.mcdr.task.sync_world_task import SyncWorldTask
from mirror_world_updater.mcdr.task.upstream_task import UpstreamTask
from mirror_world_updater.utils.mcdr_util import *
from mirror_world_updater.mcdr.task.show_welcome_task import ShowWelcomeTask



class CommandManager:
    def __init__(self, server: PluginServerInterface):
        self.server = server
        self.config = Config.get()

    def cmd_help(self, source: CommandSource, context: dict):
        what = context.get('what')
        if what is not None and what not in ShowHelpTask.COMMANDS_WITH_DETAILED_HELP:
            reply_message(source, tr('command.help.no_help', name=RText(f'!!mwu {what}', RColor.red)))
            return
        else:
            help_task = ShowHelpTask(source, what)
            help_task.run()

    def cmd_welcome(self, source: CommandSource, context: CommandContext):
        show_welcome = ShowWelcomeTask(source)
        show_welcome.run()

    def sync_world(self, source: CommandSource, context: CommandContext):
        backup_id = context.get('backup_id')
        if backup_id is None:
            reply_message(source, tr('command.sync.no_sync', RText(backup_id, RColor.red)))
            return
        sync_task = SyncWorldTask(source)
        sync_task.sync(backup_id)

    def list_backups(self, source: CommandSource, _):
        sync_task = SyncWorldTask(source)
        sync_task.list_backups()

    def list_upstream(self, source: CommandSource, _):
        upstream_task = UpstreamTask(source)
        upstream_task.list_upstreams()

    def set_upstream(self, source: CommandSource, context: CommandContext):
        server_name = context.get('server_name')
        server_list = self.config.paths.server_list
        if server_name not in server_list:
            reply_message(source, tr('command.upstream.no_server', name=RText(server_name, RColor.red)))
            return
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

        # help
        builder.command('help', self.cmd_help)
        builder.command('help <what>', self.cmd_help)

        builder.arg('what', Text).suggests(lambda: ShowHelpTask.COMMANDS_WITH_DETAILED_HELP)

        # sync
        builder.command('sync <backup_id>', self.sync_world)
        builder.command('sync list', self.list_backups)

        builder.arg('backup_id', Integer)

        # check
        builder.command('upstream', lambda src: self.cmd_help(src, {'what': 'upstream'}))
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
