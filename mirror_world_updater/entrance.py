from typing import Optional

from mcdreforged.api.all import *

from mirror_world_updater.command.command import CommandManager

command_manager: Optional[CommandManager] = None


def on_load(server: PluginServerInterface, old):
    global command_manager

    command_manager = CommandManager(server)
    command_manager.register_commands()
