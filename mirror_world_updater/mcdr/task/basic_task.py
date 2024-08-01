from abc import ABC
from typing import TypeVar, Union
from mcdreforged.api.all import *

from mirror_world_updater.mcdr.task import Task, help_message_utils
from mirror_world_updater.utils import mcdr_util

T = TypeVar('T')
_T = TypeVar('_T')


class _BasicTask(Task[_T], ABC):
    def __init__(self, source: CommandSource):
        super().__init__(source)

        from mirror_world_updater.config.config import Config
        self.config = Config()

        self._quite = False

    def reply_tr(self, key: str, *args, **kwargs):
        with_prefix = kwargs.pop('with_prefix', True)
        self.reply(self.tr(key, *args, **kwargs), with_prefix=with_prefix)

    def reply(self, msg: Union[str, RTextBase], *, with_prefix: bool = True):
        if self._quite:
            return
        mcdr_util.reply_message(self.source, msg, with_prefix=with_prefix)
