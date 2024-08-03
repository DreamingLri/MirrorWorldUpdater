from abc import ABC

from mirror_world_updater.tasks.task import Task


class Sync(Task, ABC):
    def __init__(self):
        super().__init__()

    def id(self) -> str:
        return 'sync'
