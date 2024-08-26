from typing import Union, Dict

from mcdreforged.api.all import *

from mirror_world_updater import mcdr_globals
from mirror_world_updater.tasks.help import HelpMessage
from mirror_world_updater.tasks.__init__ import Task
from mirror_world_updater.text_component import TextComponent
from mirror_world_updater.utils import help_message_utils
from mirror_world_updater.utils.utils import mk_cmd


class Welcome(Task):
    COMMON_COMMANDS = ['', 'help', 'upstream', 'update', 'confirm', 'abort']

    def __init__(self, source: CommandSource):
        super().__init__(source)

    @property
    def id(self) -> str:
        return 'welcome'

    def reply(self, msg: Union[str, RTextBase], *, with_prefix: bool = False):
        super().reply(msg, with_prefix=with_prefix)

    def show_welcome(self) -> None:
        self.reply(TextComponent.title(self.tr(
            'title',
            name=RText(mcdr_globals.metadata.name, RColor.dark_aqua),
            version=RText(f'v{mcdr_globals.metadata.version}', RColor.gold),
        )))
        self.reply(mcdr_globals.metadata.get_description_rtext())

        self.reply(
            self.tr('common_commands').
            set_color(RColor.dark_aqua).
            h(self.tr('common_commands.hover', TextComponent.command('help'))).
            c(RAction.suggest_command, mk_cmd('help'))
        )
        helps = self.__generate_command_helps()
        for cmd in self.COMMON_COMMANDS:
            self.reply(helps[cmd])

        self.reply(self.tr('quick_actions.title').set_color(RColor.dark_aqua))
        with self.source.preferred_language_context():
            buttons = [
                RTextList('[', self.tr('quick_actions.update'), ']').
                set_color(RColor.green).
                h(TextComponent.command('update')).
                c(RAction.suggest_command, mk_cmd('update --confirm'))
            ]
        self.reply(RTextBase.join(' ', buttons))

    def __generate_command_helps(self) -> Dict[str, RTextBase]:
        msg = HelpMessage(self.source).tr('commands.content', prefix=self.__cmd_prefix)
        with self.source.preferred_language_context():
            return {h.literal: h.text for h in help_message_utils.parse_help_message(msg)}

    @property
    def __cmd_prefix(self) -> str:
        return self.config.prefix


