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

	result:list = await getDiscordServerLevels(cls, Message.guild.id, member_id=Message.author.id)

	if not result:
		LevelUser:DiscordLevelUser = await newUser(cls, Message.guild.id, Message.author.id)
	else:
		# there should be only on in the list
		LevelUser:DiscordLevelUser = result[0]

	print(LevelUser)

async def newUser(cls:"PhaazebotDiscord", server_id:str, member_id:str) -> DiscordLevelUser:

	res:dict = cls.BASE.PhaazeDB.insert(
		into = f"discord/level/level_{server_id}",
		content = {"member_id": member_id}
	)

	if res.get("status", "error") == "inserted":
		cls.BASE.Logger.debug(f"(Discord) New entry into levels: S:{server_id} M:{member_id}", require="discord:level")
		return DiscordLevelUser( {"member_id": member_id}, server_id )
	else:
		cls.BASE.Logger.critical(f"(Discord) New entry into levels failed: S:{server_id} M:{member_id}")
		raise RuntimeError("New entry into levels failed")
