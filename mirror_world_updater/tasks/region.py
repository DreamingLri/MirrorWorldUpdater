import datetime
import os
import shutil
import time
from typing import Union, Iterable
from mcdreforged.api.all import *
from datetime import datetime

from mirror_world_updater import mcdr_globals
from mirror_world_updater.config.config import Config
from mirror_world_updater.tasks.update_task import UpdateTask
from mirror_world_updater.text_component import TextComponent
from mirror_world_updater.utils.utils import click_and_run, mk_cmd, reply_message, tr

abort_update = False
update_requested = False

region_list = []
history_list = []


class RegionFile:
    def __init__(self, x: int, z: int, dim: int):
        self.x = x
        self.z = z
        self.dim = dim
        self.config = Config.get()

    def to_file_name(self):
        return 'r.{}.{}.mca'.format(self.x, self.z)

    def to_file_list(self):
        file_list = []
        folders = self.config.dimension_region[str(self.dim)]
        if isinstance(folders, str):
            file_list.append(os.path.join(folders, self.to_file_name()))
        elif isinstance(folders, Iterable):
            for folder in folders:
                file_list.append(os.path.join(folder, self.to_file_name()))
        else:
            pass
        return file_list

    def to_format(self):
        return '[x={}, z={}, d={}]'.format(self.x, self.z, self.dim)

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return False
        return self.x == other.x and self.z == other.z and self.dim == other.dim

    def __repr__(self):
        return 'Region[x={}, z={}, dim={}]'.format(self.x, self.z, self.dim)


def get_region_from_source(source: PlayerCommandSource) -> RegionFile:
    api = source.get_server().get_plugin_instance('minecraft_data_api')
    coord = api.get_player_coordinate(source.player)
    dim = api.get_player_dimension(source.player)
    return RegionFile(int(coord.x) // 512, int(coord.z) // 512, dim)


class Region(UpdateTask):
    def __init__(self, source: CommandSource):
        super().__init__(source)

    @property
    def id(self) -> str:
        return 'region'

    def reply(self, msg: Union[str, RTextBase], *, with_prefix: bool = False):
        super().reply(msg, with_prefix=with_prefix)

    def add_region(self, region: RegionFile) -> None:
        global region_list
        if region in region_list:
            self.reply(self.tr('already_exist', RText(region, RColor.green)))
        else:
            region_list.append(region)
            self.reply(self.tr('added', RText(region, RColor.green)))

    @new_thread(mcdr_globals.metadata.name)
    def add_region_here(self) -> None:
        if isinstance(self.source, PlayerCommandSource):
            self.add_region(get_region_from_source(self.source))
        else:
            self.reply(self.tr('only_player'))

    def del_region(self, region: RegionFile) -> None:
        global region_list
        if region not in region_list:
            self.reply(self.tr('not_exist', RText(region, RColor.green)))
        else:
            region_list.remove(region)
            self.reply(self.tr('deleted', RText(region, RColor.green)))

    @new_thread(mcdr_globals.metadata.name)
    def del_region_here(self) -> None:
        if isinstance(self.source, PlayerCommandSource):
            self.del_region(get_region_from_source(self.source))
        else:
            self.reply(self.tr('only_player'))

    def clear_region_list(self) -> None:
        global region_list
        region_list.clear()
        self.reply(self.tr('cleared'))

    def show_region_list(self) -> None:
        global region_list
        self.reply(RText(self.tr('list.title'), RColor.aqua))
        self.reply(self.tr('list.amount', RText(len(region_list), RColor.aqua))
                   + click_and_run(
            RText('[+]', RColor.green),
            self.tr('list.hover'),
            mk_cmd('region add'))
                   )
        for region in region_list:
            self.reply('- ' + RText(region, RColor.gold))

    def show_history(self) -> None:
        global history_list, region_list
        self.reply(RText(self.tr('history.title'), RColor.aqua))
        self.reply(self.tr('history.amount', RText(len(history_list), RColor.aqua)))
        msg = {True: RText(self.tr('history.succeeded'), RColor.green),
               False: RText(self.tr('history.failed'), RColor.red)}
        for region, flag, info in history_list:
            self.reply(RText(region, RColor.gold) + ': ' + msg[flag].h(info))

    def update_region(self, need_confirm: bool = True) -> None:
        if not self.check_paths():
            return

        global abort_update, update_requested
        abort_update = False
        update_requested = True

        if not need_confirm:
            self.confirm()
            return

        self.reply(tr("task.upstream.current_upstream",
                      name=RText(self.config.get().upstream, RColor.dark_aqua),
                      path=RText(self.config.get().upstream_server_path, RColor.gray)))
        self.reply(
            click_and_run(RText(self.tr('confirm_hint'), RColor.green), self.tr('confirm_hover'),
                          mk_cmd('region confirm'))
            + '  '
            + click_and_run(RText(self.tr('abort_hint'), RColor.red), self.tr('abort_hover'), mk_cmd('region abort'))
        )

    @new_thread(mcdr_globals.metadata.name)
    def __update_region(self) -> None:
        global history_list, region_list
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
                global abort_update
                if abort_update:
                    self.reply(self.tr('aborted'))
                    return

        self.server.stop()
        self.server.wait_for_start()

        history_list.clear()
        for region in region_list:
            for region_file in region.to_file_list():
                try:
                    for world in self.config.world_names:
                        src_world_file = os.path.join(self.config.upstream_server_path, world)
                        dest_world_file = os.path.join(self.config.self_server_path, world)

                        src_file = os.path.join(str(src_world_file), region_file)
                        dest_file = os.path.join(str(dest_world_file), region_file)

                        if not os.path.isfile(src_file) and os.path.isfile(dest_file):
                            os.remove(dest_file)
                            self.server.logger.info('- *deleted* -> "{}"'.format(src_file, dest_file))
                        else:
                            self.server.logger.info('- "{}" -> "{}"'.format(src_file, dest_file))
                            shutil.copyfile(src_file, dest_file)
                except Exception as e:
                    flag = False
                    self.server.logger.error(e)
                    info = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                else:
                    flag = True
                    info = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                history_list.append((region, flag, info))

        region_list.clear()
        time.sleep(1)
        self.server.start()

    def confirm(self):
        global update_requested
        if not update_requested:
            reply_message(self.source, tr('command.confirm.no_confirm'))
        else:
            self.__update_region()

    def abort(self) -> None:
        global abort_update, update_requested
        abort_update = True
        update_requested = False
        self.reply(self.tr('abort'))
