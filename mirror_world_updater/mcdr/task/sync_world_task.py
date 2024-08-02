import shutil
import time
from abc import ABC
from pathlib import Path
from typing import Union, List

import mcdreforged.api.event
from mcdreforged.api.all import *

from mirror_world_updater.mcdr.mcdr_globals import server
from mirror_world_updater.mcdr.task.basic_task import _BasicTask
from mirror_world_updater.mcdr.text_components import TextComponent
from mirror_world_updater.utils.mcdr_util import click_and_run, mkcmd
from prime_backup.mcdr.task_manager import TaskManager


class SyncWorldTask(_BasicTask[None], ABC):
    def __init__(self, source: CommandSource):
        super().__init__(source)
        self.task_manager: TaskManager = server.get_plugin_instance('prime_backup').task_manager
        self.has_backup = False

    @property
    def id(self):
        return 'sync'

    def reply(self, msg: Union[str, RTextBase], *, with_prefix: bool = False):
        super().reply(msg, with_prefix=with_prefix)

    def run(self) -> None:
        pass

    def list_backups(self) -> None:
        pass

    def __countdown_and_stop_server(self, current_upstream: str) -> bool:

        for countdown in range(max(0, self.config.sync_countdown_sec), 0, -1):
            self.broadcast(click_and_run(RText('!!! ', RColor.red) + self.tr('countdown', countdown, current_upstream),
                                         self.tr('countdown.hover', TextComponent.command('sync abort')),
                                         mkcmd('abort')
                                         ))

        self.server.stop()
        self.server.wait_until_stop()
        return True

    def __backup_before_sync(self, current_upstream: str) -> None:
        from prime_backup.mcdr.task.backup.create_backup_task import CreateBackupTask
        comment: str = 'backup before sync to ' + current_upstream

        self.task_manager.add_task(CreateBackupTask(self.source, comment), callback=self.__server_has_backup())

    def __server_has_backup(self):
        self.has_backup = True

    def __sync_backup(self, world_path: str, sync_path: str) -> None:
        shutil.rmtree(world_path)
        shutil.copytree(sync_path, world_path)
        self.has_backup = False

    def sync(self) -> None:
        try:
            self_config = self.config.get()
            current_upstream = self_config.paths.current_upstream
            backup_before_sync = self_config.backup_before_sync

            world_path = self_config.paths.world_path
            sync_path = self_config.paths.sync_path

            if world_path == sync_path:
                self.reply(RText(self.tr('duplicate'), RColor.red))

            if backup_before_sync:
                self.__backup_before_sync(current_upstream)

            server_was_running = self.server.is_server_running()

            while not self.has_backup:
                time.sleep(0.1)
            if server_was_running:
                if not self.__countdown_and_stop_server(current_upstream):
                    return

            self.__sync_backup(world_path, sync_path)

            if server_was_running:
                self.server.start()
                self.broadcast(self.tr('success', RText(current_upstream), RColor.dark_aqua))
        except Exception as e:
            self.broadcast(self.tr('error', RText(e), RColor.red))

    def abort(self) -> None:
        pass

    def confirm(self) -> None:
        pass

