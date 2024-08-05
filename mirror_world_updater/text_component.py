from typing import Any
from mcdreforged.api.all import *

from mirror_world_updater.utils.utils import mk_cmd


class TextComponent:
    @classmethod
    def tr(cls, key, *args, **kwargs):
        from prime_backup.utils.mcdr_utils import tr
        return tr('text_component.' + key, *args, **kwargs)

    @classmethod
    def title(cls, text: Any) -> RTextBase:
        return RTextList(RText('======== ', RColor.gray), text, RText(' ========', RColor.gray))

    @classmethod
    def command(cls, s: str, *, color: RColor = RColor.gray, suggest: bool = False, run: bool = False,
                raw: bool = False) -> RTextBase:
        cmd = s if raw else mk_cmd(s)
        text = RText(cmd, color)
        if suggest:
            text.h(cls.tr('command.suggest', cmd)).c(RAction.suggest_command, cmd)
        elif run:
            text.h(cls.tr('command.run', cmd)).c(RAction.run_command, cmd)
        return text
