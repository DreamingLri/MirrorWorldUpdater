from abc import ABC
from typing import Union

from mcdreforged.api.all import *

from mirror_world_updater.mcdr.task.basic_task import _BasicTask
from mirror_world_updater.utils.mcdr_util import tr


class UpstreamTask(_BasicTask, ABC):
    @property
    def id(self) -> str:
        return 'upstream'

    def reply(self, msg: Union[str, RTextBase], *, with_prefix: bool = False):
        super().reply(msg, with_prefix=with_prefix)

    def run(self) -> None:
        pass

    def set_upstream(self, server_name: str):
        config = self.config.get()
        # pb_path = config.paths.pb_path
        # pb_path = pb_path.replace(config.paths.current_upstream, server_name)
        sync_path = '../' + server_name + '/server/world'
        config.paths.current_upstream = server_name
        # config.paths.pb_path = pb_path
        config.paths.sync_path = sync_path
        self.server.save_config_simple(config)
        self.reply(self.tr('set_upstream_server_success', RText(server_name, RColor.dark_aqua)))

    def list_upstreams(self):
        config = self.config.get()
        server_list = config.paths.server_list
        current_upstream = config.paths.current_upstream
        self.reply(self.tr('title'))
        self.reply(self.tr('current_upstream', RText(current_upstream, RColor.dark_aqua)))
        if len(current_upstream) == 0:
            self.reply(RText(self.tr('no_upstream'), RColor.red))
        for server in server_list:
            self.reply(RText(server, RColor.dark_aqua))
