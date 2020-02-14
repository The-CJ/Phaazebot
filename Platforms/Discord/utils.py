from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from .main_discord import PhaazebotDiscord

import discord
from Utils.Classes.discordserversettings import DiscordServerSettings
from Utils.Classes.discordcommand import DiscordCommand
from Utils.Classes.discorduserstats import DiscordUserStats
from Utils.Classes.discordquote import DiscordQuote
from Utils.Classes.discordassignrole import DiscordAssignRole
from Utils.Classes.discordtwitchalert import DiscordTwitchAlert

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

	res:list = cls.BASE.PhaazeDB.selectQuery("""
		SELECT
			`discord_setting`.*,
			(SELECT GROUP_CONCAT(`discord_blacklist_whitelistrole`.`role_id` SEPARATOR ',') FROM `discord_blacklist_whitelistrole` WHERE `discord_blacklist_whitelistrole`.`guild_id` = `discord_setting`.`guild_id`)
				AS `blacklist_whitelistroles`,
			(SELECT GROUP_CONCAT(`discord_blacklist_whitelistlink`.`link` SEPARATOR ";;;") FROM `discord_blacklist_whitelistlink` WHERE `discord_blacklist_whitelistlink`.`guild_id` = `discord_setting`.`guild_id`)
				AS `blacklist_whitelistlinks`,
			(SELECT GROUP_CONCAT(`discord_blacklist_blacklistword`.`word` SEPARATOR ";;;") FROM `discord_blacklist_blacklistword` WHERE `discord_blacklist_blacklistword`.`guild_id` = `discord_setting`.`guild_id`)
				AS `blacklist_blacklistwords`,
			(SELECT GROUP_CONCAT(`discord_disabled_levelchannel`.`channel_id` SEPARATOR ',') FROM `discord_disabled_levelchannel` WHERE `discord_disabled_levelchannel`.`guild_id` = `discord_setting`.`guild_id`)
				AS `disabled_levelchannels`,
			(SELECT GROUP_CONCAT(`discord_disabled_quotechannel`.`channel_id` SEPARATOR ',') FROM `discord_disabled_quotechannel` WHERE `discord_disabled_quotechannel`.`guild_id` = `discord_setting`.`guild_id`)
				AS `disabled_quotechannels`,
			(SELECT GROUP_CONCAT(`discord_disabled_normalchannel`.`channel_id` SEPARATOR ',') FROM `discord_disabled_normalchannel` WHERE `discord_disabled_normalchannel`.`guild_id` = `discord_setting`.`guild_id`)
				AS `disabled_normalchannels`,
			(SELECT GROUP_CONCAT(`discord_disabled_regularchannel`.`channel_id` SEPARATOR ',') FROM `discord_disabled_regularchannel` WHERE `discord_disabled_regularchannel`.`guild_id` = `discord_setting`.`guild_id`)
				AS `disabled_regularchannels`,
			(SELECT GROUP_CONCAT(`discord_enabled_gamechannel`.`channel_id` SEPARATOR ',') FROM `discord_enabled_gamechannel` WHERE `discord_enabled_gamechannel`.`guild_id` = `discord_setting`.`guild_id`)
				AS `enabled_gamechannels`,
			(SELECT GROUP_CONCAT(`discord_enabled_nsfwchannel`.`channel_id` SEPARATOR ',') FROM `discord_enabled_nsfwchannel` WHERE `discord_enabled_nsfwchannel`.`guild_id` = `discord_setting`.`guild_id`)
				AS `enabled_nsfwchannels`

		FROM `discord_setting`
		WHERE `discord_setting`.`guild_id` = %s
		GROUP BY `discord_setting`.`guild_id`""",
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
		cls.BASE.PhaazeDB.insertQuery(
			table = "discord_setting",
			content = dict(guild_id = guild_id)
		)

		cls.BASE.Logger.info(f"(Discord) New server settings DB entry: S:{guild_id}")
		return DiscordServerSettings( infos = {} )
	except:
		cls.BASE.Logger.critical(f"(Discord) New server settings failed: S:{guild_id}")
		raise RuntimeError("Creating new DB entry failed")

async def getDiscordServerCommands(cls:"PhaazebotDiscord", guild_id:str, trigger:str=None, command_id:str or int=None, order_str:str="ORDER BY id", show_nonactive:bool=False, limit:int=0, offset:int=0) -> list:
	"""
		Get custom commands from a discord server/guild, if trigger = None, get all.
		else only get one associated with trigger.

		If command_id != None: only get one command associated with id
		Returns a list of DiscordCommand()
	"""

	sql:str = """
		SELECT * FROM `discord_command`
		WHERE `discord_command`.`guild_id` = %s"""
	values:tuple = ( str(guild_id), )

	if not show_nonactive:
		sql += " AND `discord_command`.`active` = 1"

	if command_id:
		sql += " AND `discord_command`.`id` = %s"
		values += (command_id,)

	elif trigger:
		sql += " AND `discord_command`.`trigger` = %s"
		values += (trigger,)

	sql += f" {order_str}"

	if limit:
		sql += f" LIMIT {limit}"
		if offset:
			sql += f" OFFSET {offset}"

	res:list = cls.BASE.PhaazeDB.selectQuery(sql, values)

	if res:
		return [DiscordCommand(x, guild_id) for x in res]

	else:
		return []

async def getDiscordServerUsers(cls:"PhaazebotDiscord", guild_id:str, member_id:str=None, order_str:str="ORDER BY `id`", limit:int=0, offset:int=0, edited:int=0, name_contains:str=None) -> list:
	"""
		Get server levels, if member_id = None, get all
		else only get one associated with the member_id
		Returns a list of DiscordUserStats().

		guild_id [required]
		member_id : limits results to 1
		order_str : order at end of sql
		limit : max return list length
		offset : list offset
		edited : select (0 = all), (1 = not edited), (2 = only edited)
		name_contains : username or nickname LIKE X
	"""

	sql:str = """
		WITH `discord_user` AS (
			SELECT
				`discord_user`.*,
				GROUP_CONCAT(`discord_user_medal`.`name` SEPARATOR ';;;') AS `medals`,
				RANK() OVER (ORDER BY `exp` DESC) AS `rank`
			FROM `discord_user`
			LEFT JOIN `discord_user_medal`
				ON `discord_user_medal`.`guild_id` = `discord_user`.`guild_id`
					AND `discord_user_medal`.`member_id` = `discord_user`.`member_id`
			WHERE `discord_user`.`on_server` = 1
				AND `discord_user`.`guild_id` = %s
			GROUP BY `discord_user`.`guild_id`, `discord_user`.`member_id`
		)
		SELECT * FROM `discord_user` WHERE 1=1"""

	values:tuple = ( str(guild_id), )

	if member_id:
		sql += " AND `discord_user`.`member_id` = %s"
		values += ( str(member_id), )

	if name_contains:
		name_contains = f"%{name_contains}%"
		sql += " AND (`discord_user`.`username` LIKE %s OR `discord_user`.`nickname` LIKE %s)"
		values += (name_contains, name_contains)

	if edited == 2:
		sql += " AND `discord_user`.`edited` = 1"
	elif edited == 1:
		sql += " AND `discord_user`.`edited` = 0"

	sql += f" {order_str}"

	if limit:
		sql += f" LIMIT {limit}"
		if offset:
			sql += f" OFFSET {offset}"

	res:list = cls.BASE.PhaazeDB.selectQuery(sql, values)

	if res:
		return [DiscordUserStats(x, guild_id) for x in res]

	else:
		return []

async def getDiscordServerUserAmount(cls:"PhaazebotDiscord", guild_id:str, where:str="1=1", where_values:tuple=()) -> int:

	sql:str = f"""
		SELECT COUNT(*) AS `I` FROM `discord_user`
		WHERE `discord_user`.`on_server` = 1 AND `discord_user`.`guild_id` = %s AND {where}"""

	values:tuple = (guild_id,) + where_values

	res:list = cls.BASE.PhaazeDB.selectQuery(sql, values)

	return res[0]["I"]

async def getDiscordServerQuotes(cls:"PhaazebotDiscord", guild_id:str, quote_id:int=None, random:bool=False, limit:int=0, offset:int=0) -> list:
	"""
		Get server quotes, if quote_id = None, get all
		else only get one associated with the quote_id
		Returns a list of DiscordQuote().
	"""

	sql:str = """
		SELECT * FROM `discord_quote`
		WHERE `discord_quote`.`guild_id` = %s"""

	values:tuple = ( str(guild_id), )

	if quote_id:
		sql += " AND `discord_quote`.`id` = %s"
		values += (quote_id,)

	if random:
		sql += " ORDER BY RAND()"
	else:
		sql += " ORDER BY `id`"

	if limit:
		sql += f" LIMIT {limit}"
		if offset:
			sql += f" OFFSET {offset}"

	res:list = cls.BASE.PhaazeDB.selectQuery(sql, values)

	if res:
		return [DiscordQuote(x, guild_id) for x in res]

	else:
		return []

async def getDiscordTwitchAlerts(cls:"PhaazebotDiscord", guild_id:str, alert_id:int=None, limit:int=0, offset:int=0) -> list:
	"""
		Get server discord alerts, if alert_id = None, get all
		else only get one associated with the alert_id
		Returns a list of DiscordTwitchAlert().
	"""

	sql:str = """
		SELECT
			`discord_twitch_alert`.*,
			`twitch_user_name`.`user_name` AS `twitch_channel_name`
		FROM `discord_twitch_alert`
		LEFT JOIN `twitch_user_name`
			ON `discord_twitch_alert`.`twitch_channel_id` = `twitch_user_name`.`user_id`
		WHERE `discord_twitch_alert`.`discord_guild_id` = %s"""

	values:tuple = ( str(guild_id), )

	if alert_id:
		sql += " AND `discord_twitch_alert`.`id` = %s"
		values += (alert_id,)

	if limit:
		sql += f" LIMIT {limit}"
		if offset:
			sql += f" OFFSET {offset}"

	res:list = cls.BASE.PhaazeDB.selectQuery(sql, values)

	if res:
		return [DiscordTwitchAlert(x) for x in res]

	else:
		return []

async def getDiscordTwitchAlertsAmount(cls:"PhaazebotDiscord", guild_id:str, where:str="1=1", where_values:tuple=()) -> int:

	sql:str = f"""
		SELECT COUNT(*) AS `I` FROM `discord_twitch_alert`
		WHERE `discord_twitch_alert`.`discord_guild_id` = %s AND {where}"""

	values:tuple = (guild_id,) + where_values

	res:list = cls.BASE.PhaazeDB.selectQuery(sql, values)

	return res[0]["I"]

async def getDiscordServerAssignRoles(cls:"PhaazebotDiscord", guild_id:str, role_id:int=None, assignrole_id:int=None, trigger:str=None, order_str:str="ORDER BY `id`", limit:int=0, offset:int=0) -> list:
	"""
		Get server assign roles, if role_id and trigger are None, get all
		else only get one associated with the role_id or trigger
		Returns a list of DiscordAssignRole().
	"""

	sql:str = """
		SELECT * FROM `discord_assignrole`
		WHERE `discord_assignrole`.`guild_id` = %s"""

	values:tuple = ( str(guild_id), )

	if role_id:
		sql += " AND `discord_assignrole`.`role_id` = %s"
		values += (role_id,)

	if assignrole_id:
		sql += " AND `discord_assignrole`.`id` = %s"
		values += (assignrole_id,)

	if trigger:
		sql += " AND `discord_assignrole`.`trigger` = %s"
		values += (trigger,)

	sql += f" {order_str}"

	if limit:
		sql += f" LIMIT {limit}"
		if offset:
			sql += f" OFFSET {offset}"

	res:list = cls.BASE.PhaazeDB.query(sql, values)

	if res:
		return [DiscordAssignRole(x, guild_id) for x in res]

	else:
		return []

async def getDiscordServerAssignRoleAmount(cls:"PhaazebotDiscord", guild_id:str, where:str="1=1", where_values:tuple=()) -> int:

	sql:str = f"""
		SELECT COUNT(*) AS `I` FROM `discord_assignrole`
		WHERE `discord_assignrole`.`guild_id` = %s AND {where}"""

	values:tuple = ( str(guild_id), ) + where_values

	res:list = cls.BASE.PhaazeDB.selectQuery(sql, values)

	return res[0]["I"]

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
