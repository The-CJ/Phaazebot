from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from .main_discord import PhaazebotDiscord

import discord
from Utils.Classes.discordserversettings import DiscordServerSettings
from Utils.Classes.discordcommand import DiscordCommand
from Utils.Classes.discordleveluser import DiscordLevelUser
from Utils.Classes.discordquote import DiscordQuote
from Utils.Classes.discordassignrole import DiscordAssignRole

# db management
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

async def getDiscordServerQuotes(cls:"PhaazebotDiscord", guild_id:str, quote_id:str=None, random:bool=False, limit:int=0) -> list:
	"""
		Get server quotes, if quote_id = None, get all
		else only get one associated with the quote_id
		Returns a list of DiscordQuote().
	"""

	sql:str = """
		SELECT * FROM discord_quote
		WHERE discord_quote.guild_id = %s"""

	values:tuple = (guild_id,)

	if quote_id:
		sql += " AND discord_quote.id = %s"
		values += (quote_id,)

	if random:
		sql += " ORDER BY RAND()"
	else:
		sql += " ORDER BY id"

	if limit:
		sql += f" LIMIT {limit}"

	res:list = cls.BASE.PhaazeDB.query(sql, values)

	if res:
		return [DiscordQuote(x, guild_id) for x in res]

	else:
		return []

async def getDiscordServerAssignRoles(cls:"PhaazebotDiscord", guild_id:str, role_id:str=None, trigger:str=None) -> list:
	"""
		Get server assign roles, if role_id and trigger are None, get all
		else only get one associated with the role_id or trigger
		Returns a list of DiscordAssignRole().
	"""

	sql:str = """
		SELECT * FROM discord_giverole
		WHERE discord_giverole.guild_id = %s"""

	values:tuple = (guild_id,)

	if role_id:
		sql += " AND discord_giverole.role_id = %s"
		values += (role_id,)

	if trigger:
		sql += " AND discord_giverole.trigger = %s"
		values += (trigger,)

	res:list = cls.BASE.PhaazeDB.query(sql, values)

	if res:
		return [DiscordAssignRole(x, guild_id) for x in res]

	else:
		return []

# utility functions
def getDiscordMemberFromString(cls:"PhaazebotDiscord", Guild:discord.Guild, search:str or int, Message:discord.Message=None) -> discord.Member or None:
	"""
		Tryes to get a member from a guild, the search input may be,
		the user name or his id, else None is given

		Also can take Message mentions in account if Message given
	"""

	# mention
	if Message:
		if Message.mentions:
			return Message.mentions[0]

	search:str = str(search)
	Member:discord.Member = None

	# id
	if search.isdigit():
		Member = Guild.get_member(int(search))
		if Member: return Member

	# name
	Member = Guild.get_member_named(search)
	if Member:
		return Member

def getDiscordRoleFromString(cls:"PhaazebotDiscord", Guild:discord.Guild, search:str or int, Message:discord.Message=None) -> discord.Role or None:
	"""
		Tryes to get a role from a guild, the search input may be,
		the role name or the id, else None is given

		Also can take Message role mentions in account if Message given
	"""

	# mention
	if Message:
		if Message.role_mentions:
			return Message.role_mentions[0]

	search:str = str(search)

	for Ro in Guild.roles:
		if search.isdigit():
			if Ro.id == int(search): return Ro

		if Ro.name == search: return Ro
