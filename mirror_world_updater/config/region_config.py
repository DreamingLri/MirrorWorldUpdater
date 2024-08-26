from typing import Dict, Union, List

from mcdreforged.utils.serializer import Serializable


class RegionConfig(Serializable):
    dimension_region: Dict[str, Union[str, List[str]]] = {
        '-1': ['DIM-1/region', 'DIM-1/poi'],
        '0': ['region', 'poi'],
        '1': ['DIM1/region', 'DIM1/poi']
    }
