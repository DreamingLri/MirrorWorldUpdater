from abc import ABC
from typing import TypeVar, Union
from mcdreforged.api.all import *

from mirror_world_updater.task import Task
from mirror_world_updater.utils import mcdr_util

T = TypeVar('T')
_T = TypeVar('_T')


class _BasicTask(Task[_T], ABC):
    def __init__(self, source: CommandSource):
        super().__init__(source)

        from mirror_world_updater.config.config import Config
        self.config = Config()

        self._quite = False

    def reply(self, msg: Union[str, RTextBase], *, with_prefix: bool = True):
        if self._quite:
            return
        mcdr_util.reply_message(self.source, msg, with_prefix=with_prefix)

