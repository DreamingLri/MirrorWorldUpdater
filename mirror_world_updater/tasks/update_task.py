import os
from abc import ABC, abstractmethod

from mcdreforged.command.command_source import CommandSource
from mcdreforged.minecraft.rtext.style import RColor
from mcdreforged.minecraft.rtext.text import RText

from mirror_world_updater.tasks import Task


class UpdateTask(Task):
    def __init__(self, source: CommandSource):
        super().__init__(source)

    def check_paths(self) -> bool:
        success = True

        def check_dir(path: str) -> bool:
            if not os.path.exists(path):
                self.reply(self.tr('path.not_exist', RText(path, RColor.green)))
                return False
            if not os.path.isdir(path):
                self.reply(self.tr('path.not_a_dir', RText(path, RColor.green)))
                return False
            return True

        def check_server_path(path: str):
            if not check_dir(path):
                return False
            for world in self.config.world_names:
                world_path = os.path.join(path, world)
                if not check_dir(world_path):
                    return False
            return True

        success = success and check_server_path(self.config.upstream_server_path)
        success = success and check_server_path(self.config.self_server_path)

        return success

    @abstractmethod
    def confirm(self) -> None:
        pass

    @abstractmethod
    def abort(self) -> None:
        pass
