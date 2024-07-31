from typing import Any
from mcdreforged.api.all import *


class TextComponent:
    @classmethod
    def tr(cls, key, *args, **kwargs):
        from mirror_world_updater.utils.mcdr_util import tr
        return tr('text_components.' + key, *args, **kwargs)

    @classmethod
    def title(cls, text: Any) -> RTextBase:
        return RTextList(RText('======== ', RColor.gray), text, RText(' ========', RColor.gray))
