from abc import ABC
from typing import Union

from mcdreforged.api.all import *

from mirror_world_updater.mcdr.task.basic_task import _BasicTask


class SyncWorldTask(_BasicTask[None], ABC):
    def __init__(self, source: CommandSource):
        super().__init__(source)

    @property
    def id(self):
        return 'sync'

    def reply(self, msg: Union[str, RTextBase], *, with_prefix: bool = False):
        super().reply(msg, with_prefix=with_prefix)

    def run(self) -> None:
        pass




