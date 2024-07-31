from abc import ABC, abstractmethod
from typing import TypeVar, Generic

from mirror_world_updater.utils import mcdr_util
from mcdreforged.api.all import *

T = TypeVar('T')


class Task(Generic[T], mcdr_util.TranslationContext, ABC):
    def __init__(self, source: CommandSource):
        super().__init__(f'task.{self.id}')

        from mirror_world_updater.mcdr import mcdr_globals
        self.source = source
        self.server = mcdr_globals.server

    @property
    @abstractmethod
    def id(self) -> str:
        ...

    @abstractmethod
    def run(self) -> T:
        ...
