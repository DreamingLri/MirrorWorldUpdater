from abc import abstractmethod, ABC
from typing import Union

from mcdreforged.api.all import *

from mirror_world_updater import mcdr_globals
from mirror_world_updater.config.config import Config
from mirror_world_updater.utils import utils
from mirror_world_updater.utils.utils import tr
from mirror_world_updater.utils.utils import TranslationContext


class Task(TranslationContext, ABC):
    def __init__(self, source: CommandSource):
        super().__init__(f'task.{self.id}')
        self.source = source
        self.server = mcdr_globals.server
        self.config = Config.get()

    @property
    @abstractmethod
    def id(self) -> str:
        ...

    def reply(self, msg: Union[str, RTextBase], *, with_prefix: bool = True):
        utils.reply_message(self.source, msg, with_prefix=with_prefix)

    def reply_tr(self, key: str, *args, **kwargs):
        with_prefix = kwargs.pop('with_prefix', True)
        self.reply(tr(key, *args, **kwargs), with_prefix=with_prefix)

    def broadcast(self, msg: Union[str, RTextBase], *, with_prefix: bool = True):
        utils.broadcast_message(msg, with_prefix=with_prefix)
