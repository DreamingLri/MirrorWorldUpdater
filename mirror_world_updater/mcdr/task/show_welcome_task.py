from abc import ABC
from typing import Union

from mcdreforged.api.all import *

from mirror_world_updater.mcdr.task.basic_task import _BasicTask
from mirror_world_updater.mcdr import mcdr_globals
from mirror_world_updater.mcdr.text_components import TextComponent


class ShowWelcomeTask(_BasicTask[None], ABC):

    @property
    def id(self) -> str:
        return 'welcome'

    def reply(self, msg: Union[str, RTextBase], *, with_prefix: bool = False):
        super().reply(msg, with_prefix=with_prefix)

    def run(self) -> None:
        self.reply(TextComponent.title(self.tr(
            'title',
            name=RText(mcdr_globals.metadata.name, RColor.dark_aqua),
            version=RText(f'v{mcdr_globals.metadata.version}', RColor.gold),
        )))
