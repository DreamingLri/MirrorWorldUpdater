import os
import shutil
import threading
import time
from abc import ABC
from datetime import datetime
from typing import Union, List

from mcdreforged.api.all import *

from mirror_world_updater import constants, mcdr_globals
from mirror_world_updater.tasks.__init__ import Task
from mirror_world_updater.text_component import TextComponent
from mirror_world_updater.utils.utils import click_and_run, mk_cmd, reply_message, tr

abort_sync = False
sync_requested = False


def ignore_remove(path: str, ignore_files: List[str]):
    exclude_items = ignore_files or []
    for root, dirs, files in os.walk(path, topdown=False):
        for file in files:
            file_path = os.path.join(root, file)
            if os.path.basename(file_path) not in exclude_items:
                os.remove(file_path)

        for _dir in dirs:
            dir_path = os.path.join(root, _dir)
            if os.path.basename(dir_path) not in exclude_items:
                shutil.rmtree(dir_path, ignore_errors=True)


def ignore_copy(src_path: str, dst_path: str, ignore_files: List[str]):
    exclude_items = ignore_files or []

    def ignore_items(path, items):
        relative_dir: str = os.path.relpath(path, src_path)
        ignored = []
        for item in items:
            item_path = os.path.join(relative_dir, item)
            if item in exclude_items or item_path in exclude_items:
                ignored.append(item)
        return ignored

    shutil.copytree(src_path, dst_path, ignore=ignore_items, dirs_exist_ok=True)


class Sync(Task, ABC):

    def __init__(self, source: CommandSource):
        super().__init__(source)
        self.backup = True
        self.ignore_file = False
        self.condition = threading.Condition()
        self.backup_done = False

    @property
    def id(self) -> str:
        return 'sync'

    def reply(self, msg: Union[str, RTextBase], *, with_prefix: bool = False):
        super().reply(msg, with_prefix=with_prefix)

    def update_world(self, needs_confirm: bool = True, ignore_file: bool = False, backup: bool = True) -> None:
        if not self.__check_paths():
            return

        global abort_sync, sync_requested
        abort_sync = False
        sync_requested = True

        if ignore_file or self.config.get().sync_ignore_files:
            self.ignore_file = True
        if not backup or not self.config.get().backup_before_sync:
            self.backup = False
        if not needs_confirm:
            self.confirm()
            return

        self.reply(RText(self.tr('echo'), RColor.gold))
        self.reply(tr("task.upstream.current_upstream",
                      name=RText(self.config.get().upstream, RColor.dark_aqua),
                      path=RText(self.config.get().upstream_server_path, RColor.gray)))
        self.reply(
            click_and_run(RText(self.tr('confirm_hint'), RColor.green), self.tr('confirm_hover'), mk_cmd('confirm'))
            + '  '
            + click_and_run(RText(self.tr('abort_hint'), RColor.red), self.tr('abort_hover'), mk_cmd('abort'))
        )

    @new_thread(mcdr_globals.metadata.name)
    def _update_world(self) -> None:
        with self.condition:
            while not self.backup_done:
                if not self.backup:
                    break
                self.server.logger.info('Waiting for update...')
                self.condition.wait()
            self.reply(self.tr('countdown.intro', self.config.count_down))
            for countdown in range(self.config.count_down, 0, -1):
                self.broadcast(
                    click_and_run(
                        RText('!!! ', RColor.red) + self.tr('countdown.text', countdown),
                        self.tr('countdown.hover', TextComponent.command('abort')),
                        mk_cmd('abort'),
                    ))
                for i in range(10):
                    time.sleep(0.1)
                    global abort_sync
                    if abort_sync:
                        self.reply(self.tr('aborted'))
                        return

            self.server.stop()
            self.server.logger.info('Wait for server to stop')
            self.server.wait_for_start()

            self.server.logger.info('Deleting world')
            self.remove_worlds(self.config.get().self_server_path)

            self.server.logger.info('Copying {} worlds to the server'.format(self.config.get().upstream))

            self.copy_worlds(self.config.get().upstream_server_path, self.config.get().self_server_path)
            self.server.logger.info('Sync done, starting the server')
            self.server.start()

            self.backup_done = False

    def backup_before_sync(self):
        from prime_backup.mcdr.crontab_job import CrontabJobEvent
        from prime_backup.mcdr.mcdr_entrypoint import crontab_manager, task_manager
        from prime_backup.mcdr.task.backup.create_backup_task import CreateBackupTask

        def callback(_, err):
            with self.condition:
                if err is None:
                    crontab_manager.send_event(CrontabJobEvent.manual_backup_created)
                self.backup_done = True
                self.condition.notify()

        with self.condition:
            if self.config.get().backup_before_sync:
                if constants.PB_ID in self.server.get_plugin_list():
                    self.server.logger.info('Backup before sync')
                    comment: str = 'backup before sync' + datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    task_manager.add_task(CreateBackupTask(self.source, comment), callback)
                else:
                    self.server.logger.warning('Backup is enabled but {} is not loaded'.format(constants.PB_ID))

    def confirm(self) -> None:
        global sync_requested
        if not sync_requested:
            reply_message(self.source, tr('command.confirm.no_confirm'))
        else:
            sync_world = threading.Thread(target=self._update_world)
            update_world = threading.Thread(target=self.backup_before_sync)
            if not self.backup:
                sync_world.start()
                sync_requested = False
                sync_world.join()
                self.backup = True
                return

            update_world.start()
            sync_world.start()

            update_world.join()
            sync_world.join()
            sync_requested = False

    def abort(self) -> None:
        global abort_sync, sync_requested
        abort_sync = True
        sync_requested = False
        self.reply(self.tr('abort'))

    def __check_paths(self) -> bool:
        success = True

        def check_dir(path: str) -> bool:
            if not os.path.exists(path):
                self.reply(self.tr('path.not_exist', RText(path, RColor.green)))
                return False
            if not os.path.isdir(path):
                self.reply(self.tr('path.not_a_dir', RText(path, RColor.green)))
                return False
            return True

        def check_server_path(path: str):
            if not check_dir(path):
                return False
            for world in self.config.world_names:
                world_path = os.path.join(path, world)
                if not check_dir(world_path):
                    return False
            return True

        success = success and check_server_path(self.config.upstream_server_path)
        success = success and check_server_path(self.config.self_server_path)

        return success

    def remove_worlds(self, folder: str):
        for world in self.config.world_names:
            target_path = os.path.join(folder, world)

            while os.path.islink(target_path):
                link_path = os.readlink(target_path)
                os.unlink(target_path)
                target_path = link_path if os.path.isabs(link_path) else os.path.normpath(
                    os.path.join(os.path.dirname(target_path), link_path))

            if os.path.isdir(target_path):
                if self.ignore_file:
                    ignore_files = self.config.get().ignore_files
                    ignore_remove(target_path, ignore_files)
                else:
                    shutil.rmtree(target_path)
            elif os.path.isfile(target_path):
                os.remove(target_path)
            else:
                ServerInterface.get_instance().logger.warning('{} does not exist while removing'.format(target_path))

    def copy_worlds(self, src: str, dst: str):
        for world in self.config.world_names:
            src_path = os.path.join(src, world)
            dst_path = os.path.join(dst, world)

            while os.path.islink(src_path):
                self.server.logger.info('copying {} -> {} (symbolic link)'.format(src_path, dst_path))
                dst_dir = os.path.dirname(dst_path)
                if not os.path.isdir(dst_dir):
                    os.makedirs(dst_dir)
                link_path = os.readlink(src_path)
                os.symlink(link_path, dst_path)
                src_path = link_path if os.path.isabs(link_path) else os.path.normpath(
                    os.path.join(os.path.dirname(src_path), link_path))
                dst_path = os.path.join(dst, os.path.relpath(src_path, src))

            self.server.logger.info('copying {} -> {}'.format(src_path, dst_path))

            if os.path.isdir(src_path):

                if self.ignore_file:
                    ignore_files = self.config.get().ignore_files
                    if self.config.get().ignore_session_lock:
                        ignore_files.append('session.lock')
                    ignore_copy(src_path, dst_path, ignore_files)
                else:
                    def filter_ignore(path, files):
                        return [file for file in files if
                                file == 'session.lock' and self.config.get().ignore_session_lock]

                    shutil.copytree(src_path, dst_path, dirs_exist_ok=True, ignore=filter_ignore)

            elif os.path.isfile(src_path):
                dst_dir = os.path.dirname(dst_path)
                if not os.path.isdir(dst_dir):
                    os.makedirs(dst_dir)
                shutil.copy(src_path, dst_path)
            else:
                self.server.logger.warning('{} does not exist while copying ({} -> {})'
                                           .format(src_path, src_path, dst_path))
