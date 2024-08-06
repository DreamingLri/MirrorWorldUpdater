import functools
from typing import Callable

from mcdreforged.api.all import *

from mirror_world_updater.config.config import Config
from mirror_world_updater.tasks.help import HelpMessage
from mirror_world_updater.tasks.sync import Sync
from mirror_world_updater.tasks.upstream import Upstream
from mirror_world_updater.tasks.welcome import Welcome
from mirror_world_updater.utils.utils import reply_message, tr, mk_cmd


class CommandManager:
    def __init__(self, server: PluginServerInterface):
        self.server = server
        self.config = Config.get()

    # call functions

    def cmd_help(self, source: CommandSource, context: dict):
        what = context.get('what')
        if what is not None and what not in HelpMessage.COMMANDS_WITH_DETAILED_HELP:
            reply_message(source, tr('command.help.no_help', RText(mk_cmd(what), RColor.gray)))
            return

        HelpMessage(source).show_help(what)

    def set_upstream(self, source: CommandSource, context: CommandContext):
        server_name = context.get('server')
        Upstream(source).set_upstream(server_name)

    def list_upstream(self, source: CommandSource):
        Upstream(source).list_upstream()

    def cmd_sync(self, source: CommandSource, context: CommandContext):
        needs_confirm = context.get('confirm', 0) == 0
        ignore_file = context.get('ignore', 0) == 1
        Sync(source).update_world(needs_confirm=needs_confirm, ignore_file=ignore_file)

    def cmd_welcome(self, source: CommandSource):
        Welcome(source).show_welcome()

    def confirm(self, source: CommandSource, _):
        Sync(source).confirm()

    def abort(self, source: CommandSource):
        Sync(source).abort()

    def register_command(self):
        permissions = self.config.permission

        def get_permission_checker(literal: str) -> Callable[[CommandSource], bool]:
            return functools.partial(CommandSource.has_permission, level=permissions.get(literal))

        def get_permission_denied_text():
            return tr('error.permission_denied').set_color(RColor.red)

        def create_subcommand(literal: str) -> Literal:
            node = Literal(literal)
            node.requires(get_permission_checker(literal), get_permission_denied_text)
            return node

        builder = SimpleCommandBuilder()

        # simple commands
        # help
        builder.command('help', self.cmd_help)
        builder.command('help <what>', self.cmd_help)

        builder.arg('what', Text).suggests(lambda: HelpMessage.COMMANDS_WITH_DETAILED_HELP)

        # upstream
        builder.command('upstream', lambda src: self.cmd_help(src, {'what': 'upstream'}))
        builder.command('upstream set', self.set_upstream)
        builder.command('upstream set <server>', self.set_upstream)
        builder.command('upstream list', self.list_upstream)

        builder.arg('server', GreedyText).suggests(lambda: Upstream.server_list)

        # sync
        builder.command('update', self.cmd_sync)

        # command
        builder.command('confirm', self.confirm)
        builder.command('abort', self.abort)

        root = (
            Literal(self.config.prefix).runs(self.cmd_welcome)
        )

        builder.add_children_for(root)

        # complex commands
        # update
        def set_confirm_able(node: AbstractNode):
            node.then(CountingLiteral('--confirm', 'confirm').redirects(node))

        def set_ignore_files(node: AbstractNode):
            node.then(CountingLiteral('--ignore', 'ignore').redirects(node))

        def make_sync_cmd() -> Literal:
            node_sc = create_subcommand('update')
            for node in [node_sc]:
                set_confirm_able(node)
                set_ignore_files(node)
                node.runs(self.cmd_sync)
            return node_sc

        root.then(make_sync_cmd())

        self.server.register_command(root)
