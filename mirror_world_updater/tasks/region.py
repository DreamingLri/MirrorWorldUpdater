import os
from abc import ABC
from typing import Union, Iterable, Optional
from mcdreforged.api.all import *

from mirror_world_updater import mcdr_globals
from mirror_world_updater.config.config import Config
from mirror_world_updater.tasks import Task


class RegionFile:
    def __init__(self, x: int, z: int, dim: int):
        self.x = x
        self.z = z
        self.dim = dim
        self.config: Optional[Config] = None

    def to_file_name(self):
        return 'r.{}.{}.mca'.format(self.x, self.z)

    def to_file_list(self):
        file_list = []
        folders = self.config.get().regions.dimension_region[str(self.dim)]
        if isinstance(folders, str):
            file_list.append(os.path.join(folders, self.to_file_name()))
        elif isinstance(folders, Iterable):
            for folder in folders:
                file_list.append(os.path.join(folder, self.to_file_name()))
        else:
            pass
        return file_list

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


class Region(Task, ABC):
    def __init__(self, source: CommandSource):
        super().__init__(source)
        self.region_list = []
        self.history_list = []

    @property
    def id(self) -> str:
        return 'region'

    def reply(self, msg: Union[str, RTextBase], *, with_prefix: bool = False):
        super().reply(msg, with_prefix=with_prefix)

    def add_region(self, region: RegionFile):
        if region in self.region_list:
            self.server.reply(self.tr('already_exist', RText(region.to_file_name(), RColor.green)))
        else:
            self.region_list.append(region)
            self.server.reply(self.tr('added', RText(region.to_file_name(), RColor.green)))

    @new_thread(mcdr_globals.metadata.name)
    def add_region_here(self):
        if isinstance(self.source, PlayerCommandSource):
            self.add_region(get_region_from_source(self.source))
        else:
            self.server.reply(self.tr('only_player'))

    def del_region(self, region: RegionFile):
        if region not in self.region_list:
            self.server.reply(self.tr('not_exist', RText(region.to_file_name(), RColor.green)))
        else:
            self.region_list.remove(region)
            self.server.reply(self.tr('deleted', RText(region.to_file_name(), RColor.green)))

    @new_thread(mcdr_globals.metadata.name)
    def del_region_here(self):
        if isinstance(self.source, PlayerCommandSource):
            self.del_region(get_region_from_source(self.source))
        else:
            self.server.reply(self.tr('only_player'))

    def clear_region_list(self):
        self.region_list.clear()
        self.server.reply(self.tr('cleared'))

    def show_region_list(self):
        pass

    def show_history(self):
        pass

    def update_region(self):
        pass
