from typing import Optional

from mcdreforged.api.all import *

from mirror_world_updater import mcdr_globals
from mirror_world_updater.command.commands import CommandManager
from mirror_world_updater.config.config import Config, set_config_instance
from mirror_world_updater.utils.utils import tr, click_and_run, mk_cmd

command_manager: Optional[CommandManager] = None
config: Optional[Config] = None

mcdr_globals.load()


def on_load(server: PluginServerInterface, old):
    global command_manager, config
    try:
        config = server.load_config_simple(target_class=Config, failure_policy='raise')
        set_config_instance(config)
    except Exception as e:
        server.logger.error('Failed to load config: {}'.format(e))
    try:
        command_manager = CommandManager(server)
        command_manager.register_command()

        server.register_help_message(config.prefix, mcdr_globals.metadata.get_description_rtext())
    except Exception as e:
        server.logger.error('Failed to register command: {}'.format(e))


def on_player_joined(server: PluginServerInterface, player: str, info: Info):
    server.tell(player,
                click_and_run(
                    RText("[" + tr("task.welcome.quick_actions.update") + "]", RColor.green),
                    tr("task.welcome.simple_sync"),
                    mk_cmd("update --confirm"))
                )

