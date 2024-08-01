from typing import List

from mcdreforged.api.all import *


class Paths(Serializable):
    server_list: List[str] = [
        'survival',
        'creative',
        'mirror'
    ]
    destination_world_directory: str = './server/world'
    current_upstream: str = 'survival'
    upstreams: str = "../survival/pb_files/prime_backup.db"
