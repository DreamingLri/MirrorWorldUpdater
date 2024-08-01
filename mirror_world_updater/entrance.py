from typing import Optional

from mcdreforged.api.all import *

from mirror_world_updater.config.config import Config
from mirror_world_updater.mcdr.command.commands import CommandManager

command_manager: Optional[CommandManager] = None
config: Optional[Config] = None


def on_load(server: PluginServerInterface, old):
    global command_manager, config

    try:
        config = server.load_config_simple(target_class=Config, failure_policy='raise')
        command_manager = CommandManager(server)
        command_manager.register_commands()
    except Exception as e:
        server.logger.error('Failed to load config: {}'.format(e))
