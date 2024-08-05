import os
import shutil
import time
from abc import ABC
from datetime import datetime
from typing import Union

from mcdreforged.api.all import *

from mirror_world_updater import constants, mcdr_globals
from mirror_world_updater.tasks.task import Task
from mirror_world_updater.utils.utils import click_and_run, mk_cmd, reply_message, tr
from prime_backup.mcdr.crontab_job import CrontabJobEvent
from prime_backup.mcdr.mcdr_entrypoint import crontab_manager, task_manager
from prime_backup.mcdr.task.backup.create_backup_task import CreateBackupTask
from prime_backup.mcdr.task_manager import TaskManager

abort_sync = False
sync_requested = False


class Sync(Task, ABC):
    def __init__(self, source: CommandSource):
        super().__init__(source)

    def id(self) -> str:
        return 'sync'

    def reply(self, msg: Union[str, RTextBase], *, with_prefix: bool = False):
        super().reply(msg, with_prefix=with_prefix)

    def update_world(self) -> None:
        if not self.__check_paths():
            return

        global abort_sync, sync_requested
        abort_sync = False
        sync_requested = True

        self.reply(RText(self.tr('echo'), RColor.gold))
        self.reply(
            click_and_run(self.tr('confirm_hint'), self.tr('confirm_hover'), mk_cmd('confirm'))
            + ', '
            + click_and_run(self.tr('abort_hint'), self.tr('abort_hover'), mk_cmd('abort'))
        )

    @new_thread('MWU')
    def _update_world(self) -> None:
        self.reply(self.tr('countdown.intro', self.config.count_down))
        for countdown in range(1, self.config.count_down):
            self.broadcast(
                click_and_run(self.tr('countdown.text', self.config.count_down - countdown),
                              self.tr('countdown.hover'),
                              mk_cmd('abort'))
            )
            for i in range(10):
                time.sleep(0.1)
                global abort_sync
                if abort_sync:
                    self.reply(self.tr('aborted'))
                    return

        self.server.stop()
        self.server.logger.info('Wait for server to stop')
        self.server.wait_for_start()

        def callback(_, err):
            if err is None:
                crontab_manager.send_event(CrontabJobEvent.manual_backup_created)

        if self.config.get().backup_before_sync:
            if constants.PB_ID in self.server.get_plugin_list():
                self.server.logger.info('Backup before sync')
                comment: str = 'backup before sync' + datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                task_manager.add_task(CreateBackupTask(self.source, comment), callback)
            else:
                self.server.logger.warning('Backup is enabled but {} is not loaded'.format(constants.PB_ID))

        self.server.logger.info('Deleting world')
        self.remove_worlds(self.config.get().upstream_server_path)

        self.server.logger.info('Copying {} worlds to the qmirror server'.format(self.config.get().upstream))

        self.copy_worlds(self.config.get().upstream_server_path, self.config.get().self_server_path)
        self.server.logger.info('Sync done, starting the server')
        self.server.start()

    def confirm(self) -> None:
        global sync_requested
        if not sync_requested:
            reply_message(self.source, tr('command.confirm.no_confirm'))
        else:
            self._update_world()
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

            def filter_ignore(path, files):
                return [file for file in files if file == 'session.lock' and self.config.get().ignore_session_lock]

            if os.path.isdir(src_path):
                shutil.copytree(src_path, dst_path, ignore=filter_ignore)

            elif os.path.isfile(src_path):
                dst_dir = os.path.dirname(dst_path)
                if not os.path.isdir(dst_dir):
                    os.makedirs(dst_dir)
                shutil.copy(src_path, dst_path)
            else:
                self.server.logger.warning('{} does not exist while copying ({} -> {})'
                                           .format(src_path, src_path, dst_path))

