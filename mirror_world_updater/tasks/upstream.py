from typing import Union

from mcdreforged.api.all import *

from mirror_world_updater.tasks.__init__ import Task
from mirror_world_updater.utils.utils import click_and_run, mk_cmd


class Upstream(Task):
    server_list = [
        'survival',
        'mirror',
        'creative'
    ]

    def __init__(self, source: CommandSource):
        super().__init__(source)
        self.update_config = self.config.get()
        self.upstream = self.config.get().upstream
        self.upstream_server_path = self.config.get().upstream_server_path
        self.upstream_list = self.config.get().upstream_list

    @property
    def id(self) -> str:
        return 'upstream'

    def reply(self, msg: Union[str, RTextBase], *, with_prefix: bool = False):
        super().reply(msg, with_prefix=with_prefix)

    def list_upstream(self) -> None:
        self.reply(RText(self.tr("title"), RColor.dark_aqua))
        self.reply(self.tr(
            "current_upstream",
            name=RText(self.upstream, RColor.dark_aqua),
            path=RText(self.upstream_server_path, RColor.gray)))

        for server_info in self.upstream_list:
            self.reply(self.tr(
                "list_upstream",
                name=RText(server_info.server, RColor.dark_aqua),
                path=RText(server_info.server_path, RColor.gray))
                + ' ' + click_and_run(
                RText('[+]', RColor.dark_green),
                self.tr('set_upstream'),
                mk_cmd('upstream set ' + server_info.server)
            ))

    def set_upstream(self, server_name: str) -> None:
        for server_info in self.upstream_list:
            if server_info.server == server_name:
                self.update_config.upstream = server_name
                self.update_config.upstream_server_path = server_info.server_path
                self.reply(self.tr("set_success", RText(server_name, RColor.dark_aqua)))
                self.server.save_config_simple(self.config)
                return

        self.reply(self.tr("no_upstream", RText(server_name, RColor.red)))
        self.list_upstream()
        return
