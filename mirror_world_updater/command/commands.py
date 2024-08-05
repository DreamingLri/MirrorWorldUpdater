from mcdreforged.api.all import *

from mirror_world_updater.config.config import Config
from mirror_world_updater.tasks.help import HelpMessage
from mirror_world_updater.tasks.upstream import Upstream
from mirror_world_updater.utils.utils import reply_message, tr, mk_cmd


class CommandManager:
    def __init__(self, server: PluginServerInterface):
        self.server = server
        self.config = Config.get()

    def cmd_help(self, source: CommandSource, context: dict):
        what = context.get('what')
        if what is not None and what not in HelpMessage:
            reply_message(source, tr('command.help.no_help', RText(mk_cmd(what), RColor.gray)))
            return

        HelpMessage(source).show_help()

    def set_upstream(self, source: CommandSource, context: CommandContext):
        server_name = context['server']
        if server_name is None:
            reply_message(source, RText(tr('command.upstream.no_server'), RColor.red))
        Upstream(source).set_upstream(server_name)

    def list_upstream(self, source: CommandSource, _):
        Upstream(source).list_upstream()

    def cmd_sync(self):
        pass

    def cmd_welcome(self):
        pass

    def register_command(self):
        builder = SimpleCommandBuilder()

        # help
        builder.command('help', self.cmd_help)
        builder.command('help <what>', self.cmd_help)
        # upstream
        builder.command('upstream', lambda src: self.cmd_help(src, {'what': 'upstream'}))
        builder.command('upstream set <server>', self.set_upstream)
        builder.command('upstream list', self.list_upstream)
        # sync
        builder.command('sync', self.cmd_sync)

        root = (
            Literal(self.config.prefix).runs(self.cmd_welcome)
        )

        builder.add_children_for(root)
        self.server.register_command(root)

