from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from .main_discord import PhaazebotDiscord

import discord
from Utils.Classes.discordserversettings import DiscordServerSettings
from Utils.Classes.discordleveluser import DiscordLevelUser
from .utils import getDiscordServerLevels

async def checkLevel(cls:"PhaazebotDiscord", Message:discord.Message, ServerSettings:DiscordServerSettings) -> None:
	"""
		Run every time a user writes a message (not edited) and updates the exp.
	"""

	# TODO: Cooldown

	if Message.channel.id in ServerSettings.disable_chan_level: return
	if ServerSettings.owner_disable_level: return

	LevelUser:DiscordLevelUser = await getDiscordServerLevels(cls, Message.guild.id, member_id=Message.author.id)

	print(LevelUser)
