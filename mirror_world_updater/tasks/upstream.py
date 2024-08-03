from abc import ABC

from mcdreforged.command.command_source import CommandSource

from mirror_world_updater.tasks.task import Task


class Upstream(Task, ABC):
    def __init__(self, source: CommandSource):
        super().__init__(source)

    def id(self) -> str:
        return 'upstream'
