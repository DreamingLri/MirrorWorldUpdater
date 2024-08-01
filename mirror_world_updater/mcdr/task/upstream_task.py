from abc import ABC
from typing import Union

from mcdreforged.api.all import *

from mirror_world_updater.mcdr.task.basic_task import _BasicTask


class UpstreamTask(_BasicTask, ABC):
    @property
    def id(self) -> str:
        return 'upstream'

    def reply(self, msg: Union[str, RTextBase], *, with_prefix: bool = False):
        super().reply(msg, with_prefix=with_prefix)

    def run(self) -> None:
        pass

    def set_upstream(self, server_name: str):
        self.config.paths.current_upstream = server_name
        self.reply(self.tr('set_upstream_server_success', name=RText(server_name, RColor.dark_aqua)))

    def list_upstreams(self):
        server_list = self.config.paths.server_list
        self.reply(self.tr('title'))
        for server in server_list:
            self.reply(RText(server, RColor.dark_aqua))
