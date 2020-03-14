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
from Utils.Classes.discordblacklistedword import DiscordBlacklistedWord
from Utils.Classes.discordwhitelistedrole import DiscordWhitelistedRole
from Utils.Classes.discordwhitelistedlink import DiscordWhitelistedLink
from Utils.Classes.discordleveldisabledchannel import DiscordLevelDisabledChannel
from Utils.Classes.discordregulardisabledchannel import DiscordRegularDisabledChannel
from Utils.Classes.discordnormaldisabledchannel import DiscordNormalDisabledChannel
from Utils.Classes.discordquotedisabledchannel import DiscordQuoteDisabledChannel
from Utils.Classes.discordgameenablededchannel import DiscordGameEnabledChannel

# base settings/config management
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

# db data requests
async def getDiscordServerCommands(cls:"PhaazebotDiscord", guild_id:str, **search:dict) -> list:
	"""
	Get server commands.
	Returns a list of DiscordCommand()

	Optional keywords:
	------------------
	* trigger `str` : (Default: None)
	* command_id `str` or `int` : (Default: None)
	* show_nonactive `bool`: (Default: False)
	* order_str `str`: (Default: "ORDER BY id")
	* limit `int`: (Default: None)
	* offset `int`: (Default: 0)
	"""
	# unpack
	trigger:str = search.get("trigger", None)
	command_id:str or int = search.get("command_id", None)
	show_nonactive:bool = search.get("show_nonactive", False)
	order_str:str = search.get("order_str", "ORDER BY `id`")
	limit:int = search.get("limit", None)
	offset:int = search.get("offset", 0)

	# process
	sql:str = """
		SELECT * FROM `discord_command`
		WHERE `discord_command`.`guild_id` = %s"""
	values:tuple = ( str(guild_id), )

	if not show_nonactive:
		sql += " AND `discord_command`.`active` = 1"

	if command_id:
		sql += " AND `discord_command`.`id` = %s"
		values += ( int(command_id), )

	elif trigger:
		sql += " AND `discord_command`.`trigger` = %s"
		values += ( str(trigger), )

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

async def getDiscordServerUsers(cls:"PhaazebotDiscord", guild_id:str, **search:dict) -> list:
	"""
	Get server levels.
	Returns a list of DiscordUserStats().

	Optional keywords:
	------------------
	* member_id `str` : (Default: None)
	* edited `int`: (Default: 0) [0=all, 1=not edited, 2=only edited]
	* name `str`: (Default: None)
	* name_contains `str`: (Default: None) [DB uses LIKE]
	* order_str `str`: (Default: "ORDER BY id")
	* limit `int`: (Default: None)
	* offset `int`: (Default: 0)
	"""
	# unpack
	member_id:str = search.get("member_id", None)
	edited:int = search.get("order_str", 0)
	name:str = search.get("name", None)
	name_contains:str = search.get("name_contains", None)
	order_str:str = search.get("order_str", "ORDER BY id")
	limit:int = search.get("limit", None)
	offset:int = search.get("offset", 0)

	# process
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

	if name:
		sql += " AND (`discord_user`.`username` = %s OR `discord_user`.`nickname` = %s)"
		values += ( str(name), str(name) )

	if name_contains:
		name_contains = f"%{name_contains}%"
		sql += " AND (`discord_user`.`username` LIKE %s OR `discord_user`.`nickname` LIKE %s)"
		values += ( str(name_contains), str(name_contains) )

	if edited == 2:
		sql += " AND `discord_user`.`edited` = 1"
	if edited == 1:
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

async def getDiscordServerQuotes(cls:"PhaazebotDiscord", guild_id:str, **search:dict) -> list:
	"""
	Get server quotes.
	Returns a list of DiscordQuote().

	Optional keywords:
	------------------
	* quote_id `str` or `int`: (Default: None)
	* content `str`: (Default: None)
	* content_contains `str`: (Default: None) [DB uses LIKE]
	* random `bool`: (Default: False) [sql add: ORDER BY RAND()]
	* limit `int`: (Default: None)
	* offset `int`: (Default: 0)
	"""
	#unpack
	quote_id:str or int = search.get("quote_id", None)
	content:str = search.get("content", None)
	content_contains:str = search.get("content_contains", None)
	random:bool = search.get("random", False)
	limit:bool = search.get("limit", None)
	offset:bool = search.get("offset", 0)

	#process
	sql:str = """
		SELECT * FROM `discord_quote`
		WHERE `discord_quote`.`guild_id` = %s"""

	values:tuple = ( str(guild_id), )

	if quote_id:
		sql += " AND `discord_quote`.`id` = %s"
		values += ( int(quote_id), )

	if content:
		sql += " AND `discord_quote`.`content` = %s"
		values += ( str(content), )

	if content_contains:
		content_contains = f"%{content_contains}%"
		sql += " AND `discord_quote`.`content` LIKE %s"
		values += ( str(content_contains), )

	if random: sql += " ORDER BY RAND()"
	else: sql += " ORDER BY `id`"

	if limit:
		sql += f" LIMIT {limit}"
		if offset:
			sql += f" OFFSET {offset}"

	res:list = cls.BASE.PhaazeDB.selectQuery(sql, values)

	if res:
		return [DiscordQuote(x, guild_id) for x in res]

	else:
		return []

async def getDiscordServerTwitchAlerts(cls:"PhaazebotDiscord", guild_id:str, **search:dict) -> list:
	"""
	Get server twitch alerts.
	Returns a list of DiscordTwitchAlert().

	Optional keywords:
	------------------
	* alert_id `str` or `int`: (Default: None)
	* twitch_name `str`: (Default: None)
	* twitch_name_contains `str`: (Default: None) [DB uses LIKE]
	* limit `int`: (Default: None)
	* offset `int`: (Default: 0)
	"""
	# unpackt
	alert_id:str or int = search.get("alert_id", None)
	twitch_name:str = search.get("twitch_name", None)
	twitch_name_contains:str = search.get("twitch_name_contains", None)
	limit:int = search.get("limit", None)
	offset:int = search.get("offset", 0)

	# process
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
		values += ( int(alert_id), )

	if twitch_name:
		sql += " AND `twitch_user_name`.`user_name` = %s"
		values += ( str(twitch_name), )

	if twitch_name_contains:
		twitch_name_contains = f"%{twitch_name_contains}%"
		sql += " AND `twitch_user_name`.`user_name` LIKE %s"
		values += ( str(twitch_name_contains), )

	if limit:
		sql += f" LIMIT {limit}"
		if offset:
			sql += f" OFFSET {offset}"

	res:list = cls.BASE.PhaazeDB.selectQuery(sql, values)

	if res:
		return [DiscordTwitchAlert(x) for x in res]

	else:
		return []

async def getDiscordServerAssignRoles(cls:"PhaazebotDiscord", guild_id:str, **search:dict) -> list:
	"""
	Get server assign roles.
	Returns a list of DiscordAssignRole().

	Optional keywords:
	------------------
	* assignrole_id `str` or `int`: (Default: None)
	* role_id `str`: (Default: None)
	* trigger `str`: (Default: None)
	* order_str `str`: (Default: "ORDER BY id")
	* limit `int`: (Default: None)
	* offset `int`: (Default: 0)
	"""
	# unpackt
	assignrole_id:str or int = search.get("assignrole_id", None)
	role_id:str = search.get("role_id", None)
	trigger:str = search.get("trigger", None)
	order_str:str = search.get("order_str", "ORDER BY `id`")
	limit:int = search.get("limit", None)
	offset:int = search.get("offset", 0)

	# process
	sql:str = """
		SELECT * FROM `discord_assignrole`
		WHERE `discord_assignrole`.`guild_id` = %s"""

	values:tuple = ( str(guild_id), )

	if assignrole_id:
		sql += " AND `discord_assignrole`.`id` = %s"
		values += ( int(assignrole_id), )

	if role_id:
		sql += " AND `discord_assignrole`.`role_id` = %s"
		values += ( str(role_id), )

	if trigger:
		sql += " AND `discord_assignrole`.`trigger` = %s"
		values += ( str(trigger), )

	sql += f" {order_str}"

	if limit:
		sql += f" LIMIT {limit}"
		if offset:
			sql += f" OFFSET {offset}"

	res:list = cls.BASE.PhaazeDB.selectQuery(sql, values)

	if res:
		return [DiscordAssignRole(x, guild_id) for x in res]

	else:
		return []

async def getDiscordServerBlacklistedWords(cls:"PhaazebotDiscord", guild_id:str, **search:dict) -> list:
	"""
	Get all words that are blacklisted on the guild.
	Returns a list of DiscordBlacklistedWord().

	Optional keywords:
	------------------
	* word_id `str` or `int`: (Default: None)
	* word `str`: (Default: None)
	* order_str `str`: (Default: "ORDER BY id")
	* limit `int`: (Default: None)
	* offset `int`: (Default: 0)
	"""
	# unpack
	word_id:str or int = search.get("word_id", None)
	word:str = search.get("word", None)
	order_str:str = search.get("order_str", "ORDER BY `id`")
	limit:int = search.get("limit", None)
	offset:int = search.get("offset", 0)

	# process
	sql:str = """
		SELECT * FROM `discord_blacklist_blacklistword`
		WHERE `discord_blacklist_blacklistword`.`guild_id` = %s"""

	values:tuple = ( str(guild_id), )

	if word_id:
		sql += " AND `discord_blacklist_blacklistword`.`id` = %s"
		values += ( int(word_id), )

	if word:
		sql += " AND `discord_blacklist_blacklistword`.`word` = %s"
		values += ( str(word), )

	sql += f" {order_str}"

	if limit:
		sql += f" LIMIT {limit}"
		if offset:
			sql += f" OFFSET {offset}"

	res:list = cls.BASE.PhaazeDB.selectQuery(sql, values)

	if res:
		return [DiscordBlacklistedWord(x, guild_id) for x in res]

	else:
		return []

async def getDiscordServerExceptionRoles(cls:"PhaazebotDiscord", guild_id:str, **search:dict) -> list:
	"""
	Get exceptionroles for a guild.
	Returns a list of DiscordWhitelistedRole().

	Optional keywords:
	------------------
	* exceptionrole_id `str` or `int`: (Default: None)
	* role_id `str`: (Default: None)
	* order_str `str`: (Default: "ORDER BY id")
	* limit `int`: (Default: None)
	* offset `int`: (Default: 0)
	"""
	# unpack
	exceptionrole_id:str or int = search.get("exceptionrole_id", None)
	role_id:str = search.get("role_id", None)
	order_str:str = search.get("order_str", "ORDER BY `id`")
	limit:int = search.get("limit", None)
	offset:int = search.get("offset", 0)

	# process
	sql:str = """
		SELECT * FROM `discord_blacklist_whitelistrole`
		WHERE `discord_blacklist_whitelistrole`.`guild_id` = %s"""

	values:tuple = ( str(guild_id), )

	if exceptionrole_id:
		sql += " AND `discord_blacklist_whitelistrole`.`id` = %s"
		values += ( int(exceptionrole_id), )

	if role_id:
		sql += " AND `discord_blacklist_whitelistrole`.`role_id` = %s"
		values += ( str(role_id), )

	sql += f" {order_str}"

	if limit:
		sql += f" LIMIT {limit}"
		if offset:
			sql += f" OFFSET {offset}"

	res:list = cls.BASE.PhaazeDB.selectQuery(sql, values)

	if res:
		return [DiscordWhitelistedRole(x, guild_id) for x in res]

	else:
		return []

async def getDiscordServerWhitelistedLinks(cls:"PhaazebotDiscord", guild_id:str, **search:dict) -> list:
	"""
	Get whitelisted links for a guild.
	Returns a list of DiscordWhitelistedLink().

	Optional keywords:
	------------------
	* link_id `str` or `int`: (Default: None)
	* link `str`: (Default: None)
	* order_str `str`: (Default: "ORDER BY id")
	* limit `int`: (Default: None)
	* offset `int`: (Default: 0)
	"""
	# unpack
	link_id:str or int = search.get("link_id", None)
	link:str = search.get("link", None)
	order_str:str = search.get("order_str", "ORDER BY `id`")
	limit:int = search.get("limit", None)
	offset:int = search.get("offset", 0)

	# process
	sql:str = """
		SELECT * FROM `discord_blacklist_whitelistlink`
		WHERE `discord_blacklist_whitelistlink`.`guild_id` = %s"""

	values:tuple = ( str(guild_id), )

	if link_id:
		sql += " AND `discord_blacklist_whitelistlink`.`id` = %s"
		values += ( int(link_id), )

	if link:
		sql += " AND `discord_blacklist_whitelistlink`.`link` = %s"
		values += ( str(link), )

	sql += f" {order_str}"

	if limit:
		sql += f" LIMIT {limit}"
		if offset:
			sql += f" OFFSET {offset}"

	res:list = cls.BASE.PhaazeDB.selectQuery(sql, values)

	if res:
		return [DiscordWhitelistedLink(x, guild_id) for x in res]

	else:
		return []

async def getDiscordServerLevelDisabledChannels(cls:"PhaazebotDiscord", guild_id:str, **search:dict) -> list:
	"""
	Get channels where levels are disabled for a guild.
	Returns a list of DiscordLevelDisabledChannel().

	Optional keywords:
	------------------
	* entry_id `str` or `int`: (Default: None)
	* channel_id `str`: (Default: None)
	* order_str `str`: (Default: "ORDER BY id")
	* limit `int`: (Default: None)
	* offset `int`: (Default: 0)
	"""
	# unpack
	entry_id:str or int = search.get("entry_id", None)
	channel_id:str = search.get("channel_id", None)
	order_str:str = search.get("order_str", "ORDER BY `id`")
	limit:int = search.get("limit", None)
	offset:int = search.get("offset", 0)

	# process
	sql:str = """
		SELECT * FROM `discord_disabled_levelchannel`
		WHERE `discord_disabled_levelchannel`.`guild_id` = %s"""

	values:tuple = ( str(guild_id), )

	if entry_id:
		sql += " AND `discord_disabled_levelchannel`.`id` = %s"
		values += ( int(entry_id), )

	if channel_id:
		sql += " AND `discord_disabled_levelchannel`.`channel_id` = %s"
		values += ( str(channel_id), )

	sql += f" {order_str}"

	if limit:
		sql += f" LIMIT {limit}"
		if offset:
			sql += f" OFFSET {offset}"

	res:list = cls.BASE.PhaazeDB.selectQuery(sql, values)

	if res:
		return [DiscordLevelDisabledChannel(x, guild_id) for x in res]

	else:
		return []

async def getDiscordServerRegularDisabledChannels(cls:"PhaazebotDiscord", guild_id:str, **search:dict) -> list:
	"""
	Get channels where regular commands (requirement = regular) are disabled for a guild.
	Returns a list of DiscordRegularDisabledChannel().

	Optional keywords:
	------------------
	* entry_id `str` or `int`: (Default: None)
	* channel_id `str`: (Default: None)
	* order_str `str`: (Default: "ORDER BY id")
	* limit `int`: (Default: None)
	* offset `int`: (Default: 0)
	"""
	# unpack
	entry_id:str or int = search.get("entry_id", None)
	channel_id:str = search.get("channel_id", None)
	order_str:str = search.get("order_str", "ORDER BY `id`")
	limit:int = search.get("limit", None)
	offset:int = search.get("offset", 0)

	# process
	sql:str = """
		SELECT * FROM `discord_disabled_regularchannel`
		WHERE `discord_disabled_regularchannel`.`guild_id` = %s"""

	values:tuple = ( str(guild_id), )

	if entry_id:
		sql += " AND `discord_disabled_regularchannel`.`id` = %s"
		values += ( int(entry_id), )

	if channel_id:
		sql += " AND `discord_disabled_regularchannel`.`channel_id` = %s"
		values += ( str(channel_id), )

	sql += f" {order_str}"

	if limit:
		sql += f" LIMIT {limit}"
		if offset:
			sql += f" OFFSET {offset}"

	res:list = cls.BASE.PhaazeDB.selectQuery(sql, values)

	if res:
		return [DiscordRegularDisabledChannel(x, guild_id) for x in res]

	else:
		return []

async def getDiscordServerNormalDisabledChannels(cls:"PhaazebotDiscord", guild_id:str, **search:dict) -> list:
	"""
	Get channels where normal commands (requirement = everyone) are disabled for a guild.
	Returns a list of DiscordNormalDisabledChannel().

	Optional keywords:
	------------------
	* entry_id `str` or `int`: (Default: None)
	* channel_id `str`: (Default: None)
	* order_str `str`: (Default: "ORDER BY id")
	* limit `int`: (Default: None)
	* offset `int`: (Default: 0)
	"""
	# unpack
	entry_id:str or int = search.get("entry_id", None)
	channel_id:str = search.get("channel_id", None)
	order_str:str = search.get("order_str", "ORDER BY `id`")
	limit:int = search.get("limit", None)
	offset:int = search.get("offset", 0)

	# process
	sql:str = """
		SELECT * FROM `discord_disabled_normalchannel`
		WHERE `discord_disabled_normalchannel`.`guild_id` = %s"""

	values:tuple = ( str(guild_id), )

	if entry_id:
		sql += " AND `discord_disabled_normalchannel`.`id` = %s"
		values += ( int(entry_id), )

	if channel_id:
		sql += " AND `discord_disabled_normalchannel`.`channel_id` = %s"
		values += ( str(channel_id), )

	sql += f" {order_str}"

	if limit:
		sql += f" LIMIT {limit}"
		if offset:
			sql += f" OFFSET {offset}"

	res:list = cls.BASE.PhaazeDB.selectQuery(sql, values)

	if res:
		return [DiscordNormalDisabledChannel(x, guild_id) for x in res]

	else:
		return []

async def getDiscordServerQuoteDisabledChannels(cls:"PhaazebotDiscord", guild_id:str, **search:dict) -> list:
	"""
	Get channels where quotes are disabled for a guild.
	Returns a list of DiscordQuoteDisabledChannel().

	Optional keywords:
	------------------
	* entry_id `str` or `int`: (Default: None)
	* channel_id `str`: (Default: None)
	* order_str `str`: (Default: "ORDER BY id")
	* limit `int`: (Default: None)
	* offset `int`: (Default: 0)
	"""
	# unpack
	entry_id:str or int = search.get("entry_id", None)
	channel_id:str = search.get("channel_id", None)
	order_str:str = search.get("order_str", "ORDER BY `id`")
	limit:int = search.get("limit", None)
	offset:int = search.get("offset", 0)

	# process
	sql:str = """
		SELECT * FROM `discord_disabled_quotechannel`
		WHERE `discord_disabled_quotechannel`.`guild_id` = %s"""

	values:tuple = ( str(guild_id), )

	if entry_id:
		sql += " AND `discord_disabled_quotechannel`.`id` = %s"
		values += ( int(entry_id), )

	if channel_id:
		sql += " AND `discord_disabled_quotechannel`.`channel_id` = %s"
		values += ( str(channel_id), )

	sql += f" {order_str}"

	if limit:
		sql += f" LIMIT {limit}"
		if offset:
			sql += f" OFFSET {offset}"

	res:list = cls.BASE.PhaazeDB.selectQuery(sql, values)

	if res:
		return [DiscordQuoteDisabledChannel(x, guild_id) for x in res]

	else:
		return []

async def getDiscordServerGameEnabledChannels(cls:"PhaazebotDiscord", guild_id:str, **search:dict) -> list:
	"""
	Get channels where games are enabled for a guild.
	Returns a list of DiscordGameEnabledChannel().

	Optional keywords:
	------------------
	* entry_id `str` or `int`: (Default: None)
	* channel_id `str`: (Default: None)
	* order_str `str`: (Default: "ORDER BY id")
	* limit `int`: (Default: None)
	* offset `int`: (Default: 0)
	"""
	# unpack
	entry_id:str or int = search.get("entry_id", None)
	channel_id:str = search.get("channel_id", None)
	order_str:str = search.get("order_str", "ORDER BY `id`")
	limit:int = search.get("limit", None)
	offset:int = search.get("offset", 0)

	# process
	sql:str = """
		SELECT * FROM `discord_enabled_gamechannel`
		WHERE `discord_enabled_gamechannel`.`guild_id` = %s"""

	values:tuple = ( str(guild_id), )

	if entry_id:
		sql += " AND `discord_enabled_gamechannel`.`id` = %s"
		values += ( int(entry_id), )

	if channel_id:
		sql += " AND `discord_enabled_gamechannel`.`channel_id` = %s"
		values += ( str(channel_id), )

	sql += f" {order_str}"

	if limit:
		sql += f" LIMIT {limit}"
		if offset:
			sql += f" OFFSET {offset}"

	res:list = cls.BASE.PhaazeDB.selectQuery(sql, values)

	if res:
		return [DiscordGameEnabledChannel(x, guild_id) for x in res]

	else:
		return []

# db total counter
async def getDiscordServerCommandsAmount(cls:"PhaazebotDiscord", guild_id:str, where:str="1=1", where_values:tuple=()) -> int:

	sql:str = f"""
		SELECT COUNT(*) AS `I` FROM `discord_command`
		WHERE `discord_command`.`guild_id` = %s AND {where}"""

	values:tuple = (guild_id,) + where_values

	res:list = cls.BASE.PhaazeDB.selectQuery(sql, values)

	return res[0]["I"]

async def getDiscordServerUserAmount(cls:"PhaazebotDiscord", guild_id:str, where:str="1=1", where_values:tuple=()) -> int:

	sql:str = f"""
		SELECT COUNT(*) AS `I` FROM `discord_user`
		WHERE `discord_user`.`on_server` = 1 AND `discord_user`.`guild_id` = %s AND {where}"""

	values:tuple = (guild_id,) + where_values

	res:list = cls.BASE.PhaazeDB.selectQuery(sql, values)

	return res[0]["I"]

async def getDiscordServerQuotesAmount(cls:"PhaazebotDiscord", guild_id:str, where:str="1=1", where_values:tuple=()) -> int:

	sql:str = f"""
		SELECT COUNT(*) AS `I` FROM `discord_quote`
		WHERE `discord_quote`.`guild_id` = %s AND {where}"""

	values:tuple = (guild_id,) + where_values

	res:list = cls.BASE.PhaazeDB.selectQuery(sql, values)

	return res[0]["I"]

async def getDiscordServerTwitchAlertsAmount(cls:"PhaazebotDiscord", guild_id:str, where:str="1=1", where_values:tuple=()) -> int:

	sql:str = f"""
		SELECT COUNT(*) AS `I` FROM `discord_twitch_alert`
		WHERE `discord_twitch_alert`.`discord_guild_id` = %s AND {where}"""

	values:tuple = (guild_id,) + where_values

	res:list = cls.BASE.PhaazeDB.selectQuery(sql, values)

	return res[0]["I"]

async def getDiscordServerAssignRoleAmount(cls:"PhaazebotDiscord", guild_id:str, where:str="1=1", where_values:tuple=()) -> int:

	sql:str = f"""
		SELECT COUNT(*) AS `I` FROM `discord_assignrole`
		WHERE `discord_assignrole`.`guild_id` = %s AND {where}"""

	values:tuple = ( str(guild_id), ) + where_values

	res:list = cls.BASE.PhaazeDB.selectQuery(sql, values)

	return res[0]["I"]

async def getDiscordServerBlacklistedWordAmount(cls:"PhaazebotDiscord", guild_id:str, where:str="1=1", where_values:tuple=()) -> int:

	sql:str = f"""
		SELECT COUNT(*) AS `I` FROM `discord_blacklist_blacklistword`
		WHERE `discord_blacklist_blacklistword`.`guild_id` = %s AND {where}"""

	values:tuple = ( str(guild_id), ) + where_values

	res:list = cls.BASE.PhaazeDB.selectQuery(sql, values)

	return res[0]["I"]

async def getDiscordServerExceptionRoleAmount(cls:"PhaazebotDiscord", guild_id:str, where:str="1=1", where_values:tuple=()) -> int:

	sql:str = f"""
		SELECT COUNT(*) AS `I` FROM `discord_blacklist_whitelistrole`
		WHERE `discord_blacklist_whitelistrole`.`guild_id` = %s AND {where}"""

	values:tuple = ( str(guild_id), ) + where_values

	res:list = cls.BASE.PhaazeDB.selectQuery(sql, values)

	return res[0]["I"]

async def getDiscordServerWhitelistedLinkAmount(cls:"PhaazebotDiscord", guild_id:str, where:str="1=1", where_values:tuple=()) -> int:

	sql:str = f"""
		SELECT COUNT(*) AS `I` FROM `discord_blacklist_whitelistlink`
		WHERE `discord_blacklist_whitelistlink`.`guild_id` = %s AND {where}"""

	values:tuple = ( str(guild_id), ) + where_values

	res:list = cls.BASE.PhaazeDB.selectQuery(sql, values)

	return res[0]["I"]

async def getDiscordServerLevelDisabledChannelAmount(cls:"PhaazebotDiscord", guild_id:str, where:str="1=1", where_values:tuple=()) -> int:

	sql:str = f"""
		SELECT COUNT(*) AS `I` FROM `discord_disabled_levelchannel`
		WHERE `discord_disabled_levelchannel`.`guild_id` = %s AND {where}"""

	values:tuple = ( str(guild_id), ) + where_values

	res:list = cls.BASE.PhaazeDB.selectQuery(sql, values)

	return res[0]["I"]

async def getDiscordServerRegularDisabledChannelAmount(cls:"PhaazebotDiscord", guild_id:str, where:str="1=1", where_values:tuple=()) -> int:

	sql:str = f"""
		SELECT COUNT(*) AS `I` FROM `discord_disabled_regularchannel`
		WHERE `discord_disabled_regularchannel`.`guild_id` = %s AND {where}"""

	values:tuple = ( str(guild_id), ) + where_values

	res:list = cls.BASE.PhaazeDB.selectQuery(sql, values)

	return res[0]["I"]

async def getDiscordServerNormalDisabledChannelAmount(cls:"PhaazebotDiscord", guild_id:str, where:str="1=1", where_values:tuple=()) -> int:

	sql:str = f"""
		SELECT COUNT(*) AS `I` FROM `discord_disabled_normalchannel`
		WHERE `discord_disabled_normalchannel`.`guild_id` = %s AND {where}"""

	values:tuple = ( str(guild_id), ) + where_values

	res:list = cls.BASE.PhaazeDB.selectQuery(sql, values)

	return res[0]["I"]

async def getDiscordServerQuoteDisabledChannelAmount(cls:"PhaazebotDiscord", guild_id:str, where:str="1=1", where_values:tuple=()) -> int:

	sql:str = f"""
		SELECT COUNT(*) AS `I` FROM `discord_disabled_quotechannel`
		WHERE `discord_disabled_quotechannel`.`guild_id` = %s AND {where}"""

	values:tuple = ( str(guild_id), ) + where_values

	res:list = cls.BASE.PhaazeDB.selectQuery(sql, values)

	return res[0]["I"]

async def getDiscordServerGameEnabledChannelAmount(cls:"PhaazebotDiscord", guild_id:str, where:str="1=1", where_values:tuple=()) -> int:

	sql:str = f"""
		SELECT COUNT(*) AS `I` FROM `discord_enabled_gamechannel`
		WHERE `discord_enabled_gamechannel`.`guild_id` = %s AND {where}"""

	values:tuple = ( str(guild_id), ) + where_values

	res:list = cls.BASE.PhaazeDB.selectQuery(sql, values)

	return res[0]["I"]

# utility functions
def getDiscordChannelFromString(cls:"PhaazebotDiscord", Guild:discord.Guild, search:str or int, Message:discord.Message=None, required_type:str=None) -> discord.abc.GuildChannel or None:
	"""
		Tryes to get a channel from a guild, the search input may be,
		the channel name or the id, else None is given

		Also can take Message mentions in account if Message given
	"""
	SearchChannel:discord.abc.GuildChannel = None

	search_str:str = str(search)
	search_id:int = 0
	if search_str.isdigit():
		search_id = int(search)

	# mention
	if Message:
		if Message.channel_mentions:
			SearchChannel = Message.channel_mentions[0]

	for Chan in Guild.channels:
		if (Chan.name == search_str) or (Chan.id == search_id):
			SearchChannel = Chan
			break

	# type check
	if required_type:
		if required_type == "text" and type(SearchChannel) is not discord.TextChannel:
			return None
		if required_type == "voice" and type(SearchChannel) is not discord.VoiceChannel:
			return None
		if required_type == "category" and type(SearchChannel) is not discord.CategoryChannel:
			return None

	return SearchChannel

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
