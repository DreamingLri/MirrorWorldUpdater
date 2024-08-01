from abc import ABC
from pathlib import Path
from typing import Union, List

from mcdreforged.api.all import *

from mirror_world_updater.mcdr.task.basic_task import _BasicTask



class SyncWorldTask(_BasicTask[None], ABC):
    def __init__(self, source: CommandSource):
        super().__init__(source)

    @property
    def id(self):
        return 'sync'

    def reply(self, msg: Union[str, RTextBase], *, with_prefix: bool = False):
        super().reply(msg, with_prefix=with_prefix)

    def run(self) -> None:
        pass

    def list_backups(self) -> None:
        from prime_backup.action.list_backup_action import ListBackupAction
        from prime_backup.types.backup_info import BackupInfo
        backup_list: List[BackupInfo] = ListBackupAction().run()
        if len(backup_list) == 0:
            self.reply(self.tr('no_backups'))
        for backup_id in backup_list:
            self.reply(self.tr('list_backups',
                               backup_id=RText(backup_id.id, RColor.dark_aqua),
                               comment=RText(backup_id.comment, RColor.aqua)))

    def sync(self, backup_id: int) -> None:
        file = open(self.config.paths.destination_pb_file_directory)
        file2 = open(self.config.paths.upstreams)
        print(file)
        print(file2)






