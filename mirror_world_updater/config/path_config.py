from typing import List

from mcdreforged.api.all import *


class Paths(Serializable):
    server_list: List[str] = [
        'survival',
        'creative',
        'mirror'
    ]
    current_upstream: str = 'survival'
    # pb_path: str = '../survival/pb_files/'
    world_path: str = '../mirror/server/world'
    sync_path: str = '../survival/server/world'
