from typing import Optional

from mcdreforged.api.all import *

from mirror_world_updater.config.config import Config, set_config_instance
from mirror_world_updater.mcdr.command.commands import CommandManager
from mirror_world_updater.mcdr import mcdr_globals

command_manager: Optional[CommandManager] = None
config: Optional[Config] = None

mcdr_globals.load()


def on_load(server: PluginServerInterface, old):
    global command_manager, config
    try:
        config = server.load_config_simple(target_class=Config, failure_policy='raise')
        set_config_instance(config)
        command_manager = CommandManager(server)
        command_manager.register_commands()

        server.register_help_message(config.command.prefix, mcdr_globals.metadata.get_description_rtext())
    except Exception as e:
        server.logger.error('Failed to load config: {}'.format(e))

