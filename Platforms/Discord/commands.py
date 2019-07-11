from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from .main_discord import PhaazebotDiscord

import discord
from Utils.Classes.discordserversettings import DiscordServerSettings
from Utils.Classes.discordcommandcontext import DiscordCommandContext

async def checkCommands(cls:"PhaazebotDiscord", Message:discord.Message, ServerSettings:DiscordServerSettings) -> None:

	CommandContext:DiscordCommandContext = DiscordCommandContext(cls, Message)
	await CommandContext.check()
