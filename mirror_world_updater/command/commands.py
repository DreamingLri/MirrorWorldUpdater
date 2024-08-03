from mcdreforged.api.all import *

from mirror_world_updater.config.config import Config


class CommandManager:
    def __init__(self, server: PluginServerInterface):
        self.server = server
        self.config = Config.get()

    def cmd_help(self):
        pass

    def cmd_upstream(self):
        pass

    def cmd_sync(self):
        pass

    def cmd_welcome(self):
        pass

    def register_command(self):
        builder = SimpleCommandBuilder()

        builder.command('help', self.cmd_help)
        builder.command('upstream', self.cmd_upstream)
        builder.command('sync', self.cmd_sync)

        root = (
            Literal(self.config.prefix).runs(self.cmd_welcome)
        )

        builder.add_children_for(root)
        self.server.register_command(root)

