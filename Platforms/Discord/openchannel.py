from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from .main_discord import PhaazebotDiscord

import discord
from Utils.Classes.discordserversettings import DiscordServerSettings
from .utils import getDiscordSeverSettings

async def openChannel(cls:"PhaazebotDiscord", Message:discord.Message) -> discord.Message:

	# get server settings
	ServerSettings:DiscordServerSettings = await getDiscordSeverSettings(cls, Message)

	print(ServerSettings)
	print(Message.guild.id)

	pass
