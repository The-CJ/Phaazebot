from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from .main_discord import PhaazebotDiscord

import discord
import json
from Utils.Classes.discordserversettings import DiscordServerSettings
from Utils.Classes.discordcommand import DiscordCommand
from Utils.Classes.discordleveluser import DiscordLevelUser

async def getDiscordSeverSettings(cls:"PhaazebotDiscord", origin:discord.Message or str or int, prevent_new:bool=False) -> DiscordServerSettings:
	"""
		Get server settings for a discord server/guild
		create new one if not prevented.
		Returns a DiscordServerSettings()
	"""
	if type(origin) is discord.Message:
		guild_id:str = str(origin.guild.id)

	elif type(origin) is str:
		guild_id:str = str(origin)

	else:
		guild_id:str = origin

	res:list = cls.BASE.PhaazeDB.query("""
		SELECT * FROM discord_setting
		WHERE discord_setting.guild_id = %s""",
		(guild_id,)
	)

	if res:
		return DiscordServerSettings( infos = res[0] )

	else:
		if prevent_new:
			return DiscordServerSettings()
		else:
			return await makeDiscordSeverSettings(cls, guild_id)

async def makeDiscordSeverSettings(cls:"PhaazebotDiscord", guild_id:str) -> DiscordServerSettings:
	"""
		Makes a new entry in the PhaazeDB for a discord server/guild.
		Returns a DiscordServerSettings()
	"""

	try:
		cls.BASE.PhaazeDB.query("""
			INSERT INTO discord_setting
			(guild_id)
			VALUES (%s)""",	(guild_id,)
		)
		cls.BASE.Logger.info(f"(Discord) New server settings DB entry: S:{guild_id}")
		return DiscordServerSettings( infos = {} )
	except:
		cls.BASE.Logger.critical(f"(Discord) New server settings failed: S:{guild_id}")
		raise RuntimeError("Creating new DB entry failed")

async def getDiscordServerCommands(cls:"PhaazebotDiscord", guild_id:str, trigger:str=None, command_id:str or int=None, order_str:str="ORDER BY id") -> list:
	"""
		Get custom commands from a discord server/guild, if trigger = None, get all.
		else only get one associated with trigger.

		If command_id != None: only get one command associated with id
		Returns a list of DiscordCommand()
	"""

	sql:str = """
		SELECT * FROM discord_command
		WHERE discord_command.guild_id = %s"""
	values:tuple = (guild_id,)

	if trigger:
		sql += " AND discord_command.trigger = %s"
		values += (trigger,)

	elif command_id:
		sql += " AND discord_command.id = %s"
		values += (command_id,)

	sql += f" {order_str}"

	res:list = cls.BASE.PhaazeDB.query(sql, values)

	if res:
		return [DiscordCommand(x, guild_id) for x in res]

	else:
		return []

async def getDiscordServerLevels(cls:"PhaazebotDiscord", guild_id:str, member_id:str=None) -> list:
	"""
		Get server levels, if member_id = None, get all
		else only get one associated with the member_id
		Returns a list of DiscordLevelUser().
	"""

	sql:str = """
		SELECT * FROM discord_level
		WHERE discord_level.guild_id = %s"""

	values:tuple = (guild_id,)


	if member_id:
		sql += " AND discord_level.member_id = %s"
		values += (member_id,)

	res:list = cls.BASE.PhaazeDB.query(sql, values)

	if res:
		return [DiscordLevelUser(x, guild_id) for x in res]

	else:
		return []

# quote get
