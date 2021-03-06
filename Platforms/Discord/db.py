from typing import TYPE_CHECKING, List, Union, Optional
if TYPE_CHECKING:
	from Platforms.Discord.main_discord import PhaazebotDiscord

import discord
from Utils.Classes.discordserversettings import DiscordServerSettings
from Utils.Classes.discordcommand import DiscordCommand
from Utils.Classes.discorduserstats import DiscordUserStats
from Utils.Classes.discordregular import DiscordRegular
from Utils.Classes.discordusermedal import DiscordUserMedal
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
from Utils.Classes.discordnsfwenablededchannel import DiscordNsfwEnabledChannel
from Utils.Classes.discordlog import DiscordLog

# discord_setting
async def getDiscordSeverSettings(cls:"PhaazebotDiscord", origin:Union[discord.Message, str, int], prevent_new:bool=False) -> DiscordServerSettings:
	"""
	Get server settings for a discord server/guild
	create new one if not prevented.
	Returns a DiscordServerSettings()
	"""
	if type(origin) is discord.Message:
		guild_id:str = str(origin.guild.id)

	elif type(origin) is int:
		guild_id:str = str(origin)

	else:
		guild_id:str = origin

	res:List[dict] = cls.BASE.PhaazeDB.selectQuery("""
		SELECT
			`discord_setting`.*,
			(SELECT GROUP_CONCAT(`discord_blacklist_whitelistrole`.`role_id` SEPARATOR ',') FROM `discord_blacklist_whitelistrole` WHERE `discord_blacklist_whitelistrole`.`guild_id` = `discord_setting`.`guild_id`)
				AS `blacklist_whitelistroles`,
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
				AS `enabled_nsfwchannels`,
			(SELECT GROUP_CONCAT(`discord_blacklist_whitelistlink`.`link` SEPARATOR ";;;") FROM `discord_blacklist_whitelistlink` WHERE `discord_blacklist_whitelistlink`.`guild_id` = `discord_setting`.`guild_id`)
				AS `blacklist_whitelistlinks`,
			(SELECT GROUP_CONCAT(`discord_blacklist_blacklistword`.`word` SEPARATOR ";;;") FROM `discord_blacklist_blacklistword` WHERE `discord_blacklist_blacklistword`.`guild_id` = `discord_setting`.`guild_id`)
				AS `blacklist_blacklistwords`
		FROM `discord_setting`
		WHERE `discord_setting`.`guild_id` = %s
		GROUP BY `discord_setting`.`guild_id`""",
		(guild_id,)
	)

	if res:
		return DiscordServerSettings(res.pop(0))

	else:
		if prevent_new:
			# return a empty 'dummy'
			return DiscordServerSettings({})
		else:
			return await makeDiscordSeverSettings(cls, guild_id)

async def makeDiscordSeverSettings(cls:"PhaazebotDiscord", guild_id:str) -> DiscordServerSettings:
	"""
	Makes a new entry in the PhaazeDB for a discord server/guild.
	Returns a DiscordServerSettings()
	"""

	try:
		cls.BASE.PhaazeDB.insertQuery(
			table="discord_setting",
			content=dict(guild_id=guild_id)
		)

		cls.BASE.Logger.info(f"(Discord) New server settings DB entry: {guild_id=}")
		return DiscordServerSettings({"guild_id":guild_id})
	except:
		cls.BASE.Logger.critical(f"(Discord) New server settings failed: {guild_id=}")
		raise RuntimeError("Creating new DB entry failed")

# discord_command
async def getDiscordServerCommands(cls:"PhaazebotDiscord", **search) -> Union[List[DiscordCommand], int]:
	"""
	Get server commands.
	Returns a list of DiscordCommand()

	Optional 'search' keywords:
	---------------------------
	* `command_id` - Union[int, str, None] : (Default: None) [sets LIMIT to 1]
	* `guild_id` - Optional[str] : (Default: None)
	* `trigger` - Optional[str] : (Default: None)
	* `active` - Optional[int] : (Default: 1) [0 = only inactive, 1 = only active]
	* `complex` - Optional[int] : (Default: None) [0 = only inactive, 1 = only active]
	* `function` - Optional[str] : (Default: None)
	* `hidden` - Optional[int] : (Default: 0) [0 = only visible, 1 = only hidden]
	* `require` - Optional[int] : (Default: None)

	Optional 'contains' keywords:
	-----------------------------
	* `content_contains` - Optional[str] : (Default: None) [DB uses LIKE on `content`]

	Optional 'between' keywords:
	----------------------------
	* `cooldown_between` - Tuple[from:int, to:int] : (Default: None) [DB uses >= and <=]
	* `required_currency_between` - Tuple[from:int, to:int] : (Default: None) [DB uses >= and <=]
	* `uses_between` - Tuple[from:int, to:int] : (Default: None) [DB uses >= and <=]

	Other:
	------
	* `order_str` - str : (Default: "ORDER BY discord_command.id ASC")
	* `limit` - Optional[int] : (Default: None)
	* `offset` - int : (Default: 0)

	Special:
	--------
	* `count_mode` - bool : (Default: False)
		* [returns COUNT(*) as int, disables: `limit`, `offset`]
	* `overwrite_where` - Optional[str] : (Default: None)
		* [Overwrites everything, appended after "1=1", so start with "AND field = %s"]
		* [Without `limit`, `offset`, `order` and `group by`]
	* `overwrite_where_values` - Union[tuple, dict, None] : (Default: ())
	"""
	# process
	ground_sql:str = """
		SELECT `discord_command`.*
		FROM `discord_command`
		WHERE 1 = 1"""

	sql:str = ""
	values:tuple = ()

	# Optional 'search' keywords
	command_id:Union[str, int, None] = search.get("command_id", None)
	if command_id is not None:
		sql += " AND `discord_command`.`id` = %s"
		values += (int(command_id),)
		search["limit"] = 1

	guild_id:Optional[str] = search.get("guild_id", None)
	if guild_id is not None:
		sql += " AND `discord_command`.`guild_id` = %s"
		values += (str(guild_id),)

	trigger:Optional[str] = search.get("trigger", None)
	if trigger is not None:
		sql += " AND `discord_command`.`trigger` = %s"
		values += (str(trigger),)

	active:Optional[int] = search.get("active", 1)
	if active is not None:
		sql += " AND `discord_command`.`active` = %s"
		values += (int(active),)

	complex_:Optional[int] = search.get("complex", None)
	if complex_ is not None:
		sql += " AND `discord_command`.`complex` = %s"
		values += (int(complex_),)

	function:Optional[str] = search.get("function", None)
	if function is not None:
		sql += " AND `discord_command`.`function` = %s"
		values += (str(function),)

	hidden:Optional[int] = search.get("hidden", None)
	if hidden is not None:
		sql += " AND `discord_command`.`hidden` = %s"
		values += (int(hidden),)

	require:Optional[int] = search.get("require", None)
	if require is not None:
		sql += " AND `discord_command`.`require` = %s"
		values += (int(require),)

	# Optional 'contains' keywords
	content_contains:Optional[str] = search.get("content_contains", None)
	if content_contains is not None:
		content_contains = f"%{content_contains}%"
		sql += " AND `discord_command`.`content` LIKE %s"
		values += (str(content_contains),)

	# Optional 'between' keywords
	cooldown_between:Optional[tuple] = search.get("cooldown_between", None)
	if cooldown_between is not None:
		from_:Optional[int] = cooldown_between[0]
		to_:Optional[int] = cooldown_between[1]

		if (from_ is not None) and (to_ is not None):
			sql += " AND `discord_command`.`cooldown` BETWEEN %s AND %s"
			values += (int(from_), int(to_))

		if (from_ is not None) and (to_ is None):
			sql += " AND `discord_command`.`cooldown` >= %s"
			values += (int(from_),)

		if (from_ is None) and (to_ is not None):
			sql += " AND `discord_command`.`cooldown` <= %s"
			values += (int(to_),)

	required_currency_between:Optional[tuple] = search.get("required_currency_between", None)
	if required_currency_between is not None:
		from_:Optional[int] = required_currency_between[0]
		to_:Optional[int] = required_currency_between[1]

		if (from_ is not None) and (to_ is not None):
			sql += " AND `discord_command`.`required_currency` BETWEEN %s AND %s"
			values += (int(from_), int(to_))

		if (from_ is not None) and (to_ is None):
			sql += " AND `discord_command`.`required_currency` >= %s"
			values += (int(from_),)

		if (from_ is None) and (to_ is not None):
			sql += " AND `discord_command`.`required_currency` <= %s"
			values += (int(to_),)

	uses_between:Optional[tuple] = search.get("uses_between", None)
	if uses_between is not None:
		from_:Optional[int] = uses_between[0]
		to_:Optional[int] = uses_between[1]

		if (from_ is not None) and (to_ is not None):
			sql += " AND `discord_command`.`uses` BETWEEN %s AND %s"
			values += (int(from_), int(to_))

		if (from_ is not None) and (to_ is None):
			sql += " AND `discord_command`.`uses` >= %s"
			values += (int(from_),)

		if (from_ is None) and (to_ is not None):
			sql += " AND `discord_command`.`uses` <= %s"
			values += (int(to_),)

	# Special
	count_mode:bool = search.get("count_mode", False)
	if count_mode:
		search["limit"] = None
		search["offset"] = None
		ground_sql: str = """
			SELECT COUNT(*) AS `I`
			FROM `discord_command`
			WHERE 1 = 1"""

	overwrite_where:Optional[str] = search.get("overwrite_where", None)
	overwrite_where_values: Union[tuple, dict, None] = search.get("overwrite_where_values", ())
	if overwrite_where:
		sql = overwrite_where
		values = overwrite_where_values

	# Other
	order_str:str = search.get("order_str", "ORDER BY `discord_command`.`id` ASC")
	sql += f" {order_str}"

	limit:Optional[int] = search.get("limit", None)
	offset:int = search.get("offset", 0)
	if limit:
		sql += f" LIMIT {limit}"
		if offset:
			sql += f" OFFSET {offset}"

	res:List[dict] = cls.BASE.PhaazeDB.selectQuery(ground_sql+sql, values)

	if count_mode:
		return res[0]['I']
	else:
		return [DiscordCommand(x) for x in res]

# discord_user
async def getDiscordServerUsers(cls:"PhaazebotDiscord", **search) -> Union[List[DiscordUserStats], int]:
	"""
	Get server levels.
	Returns a list of DiscordUserStats().

	Optional 'search' keywords:
	---------------------------
	* `member_id` - Optional[str] : (Default: None)
	* `guild_id` - Optional[str] : (Default: None)
	* `edited` - Optional[int] : (Default: None) [0 = not edited, 1 = only edited]
	* `on_server` - Optional[int] : (Default: None) [0 = only not on_server, 1 = only on_server]
	* `regular` - Optional[int] : (Default: None) [0 = only non regular, 1 = only regular]
	* `username` - Optional[str] : (Default: None)
	* `nickname` - Optional[str] : (Default: None)

	Optional 'contains' keywords:
	-----------------------------
	* `name_contains` Optional[str]: (Default: None) [DB uses LIKE on `nickname`, `username`]

	Optional 'between' keywords:
	----------------------------
	* `rank_between` - Tuple[from:int, to:int] : (Default: None) [DB uses >= and <=]
	* `exp_between` - Tuple[from:int, to:int] : (Default: None) [DB uses >= and <=]
	* `currency_between` - Tuple[from:int, to:int] : (Default: None) [DB uses >= and <=]

	Other:
	------
	* `order_str` - str : (Default: "ORDER BY discord_user.id ASC")
	* `limit` - Optional[int] : (Default: None)
	* `offset` - int : (Default: 0)

	Special:
	--------
	* `count_mode` - bool : (Default: False)
		* [returns COUNT(*) as int, disables: `limit`, `offset`]
	* `overwrite_where` - Optional[str] : (Default: None)
		* [Overwrites everything, appended after "1=1", so start with "AND field = %s"]
		* [Without `limit`, `offset`, `order` and `group by`]
	* `overwrite_where_values` - Union[tuple, dict, None] : (Default: ())
	"""
	# process
	ground_sql:str = """
		WITH `discord_user` AS (
			SELECT
				`discord_user`.*,
				GROUP_CONCAT(`discord_user_medal`.`name` SEPARATOR ';;;') AS `medals`,
				RANK() OVER (PARTITION BY `discord_user`.`guild_id` ORDER BY `discord_user`.`exp` DESC) AS `rank`,
				(`discord_regular`.`id` IS NOT NULL) AS `regular`
			FROM `discord_user`
			LEFT JOIN `discord_user_medal`
				ON `discord_user_medal`.`guild_id` = `discord_user`.`guild_id`
					AND `discord_user_medal`.`member_id` = `discord_user`.`member_id`
			LEFT JOIN `discord_regular`
				ON `discord_regular`.`guild_id` = `discord_user`.`guild_id`
					AND `discord_regular`.`member_id` = `discord_user`.`member_id`
			{{on_server}}
			GROUP BY `discord_user`.`guild_id`, `discord_user`.`member_id`
		)
		SELECT `discord_user`.* FROM `discord_user` WHERE 1 = 1"""
	sql:str = ""
	values:dict = {}

	# Optional 'search' keywords
	member_id:Optional[str] = search.get("member_id", None)
	if member_id is not None:
		sql += " AND `discord_user`.`member_id` = %(member_id)s"
		values["member_id"] = str(member_id)

	guild_id:Optional[str] = search.get("guild_id", None)
	if guild_id is not None:
		sql += " AND `discord_user`.`guild_id` = %(guild_id)s"
		values["guild_id"] = str(guild_id)

	edited:Optional[int] = search.get("edited", None)
	if edited is not None:
		sql += " AND `discord_user`.`edited` = %(edited)s"
		values["edited"] = int(edited)

	regular:int = search.get("regular", None)
	if regular is not None:
		sql += " AND `discord_user`.`regular` = %(regular)s"
		values["regular"] = int(regular)

	username:Optional[str] = search.get("username", None)
	if username is not None:
		sql += " AND `discord_user`.`username` = %(username)s"
		values["username"] = str(username)

	nickname:Optional[str] = search.get("nickname", None)
	if nickname is not None:
		sql += " AND `discord_user`.`nickname` = %(nickname)s"
		values["nickname"] = str(nickname)

	# Optional 'contains' keywords
	name_contains:Optional[str] = search.get("name_contains", None)
	if name_contains:
		sql += " AND ( 1 = 2"
		sql += " OR `discord_user`.`username` LIKE %(name_contains)s"
		sql += " OR `discord_user`.`nickname` LIKE %(name_contains)s"
		sql += " )"
		values["name_contains"] = str(f"%{name_contains}%")

	# Optional 'between' keywords
	rank_between:Optional[tuple] = search.get("rank_between", None)
	if rank_between is not None:
		from_:Optional[int] = rank_between[0]
		to_:Optional[int] = rank_between[1]

		if (from_ is not None) and (to_ is not None):
			sql += " AND `discord_user`.`rank` BETWEEN %(rank_between_from)s AND %(rank_between_to)s"
			values["rank_between_from"] = int(from_)
			values["rank_between_to"] = int(to_)

		if (from_ is not None) and (to_ is None):
			sql += " AND `discord_user`.`rank` >= %(rank_between_from)s"
			values["rank_between_from"] = int(from_)

		if (from_ is None) and (to_ is not None):
			sql += " AND `discord_user`.`rank` <= %(rank_between_to)s"
			values["rank_between_to"] = int(to_)

	exp_between:Optional[tuple] = search.get("exp_between", None)
	if exp_between is not None:
		from_:Optional[int] = exp_between[0]
		to_:Optional[int] = exp_between[1]

		if (from_ is not None) and (to_ is not None):
			sql += " AND `discord_user`.`exp` BETWEEN %(exp_between_from)s AND %(exp_between_to)s"
			values["exp_between_from"] = int(from_)
			values["exp_between_to"] = int(to_)

		if (from_ is not None) and (to_ is None):
			sql += " AND `discord_user`.`exp` >= %(exp_between_from)s"
			values["exp_between_from"] = int(from_)

		if (from_ is None) and (to_ is not None):
			sql += " AND `discord_user`.`exp` <= %(exp_between_to)s"
			values["exp_between_to"] = int(to_)

	currency_between:Optional[tuple] = search.get("currency_between", None)
	if currency_between is not None:
		from_:Optional[int] = currency_between[0]
		to_:Optional[int] = currency_between[1]

		if (from_ is not None) and (to_ is not None):
			sql += " AND `discord_user`.`currency` BETWEEN %(currency_between_from)s AND %(currency_between_to)s"
			values["currency_between_from"] = int(from_)
			values["currency_between_to"] = int(to_)

		if (from_ is not None) and (to_ is None):
			sql += " AND `discord_user`.`currency` >= %(currency_between_from)s"
			values["currency_between_from"] = int(from_)

		if (from_ is None) and (to_ is not None):
			sql += " AND `discord_user`.`currency` <= %(currency_between_to)s"
			values["currency_between_to"] = int(to_)

	# Special
	count_mode:bool = search.get("count_mode", False)
	if count_mode:
		search["limit"] = None
		search["offset"] = None
		ground_sql: str = """
		WITH `discord_user` AS (
			SELECT
				`discord_user`.*,
				GROUP_CONCAT(`discord_user_medal`.`name` SEPARATOR ';;;') AS `medals`,
				RANK() OVER (PARTITION BY `discord_user`.`guild_id` ORDER BY `discord_user`.`exp` DESC) AS `rank`,
				(`discord_regular`.`id` IS NOT NULL) AS `regular`
			FROM `discord_user`
			LEFT JOIN `discord_user_medal`
				ON `discord_user_medal`.`guild_id` = `discord_user`.`guild_id`
					AND `discord_user_medal`.`member_id` = `discord_user`.`member_id`
			LEFT JOIN `discord_regular`
				ON `discord_regular`.`guild_id` = `discord_user`.`guild_id`
					AND `discord_regular`.`member_id` = `discord_user`.`member_id`
			{{on_server}}
			GROUP BY `discord_user`.`guild_id`, `discord_user`.`member_id`
		)
		SELECT COUNT(*) AS `I` FROM `discord_user` WHERE 1 = 1"""

	overwrite_where:Optional[str] = search.get("overwrite_where", None)
	overwrite_where_values: Union[tuple, dict, None] = search.get("overwrite_where_values", ())
	if overwrite_where:
		sql = overwrite_where
		values = overwrite_where_values

	# Other
	order_str:str = search.get("order_str", "ORDER BY `discord_user`.`id` ASC")
	sql += f" {order_str}"

	limit:Optional[int] = search.get("limit", None)
	offset:int = search.get("offset", 0)
	if limit:
		sql += f" LIMIT {limit}"
		if offset:
			sql += f" OFFSET {offset}"

	# on_server must be inserted in the WITH clause before standard sql
	on_server:int = search.get("on_server", 1)
	if on_server is None:
		ground_sql = ground_sql.replace("{{on_server}}", '')
	else:
		ground_sql = ground_sql.replace("{{on_server}}", "WHERE `discord_user`.`on_server` = %(on_server)s")
		values["on_server"] = int(on_server)

	res:List[dict] = cls.BASE.PhaazeDB.selectQuery(ground_sql+sql, values)

	if count_mode:
		return res[0]['I']
	else:
		return [DiscordUserStats(x) for x in res]

# discord_user_medal
async def getDiscordUsersMedals(cls:"PhaazebotDiscord", **search) -> Union[List[DiscordUserMedal], int]:
	"""
	Get server levels.
	Returns a list of DiscordUserMedal().

	Optional 'search' keywords:
	---------------------------
	* `medal_id` - Union[int, str, None] : (Default: None)
	* `member_id` - Optional[str] : (Default: None)
	* `guild_id` - Optional[str] : (Default: None)
	* `name` - Optional[str] : (Default: None)

	Optional 'contains' keywords:
	-----------------------------
	* `name_contains` Optional[str]: (Default: None) [DB uses LIKE on `name`]

	Other:
	------
	* `order_str` - str : (Default: "ORDER BY discord_user_medal.id ASC")
	* `limit` - Optional[int] : (Default: None)
	* `offset` - int : (Default: 0)

	Special:
	--------
	* `count_mode` - bool : (Default: False)
		* [returns COUNT(*) as int, disables: `limit`, `offset`]
	* `overwrite_where` - Optional[str] : (Default: None)
		* [Overwrites everything, appended after "1=1", so start with "AND field = %s"]
		* [Without `limit`, `offset`, `order` and `group by`]
	* `overwrite_where_values` - Union[tuple, dict, None] : (Default: ())
	"""
	# process
	ground_sql:str = """
		SELECT `discord_user_medal`.* 
		FROM `discord_user_medal`
		WHERE 1 = 1"""

	sql:str = ""
	values:tuple = ()

	# Optional search keywords
	medal_id:Union[int, str, None] = search.get("medal_id", None)
	if medal_id is not None:
		sql += " AND `discord_user_medal`.`id` = %s"
		values += (int(medal_id),)

	member_id:Optional[str] = search.get("member_id", None)
	if member_id is not None:
		sql += " AND `discord_user_medal`.`member_id` = %s"
		values += (str(member_id),)

	guild_id:Optional[str] = search.get("guild_id", None)
	if guild_id is not None:
		sql += " AND `discord_user_medal`.`guild_id` = %s"
		values += (str(guild_id),)

	name:Optional[str] = search.get("name", None)
	if name is not None:
		sql += " AND `discord_user_medal`.`name` = %s"
		values += (str(name),)

	# Optional 'contains' keywords
	name_contains:Optional[str] = search.get("name_contains", None)
	if name_contains is not None:
		name_contains = f"%{name_contains}%"
		sql += " AND `discord_user_medal`.`name` LIKE %s"
		values += (str(name_contains),)

	# Special
	count_mode:bool = search.get("count_mode", False)
	if count_mode:
		search["limit"] = None
		search["offset"] = None
		ground_sql: str = """
			SELECT COUNT(*) AS `I` 
			FROM `discord_user_medal`
			WHERE 1 = 1"""

	overwrite_where:Optional[str] = search.get("overwrite_where", None)
	overwrite_where_values: Union[tuple, dict, None] = search.get("overwrite_where_values", ())
	if overwrite_where:
		sql = overwrite_where
		values = overwrite_where_values

	# Other
	order_str:str = search.get("order_str", "ORDER BY `discord_user_medal`.`id` ASC")
	sql += f" {order_str}"

	limit:Optional[int] = search.get("limit", None)
	offset:int = search.get("offset", 0)
	if limit:
		sql += f" LIMIT {limit}"
		if offset:
			sql += f" OFFSET {offset}"

	res:List[dict] = cls.BASE.PhaazeDB.selectQuery(ground_sql+sql, values)

	if count_mode:
		return res[0]['I']
	else:
		return [DiscordUserMedal(x) for x in res]

# discord_regular
async def getDiscordServerRegulars(cls:"PhaazebotDiscord", **search) -> Union[List[DiscordRegular], int]:
	"""
	Get server regulars.
	Returns a list of DiscordRegular().

	Optional 'search' keywords:
	---------------------------
	* `regular_id` - Union[int, str, None] : (Default: None)
	* `member_id` - Optional[str] : (Default: None)
	* `guild_id` - Optional[str] : (Default: None)
	* `name` - Optional[str] : (Default: None)

	Other:
	------
	* `order_str` - str : (Default: "ORDER BY discord_regular.id ASC")
	* `limit` - Optional[int] : (Default: None)
	* `offset` - int : (Default: 0)

	Special:
	--------
	* `count_mode` - bool : (Default: False)
		* [returns COUNT(*) as int, disables: `limit`, `offset`]
	* `overwrite_where` - Optional[str] : (Default: None)
		* [Overwrites everything, appended after "1=1", so start with "AND field = %s"]
		* [Without `limit`, `offset`, `order` and `group by`]
	* `overwrite_where_values` - Union[tuple, dict, None] : (Default: ())
	"""
	# process
	ground_sql:str = """
		SELECT `discord_regular`.* 
		FROM `discord_regular`
		WHERE 1 = 1"""

	sql:str = ""
	values:tuple = ()

	regular_id:Union[int, str, None] = search.get("regular_id", None)
	if regular_id is not None:
		sql += " AND `discord_regular`.`id` = %s"
		values += (int(regular_id),)

	member_id:Optional[str] = search.get("member_id", None)
	if member_id is not None:
		sql += " AND `discord_regular`.`member_id` = %s"
		values += (str(member_id),)

	guild_id:Optional[str] = search.get("guild_id", None)
	if guild_id is not None:
		sql += " AND `discord_regular`.`guild_id` = %s"
		values += (str(guild_id),)

	# Special
	count_mode:bool = search.get("count_mode", False)
	if count_mode:
		search["limit"] = None
		search["offset"] = None
		ground_sql: str = """
			SELECT COUNT(*) AS `I` 
			FROM `discord_regular`
			WHERE 1 = 1"""

	overwrite_where:Optional[str] = search.get("overwrite_where", None)
	overwrite_where_values: Union[tuple, dict, None] = search.get("overwrite_where_values", ())
	if overwrite_where:
		sql = overwrite_where
		values = overwrite_where_values

	# Other
	order_str:str = search.get("order_str", "ORDER BY `discord_regular`.`id` ASC")
	sql += f" {order_str}"

	limit:Optional[int] = search.get("limit", None)
	offset:int = search.get("offset", 0)
	if limit:
		sql += f" LIMIT {limit}"
		if offset:
			sql += f" OFFSET {offset}"

	res:List[dict] = cls.BASE.PhaazeDB.selectQuery(ground_sql+sql, values)

	if count_mode:
		return res[0]['I']
	else:
		return [DiscordRegular(x) for x in res]

# discord_quote
async def getDiscordServerQuotes(cls:"PhaazebotDiscord",**search) -> Union[List[DiscordQuote], int]:
	"""
	Get server quotes.
	Returns a list of DiscordQuote().

	Optional 'search' keywords:
	---------------------------
	* `quote_id` - Union[int, str, None] : (Default: None)
	* `guild_id` - Optional[str] : (Default: None)

	Optional 'contains' keywords:
	-----------------------------
	* `content_contains` Optional[str]: (Default: None) [DB uses LIKE on `content`]

	Other:
	------
	* `order_str` - str : (Default: "ORDER BY discord_quote.id ASC")
	* `limit` - Optional[int] : (Default: None)
	* `offset` - int : (Default: 0)

	Special:
	--------
	* `count_mode` - bool : (Default: False)
		* [returns COUNT(*) as int, disables: `limit`, `offset`]
	* `overwrite_where` - Optional[str] : (Default: None)
		* [Overwrites everything, appended after "1=1", so start with "AND field = %s"]
		* [Without `limit`, `offset`, `order` and `group by`]
	* `overwrite_where_values` - Union[tuple, dict, None] : (Default: ())
	"""
	# process
	ground_sql:str = """
		SELECT `discord_quote`.* FROM `discord_quote`
		WHERE 1 = 1"""

	sql:str = ""
	values:tuple = ()

	# Optional 'search' keywords
	quote_id:Union[int, str, None] = search.get("quote_id", None)
	if quote_id is not None:
		sql += " AND `discord_quote`.`id` = %s"
		values += (int(quote_id),)
		search["limit"] = 1

	guild_id:Optional[str] = search.get("guild_id", None)
	if guild_id is not None:
		sql += " AND `discord_quote`.`guild_id` = %s"
		values += (str(guild_id),)

	# Optional 'contains' keywords
	content_contains:Optional[str] = search.get("content_contains", None)
	if content_contains is not None:
		content_contains = f"%{content_contains}%"
		sql += " AND `discord_quote`.`content` LIKE %s"
		values += (str(content_contains),)

	# Special
	count_mode:bool = search.get("count_mode", False)
	if count_mode:
		search["limit"] = None
		search["offset"] = None
		ground_sql: str = """
			SELECT COUNT(*) AS `I` 
			FROM `discord_quote`
			WHERE 1 = 1"""

	overwrite_where:Optional[str] = search.get("overwrite_where", None)
	overwrite_where_values: Union[tuple, dict, None] = search.get("overwrite_where_values", ())
	if overwrite_where:
		sql = overwrite_where
		values = overwrite_where_values

	# Other
	order_str:str = search.get("order_str", "ORDER BY `discord_quote`.`id` ASC")
	sql += f" {order_str}"

	limit:Optional[int] = search.get("limit", None)
	offset:int = search.get("offset", 0)
	if limit:
		sql += f" LIMIT {limit}"
		if offset:
			sql += f" OFFSET {offset}"

	res:List[dict] = cls.BASE.PhaazeDB.selectQuery(ground_sql+sql, values)

	if count_mode:
		return res[0]['I']
	else:
		return [DiscordQuote(x) for x in res]

# discord_assignrole
async def getDiscordServerAssignRoles(cls:"PhaazebotDiscord", **search) -> Union[List[DiscordAssignRole], int]:
	"""
	Get server assign roles.
	Returns a list of DiscordAssignRole().

	Optional 'search' keywords:
	---------------------------
	* `assignrole_id` - Union[int, str, None] : (Default: None)
	* `role_id` - Optional[str] : (Default: None)
	* `guild_id` - Optional[str] : (Default: None)
	* `trigger` - Optional[str] : (Default: None)

	Other:
	------
	* `order_str` - str : (Default: "ORDER BY discord_assignrole.id ASC")
	* `limit` - Optional[int] : (Default: None)
	* `offset` - int : (Default: 0)

	Special:
	--------
	* `count_mode` - bool : (Default: False)
		* [returns COUNT(*) as int, disables: `limit`, `offset`]
	* `overwrite_where` - Optional[str] : (Default: None)
		* [Overwrites everything, appended after "1=1", so start with "AND field = %s"]
		* [Without `limit`, `offset`, `order` and `group by`]
	* `overwrite_where_values` - Union[tuple, dict, None] : (Default: ())
	"""
	# process
	ground_sql:str = """
		SELECT `discord_assignrole`.* 
		FROM `discord_assignrole`
		WHERE 1 = 1"""

	sql:str = ""
	values:tuple = ()

	assignrole_id:Union[int, str, None] = search.get("assignrole_id", None)
	if assignrole_id:
		sql += " AND `discord_assignrole`.`id` = %s"
		values += (int(assignrole_id),)

	role_id:Optional[str] = search.get("role_id", None)
	if role_id is not None:
		sql += " AND `discord_assignrole`.`role_id` = %s"
		values += (str(role_id),)

	guild_id:Optional[str] = search.get("guild_id", None)
	if guild_id is not None:
		sql += " AND `discord_assignrole`.`guild_id` = %s"
		values += (str(guild_id),)

	trigger:Optional[str] = search.get("trigger", None)
	if trigger is not None:
		sql += " AND `discord_assignrole`.`trigger` = %s"
		values += (str(trigger),)

	# Special
	count_mode:bool = search.get("count_mode", False)
	if count_mode:
		search["limit"] = None
		search["offset"] = None
		ground_sql: str = """
			SELECT COUNT(*) AS `I` 
			FROM `discord_assignrole`
			WHERE 1 = 1"""

	overwrite_where:Optional[str] = search.get("overwrite_where", None)
	overwrite_where_values: Union[tuple, dict, None] = search.get("overwrite_where_values", ())
	if overwrite_where:
		sql = overwrite_where
		values = overwrite_where_values

	# Other
	order_str:str = search.get("order_str", "ORDER BY `discord_assignrole`.`id` ASC")
	sql += f" {order_str}"

	limit:Optional[int] = search.get("limit", None)
	offset:int = search.get("offset", 0)
	if limit:
		sql += f" LIMIT {limit}"
		if offset:
			sql += f" OFFSET {offset}"

	res:List[dict] = cls.BASE.PhaazeDB.selectQuery(ground_sql+sql, values)

	if count_mode:
		return res[0]['I']
	else:
		return [DiscordAssignRole(x) for x in res]

# discord_twitch_alert
async def getDiscordServerTwitchAlerts(cls:"PhaazebotDiscord", **search) -> Union[List[DiscordTwitchAlert], int]:
	"""
	Get server twitch alerts.
	Returns a list of DiscordTwitchAlert().

	Optional 'search' keywords:
	---------------------------
	* `alert_id` - Union[int, str, None] : (Default: None)
	* `discord_guild_id` - Optional[str] : (Default: None)
	* `discord_channel_id` - Optional[str] : (Default: None)
	* `twitch_channel_id` - Optional[str] : (Default: None)
	* `twitch_channel_name` - Optional[str] : (Default: None)
	* `suppress_gamechange` - Optional[int] : (Default: None) [0 = with gamechange, 1 = without gamechange]

	Optional 'contains' keywords:
	-----------------------------
	* `custom_msg_contains` Optional[str]: (Default: None) [DB uses LIKE on `custom_msg`]
	* `twitch_channel_name_contains` Optional[str]: (Default: None) [DB uses LIKE on `twitch_channel_name`]

	Other:
	------
	* `order_str` - str : (Default: "ORDER BY discord_twitch_alert.id ASC")
	* `limit` - Optional[int] : (Default: None)
	* `offset` - int : (Default: 0)

	Special:
	--------
	* `count_mode` - bool : (Default: False)
		* [returns COUNT(*) as int, disables: `limit`, `offset`]
	* `overwrite_where` - Optional[str] : (Default: None)
		* [Overwrites everything, appended after "1=1", so start with "AND field = %s"]
		* [Without `limit`, `offset`, `order` and `group by`]
	* `overwrite_where_values` - Union[tuple, dict, None] : (Default: ())
	"""
	# process
	ground_sql:str = """
		SELECT
			`discord_twitch_alert`.*,
			`twitch_user_name`.`user_name` AS `twitch_channel_name`
		FROM `discord_twitch_alert`
		LEFT JOIN `twitch_user_name`
			ON `discord_twitch_alert`.`twitch_channel_id` = `twitch_user_name`.`user_id`
		WHERE 1 = 1"""

	sql:str = ""
	values:tuple = ()

	# Optional 'search' keywords
	alert_id:Union[int, str, None] = search.get("alert_id", None)
	if alert_id is not None:
		sql += " AND `discord_twitch_alert`.`id` = %s"
		values += (int(alert_id),)

	discord_guild_id:Optional[str] = search.get("discord_guild_id", None)
	if discord_guild_id is not None:
		sql += " AND `discord_twitch_alert`.`discord_guild_id` = %s"
		values += (str(discord_guild_id),)

	discord_channel_id:Optional[str] = search.get("discord_channel_id", None)
	if discord_channel_id is not None:
		sql += " AND `discord_twitch_alert`.`discord_channel_id` = %s"
		values += (str(discord_channel_id),)

	twitch_channel_id:Optional[str] = search.get("twitch_channel_id", None)
	if twitch_channel_id is not None:
		sql += " AND `discord_twitch_alert`.`twitch_channel_id` = %s"
		values += (str(twitch_channel_id),)

	suppress_gamechange:Optional[int] = search.get("suppress_gamechange", None)
	if suppress_gamechange is not None:
		sql += " AND `discord_twitch_alert`.`suppress_gamechange` = %s"
		values += (int(suppress_gamechange),)

	twitch_channel_name:Optional[str] = search.get("twitch_channel_name", None)
	if twitch_channel_name is not None:
		sql += " AND `twitch_user_name`.`twitch_channel_name` = %s"
		values += (str(twitch_channel_name),)

	# Optional 'contains' keywords
	custom_msg_contains:Optional[str] = search.get("custom_msg_contains", None)
	if custom_msg_contains is not None:
		custom_msg_contains = f"%{custom_msg_contains}%"
		sql += " AND `discord_twitch_alert`.`custom_msg` LIKE %s"
		values += (str(custom_msg_contains),)

	twitch_channel_name_contains:Optional[str] = search.get("twitch_channel_name_contains", None)
	if twitch_channel_name_contains is not None:
		twitch_channel_name_contains = f"%{twitch_channel_name_contains}%"
		sql += " AND `twitch_user_name`.`user_name` LIKE %s"
		values += (str(twitch_channel_name_contains),)

	# Special
	count_mode:bool = search.get("count_mode", False)
	if count_mode:
		search["limit"] = None
		search["offset"] = None
		ground_sql: str = """
			SELECT COUNT(*) AS `I` 
			FROM `discord_twitch_alert`
			LEFT JOIN `twitch_user_name`
				ON `discord_twitch_alert`.`twitch_channel_id` = `twitch_user_name`.`user_id`
			WHERE 1 = 1"""

	overwrite_where:Optional[str] = search.get("overwrite_where", None)
	overwrite_where_values: Union[tuple, dict, None] = search.get("overwrite_where_values", ())
	if overwrite_where:
		sql = overwrite_where
		values = overwrite_where_values

	# Other
	order_str:str = search.get("order_str", "ORDER BY `discord_twitch_alert`.`id` ASC")
	sql += f" {order_str}"

	limit:Optional[int] = search.get("limit", None)
	offset:int = search.get("offset", 0)
	if limit:
		sql += f" LIMIT {limit}"
		if offset:
			sql += f" OFFSET {offset}"

	res:List[dict] = cls.BASE.PhaazeDB.selectQuery(ground_sql+sql, values)

	if count_mode:
		return res[0]['I']
	else:
		return [DiscordTwitchAlert(x) for x in res]

# discord_blacklist_blacklistword
async def getDiscordServerBlacklistedWords(cls:"PhaazebotDiscord", **search) -> Union[List[DiscordBlacklistedWord], int]:
	"""
	Get all words that are blacklisted on the guild.
	Returns a list of DiscordBlacklistedWord().

	Optional 'search' keywords:
	---------------------------
	* `word_id` - Union[int, str, None] : (Default: None)
	* `guild_id` - Optional[str] : (Default: None)
	* `word` - Optional[str] : (Default: None)

	Optional 'contains' keywords:
	-----------------------------
	* `word_contains` Optional[str]: (Default: None) [DB uses LIKE on `word`]

	Other:
	------
	* `order_str` - str : (Default: "ORDER BY discord_blacklist_blacklistword.id ASC")
	* `limit` - Optional[int] : (Default: None)
	* `offset` - int : (Default: 0)

	Special:
	--------
	* `count_mode` - bool : (Default: False)
		* [returns COUNT(*) as int, disables: `limit`, `offset`]
	* `overwrite_where` - Optional[str] : (Default: None)
		* [Overwrites everything, appended after "1=1", so start with "AND field = %s"]
		* [Without `limit`, `offset`, `order` and `group by`]
	* `overwrite_where_values` - Union[tuple, dict, None] : (Default: ())
	"""
	# process
	ground_sql:str = """
		SELECT `discord_blacklist_blacklistword`.* 
		FROM `discord_blacklist_blacklistword`
		WHERE 1 = 1"""

	sql:str = ""
	values:tuple = ()

	# Optional 'search' keywords
	word_id:Union[int, str, None] = search.get("word_id", None)
	if word_id is not None:
		sql += " AND `discord_blacklist_blacklistword`.`id` = %s"
		values += (int(word_id),)

	guild_id:Optional[str] = search.get("guild_id", None)
	if guild_id is not None:
		sql += " AND `discord_blacklist_blacklistword`.`guild_id` = %s"
		values += (str(guild_id),)

	word:Optional[str] = search.get("word", None)
	if word is not None:
		sql += " AND `discord_blacklist_blacklistword`.`word` = %s"
		values += (str(word),)

	# Optional 'contains' keywords
	word_contains:Optional[str] = search.get("word_contains", None)
	if word_contains is not None:
		word_contains = f"%{word_contains}%"
		sql += " AND `discord_blacklist_blacklistword`.`word` LIKE %s"
		values += (str(word_contains),)

	# Special
	count_mode:bool = search.get("count_mode", False)
	if count_mode:
		search["limit"] = None
		search["offset"] = None
		ground_sql: str = """
			SELECT COUNT(*) AS `I` 
			FROM `discord_blacklist_blacklistword`
			WHERE 1 = 1"""

	overwrite_where:Optional[str] = search.get("overwrite_where", None)
	overwrite_where_values: Union[tuple, dict, None] = search.get("overwrite_where_values", ())
	if overwrite_where:
		sql = overwrite_where
		values = overwrite_where_values

	# Other
	order_str:str = search.get("order_str", "ORDER BY `discord_blacklist_blacklistword`.`id` ASC")
	sql += f" {order_str}"

	limit:Optional[int] = search.get("limit", None)
	offset:int = search.get("offset", 0)
	if limit:
		sql += f" LIMIT {limit}"
		if offset:
			sql += f" OFFSET {offset}"

	res:List[dict] = cls.BASE.PhaazeDB.selectQuery(ground_sql+sql, values)

	if count_mode:
		return res[0]['I']
	else:
		return [DiscordBlacklistedWord(x) for x in res]

# discord_blacklist_whitelistrole
async def getDiscordServerExceptionRoles(cls:"PhaazebotDiscord", **search) -> Union[List[DiscordWhitelistedRole], int]:
	"""
	Get exceptionroles for a guild.
	Returns a list of DiscordWhitelistedRole().

	Optional 'search' keywords:
	---------------------------
	* `exceptionrole_id` - Union[int, str, None] : (Default: None)
	* `guild_id` - Optional[str] : (Default: None)
	* `role_id` - Optional[str] : (Default: None)

	Other:
	------
	* `order_str` - str : (Default: "ORDER BY discord_blacklist_whitelistrole.id ASC")
	* `limit` - Optional[int] : (Default: None)
	* `offset` - int : (Default: 0)

	Special:
	--------
	* `count_mode` - bool : (Default: False)
		* [returns COUNT(*) as int, disables: `limit`, `offset`]
	* `overwrite_where` - Optional[str] : (Default: None)
		* [Overwrites everything, appended after "1=1", so start with "AND field = %s"]
		* [Without `limit`, `offset`, `order` and `group by`]
	* `overwrite_where_values` - Union[tuple, dict, None] : (Default: ())
	"""
	# process
	ground_sql:str = """
		SELECT `discord_blacklist_whitelistrole`.* 
		FROM `discord_blacklist_whitelistrole`
		WHERE 1 = 1"""

	sql:str = ""
	values:tuple = ()

	# Optional 'search' keywords
	exceptionrole_id:Union[int, str, None] = search.get("exceptionrole_id", None)
	if exceptionrole_id is not None:
		sql += " AND `discord_blacklist_whitelistrole`.`id` = %s"
		values += (int(exceptionrole_id),)

	guild_id:Optional[str] = search.get("guild_id", None)
	if guild_id is not None:
		sql += " AND `discord_blacklist_whitelistrole`.`guild_id` = %s"
		values += (str(guild_id),)

	role_id:Optional[str] = search.get("role_id", None)
	if role_id is not None:
		sql += " AND `discord_blacklist_whitelistrole`.`role_id` = %s"
		values += (str(role_id),)

	# Special
	count_mode:bool = search.get("count_mode", False)
	if count_mode:
		search["limit"] = None
		search["offset"] = None
		ground_sql: str = """
			SELECT COUNT(*) AS `I`
			FROM `discord_blacklist_whitelistrole`
			WHERE 1 = 1"""

	overwrite_where:Optional[str] = search.get("overwrite_where", None)
	overwrite_where_values:Union[tuple, dict, None] = search.get("overwrite_where_values", ())
	if overwrite_where:
		sql = overwrite_where
		values = overwrite_where_values

	# Other
	order_str:str = search.get("order_str", "ORDER BY `discord_blacklist_whitelistrole`.`id` ASC")
	sql += f" {order_str}"

	limit:Optional[int] = search.get("limit", None)
	offset:int = search.get("offset", 0)
	if limit:
		sql += f" LIMIT {limit}"
		if offset:
			sql += f" OFFSET {offset}"

	res:List[dict] = cls.BASE.PhaazeDB.selectQuery(ground_sql+sql, values)

	if count_mode:
		return res[0]['I']
	else:
		return [DiscordWhitelistedRole(x) for x in res]

# discord_blacklist_whitelistlink
async def getDiscordServerWhitelistedLinks(cls:"PhaazebotDiscord", **search) -> Union[List[DiscordWhitelistedLink], int]:
	"""
	Get whitelisted links for a guild.
	Returns a list of DiscordWhitelistedLink().

	Optional 'search' keywords:
	---------------------------
	* `link_id` - Union[int, str, None] : (Default: None)
	* `guild_id` - Optional[str] : (Default: None)
	* `link` - Optional[str] : (Default: None)

	Optional 'contains' keywords:
	-----------------------------
	* `link_contains` Optional[str]: (Default: None) [DB uses LIKE on `link`]

	Other:
	------
	* `order_str` - str : (Default: "ORDER BY discord_blacklist_whitelistlink.id ASC")
	* `limit` - Optional[int] : (Default: None)
	* `offset` - int : (Default: 0)

	Special:
	--------
	* `count_mode` - bool : (Default: False)
		* [returns COUNT(*) as int, disables: `limit`, `offset`]
	* `overwrite_where` - Optional[str] : (Default: None)
		* [Overwrites everything, appended after "1=1", so start with "AND field = %s"]
		* [Without `limit`, `offset`, `order` and `group by`]
	* `overwrite_where_values` - Union[tuple, dict, None] : (Default: ())
	"""
	# process
	ground_sql:str = """
		SELECT `discord_blacklist_whitelistlink`.* 
		FROM `discord_blacklist_whitelistlink`
		WHERE 1 = 1"""

	sql:str = ""
	values:tuple = ()

	# Optional 'search' keywords
	link_id:Union[int, str, None] = search.get("link_id", None)
	if link_id is not None:
		sql += " AND `discord_blacklist_whitelistlink`.`id` = %s"
		values += (int(link_id),)

	guild_id:Optional[str] = search.get("guild_id", None)
	if guild_id is not None:
		sql += " AND `discord_blacklist_whitelistlink`.`guild_id` = %s"
		values += (str(guild_id),)

	link:Optional[str] = search.get("link", None)
	if link is not None:
		sql += " AND `discord_blacklist_whitelistlink`.`link` = %s"
		values += (str(link),)

	# Optional 'contains' keywords
	link_contains:Optional[str] = search.get("link_contains", None)
	if link_contains is not None:
		link_contains = f"%{link_contains}%"
		sql += " AND `discord_blacklist_whitelistlink`.`link` LIKE %s"
		values += (str(link_contains),)

	# Special
	count_mode:bool = search.get("count_mode", False)
	if count_mode:
		search["limit"] = None
		search["offset"] = None
		ground_sql: str = """
			SELECT COUNT(*) AS `I`
			FROM `discord_blacklist_whitelistlink`
			WHERE 1 = 1"""

	overwrite_where:Optional[str] = search.get("overwrite_where", None)
	overwrite_where_values:Union[tuple, dict, None] = search.get("overwrite_where_values", ())
	if overwrite_where:
		sql = overwrite_where
		values = overwrite_where_values

	# Other
	order_str:str = search.get("order_str", "ORDER BY `discord_blacklist_whitelistlink`.`id` ASC")
	sql += f" {order_str}"

	limit:Optional[int] = search.get("limit", None)
	offset:int = search.get("offset", 0)
	if limit:
		sql += f" LIMIT {limit}"
		if offset:
			sql += f" OFFSET {offset}"

	res:List[dict] = cls.BASE.PhaazeDB.selectQuery(ground_sql+sql, values)

	if count_mode:
		return res[0]['I']
	else:
		return [DiscordWhitelistedLink(x) for x in res]

# discord_disabled_levelchannel
async def getDiscordServerLevelDisabledChannels(cls:"PhaazebotDiscord", **search) -> Union[List[DiscordLevelDisabledChannel], int]:
	"""
	Get channels where levels are disabled for a guild.
	Returns a list of DiscordLevelDisabledChannel().

	Optional 'search' keywords:
	---------------------------
	* `entry_id` - Union[int, str, None] : (Default: None)
	* `guild_id` - Optional[str] : (Default: None)
	* `channel_id` - Optional[str] : (Default: None)

	Other:
	------
	* `order_str` - str : (Default: "ORDER BY discord_disabled_levelchannel.id ASC")
	* `limit` - Optional[int] : (Default: None)
	* `offset` - int : (Default: 0)

	Special:
	--------
	* `count_mode` - bool : (Default: False)
		* [returns COUNT(*) as int, disables: `limit`, `offset`]
	* `overwrite_where` - Optional[str] : (Default: None)
		* [Overwrites everything, appended after "1=1", so start with "AND field = %s"]
		* [Without `limit`, `offset`, `order` and `group by`]
	* `overwrite_where_values` - Union[tuple, dict, None] : (Default: ())
	"""
	# process
	ground_sql:str = """
		SELECT `discord_disabled_levelchannel`.* 
		FROM `discord_disabled_levelchannel`
		WHERE 1 = 1"""

	sql:str = ""
	values:tuple = ()

	# Optional 'search' keywords
	entry_id:Union[int, str, None] = search.get("entry_id", None)
	if entry_id is not None:
		sql += " AND `discord_disabled_levelchannel`.`id` = %s"
		values += (int(entry_id),)

	guild_id:Optional[str] = search.get("guild_id", None)
	if guild_id is not None:
		sql += " AND `discord_disabled_levelchannel`.`guild_id` = %s"
		values += (str(guild_id),)

	channel_id:Optional[str] = search.get("channel_id", None)
	if channel_id is not None:
		sql += " AND `discord_disabled_levelchannel`.`channel_id` = %s"
		values += (str(channel_id),)

	# Special
	count_mode:bool = search.get("count_mode", False)
	if count_mode:
		search["limit"] = None
		search["offset"] = None
		ground_sql: str = """
			SELECT COUNT(*) AS `I`
			FROM `discord_disabled_levelchannel`
			WHERE 1 = 1"""

	overwrite_where:Optional[str] = search.get("overwrite_where", None)
	overwrite_where_values:Union[tuple, dict, None] = search.get("overwrite_where_values", ())
	if overwrite_where:
		sql = overwrite_where
		values = overwrite_where_values

	# Other
	order_str:str = search.get("order_str", "ORDER BY `discord_disabled_levelchannel`.`id` ASC")
	sql += f" {order_str}"

	limit:Optional[int] = search.get("limit", None)
	offset:int = search.get("offset", 0)
	if limit:
		sql += f" LIMIT {limit}"
		if offset:
			sql += f" OFFSET {offset}"

	res:List[dict] = cls.BASE.PhaazeDB.selectQuery(ground_sql+sql, values)

	if count_mode:
		return res[0]['I']
	else:
		return [DiscordLevelDisabledChannel(x) for x in res]

# discord_disabled_regularchannel
async def getDiscordServerRegularDisabledChannels(cls:"PhaazebotDiscord", **search) -> Union[List[DiscordRegularDisabledChannel], int]:
	"""
	Get channels where regular commands (requirement = regular) are disabled for a guild.
	Returns a list of DiscordRegularDisabledChannel().

	Optional 'search' keywords:
	---------------------------
	* `entry_id` - Union[int, str, None] : (Default: None)
	* `guild_id` - Optional[str] : (Default: None)
	* `channel_id` - Optional[str] : (Default: None)

	Other:
	------
	* `order_str` - str : (Default: "ORDER BY discord_disabled_regularchannel.id ASC")
	* `limit` - Optional[int] : (Default: None)
	* `offset` - int : (Default: 0)

	Special:
	--------
	* `count_mode` - bool : (Default: False)
		* [returns COUNT(*) as int, disables: `limit`, `offset`]
	* `overwrite_where` - Optional[str] : (Default: None)
		* [Overwrites everything, appended after "1=1", so start with "AND field = %s"]
		* [Without `limit`, `offset`, `order` and `group by`]
	* `overwrite_where_values` - Union[tuple, dict, None] : (Default: ())
	"""
	# process
	ground_sql:str = """
		SELECT `discord_disabled_regularchannel`.* 
		FROM `discord_disabled_regularchannel`
		WHERE 1 = 1"""

	sql:str = ""
	values:tuple = ()

	# Optional 'search' keywords
	entry_id:Union[int, str, None] = search.get("entry_id", None)
	if entry_id is not None:
		sql += " AND `discord_disabled_regularchannel`.`id` = %s"
		values += (int(entry_id),)

	guild_id:Optional[str] = search.get("guild_id", None)
	if guild_id is not None:
		sql += " AND `discord_disabled_regularchannel`.`guild_id` = %s"
		values += (str(guild_id),)

	channel_id:Optional[str] = search.get("channel_id", None)
	if channel_id is not None:
		sql += " AND `discord_disabled_regularchannel`.`channel_id` = %s"
		values += (str(channel_id),)

	# Special
	count_mode:bool = search.get("count_mode", False)
	if count_mode:
		search["limit"] = None
		search["offset"] = None
		ground_sql: str = """
			SELECT COUNT(*) AS `I`
			FROM `discord_disabled_regularchannel`
			WHERE 1 = 1"""

	overwrite_where:Optional[str] = search.get("overwrite_where", None)
	overwrite_where_values:Union[tuple, dict, None] = search.get("overwrite_where_values", ())
	if overwrite_where:
		sql = overwrite_where
		values = overwrite_where_values

	# Other
	order_str:str = search.get("order_str", "ORDER BY `discord_disabled_regularchannel`.`id` ASC")
	sql += f" {order_str}"

	limit:Optional[int] = search.get("limit", None)
	offset:int = search.get("offset", 0)
	if limit:
		sql += f" LIMIT {limit}"
		if offset:
			sql += f" OFFSET {offset}"

	res:List[dict] = cls.BASE.PhaazeDB.selectQuery(ground_sql+sql, values)

	if count_mode:
		return res[0]['I']
	else:
		return [DiscordRegularDisabledChannel(x) for x in res]

# discord_disabled_normalchannel
async def getDiscordServerNormalDisabledChannels(cls:"PhaazebotDiscord", **search) -> Union[List[DiscordNormalDisabledChannel], int]:
	"""
	Get channels where normal commands (requirement = everyone) are disabled for a guild.
	Returns a list of DiscordNormalDisabledChannel().

	Optional 'search' keywords:
	---------------------------
	* `entry_id` - Union[int, str, None] : (Default: None)
	* `guild_id` - Optional[str] : (Default: None)
	* `channel_id` - Optional[str] : (Default: None)

	Other:
	------
	* `order_str` - str : (Default: "ORDER BY discord_disabled_normalchannel.id ASC")
	* `limit` - Optional[int] : (Default: None)
	* `offset` - int : (Default: 0)

	Special:
	--------
	* `count_mode` - bool : (Default: False)
		* [returns COUNT(*) as int, disables: `limit`, `offset`]
	* `overwrite_where` - Optional[str] : (Default: None)
		* [Overwrites everything, appended after "1=1", so start with "AND field = %s"]
		* [Without `limit`, `offset`, `order` and `group by`]
	* `overwrite_where_values` - Union[tuple, dict, None] : (Default: ())
	"""
	# process
	ground_sql:str = """
		SELECT `discord_disabled_normalchannel`.* 
		FROM `discord_disabled_normalchannel`
		WHERE 1 = 1"""

	sql:str = ""
	values:tuple = ()

	# Optional 'search' keywords
	entry_id:Union[int, str, None] = search.get("entry_id", None)
	if entry_id is not None:
		sql += " AND `discord_disabled_normalchannel`.`id` = %s"
		values += (int(entry_id),)

	guild_id:Optional[str] = search.get("guild_id", None)
	if guild_id is not None:
		sql += " AND `discord_disabled_normalchannel`.`guild_id` = %s"
		values += (str(guild_id),)

	channel_id:Optional[str] = search.get("channel_id", None)
	if channel_id is not None:
		sql += " AND `discord_disabled_normalchannel`.`channel_id` = %s"
		values += (str(channel_id),)

	# Special
	count_mode:bool = search.get("count_mode", False)
	if count_mode:
		search["limit"] = None
		search["offset"] = None
		ground_sql: str = """
			SELECT COUNT(*) AS `I`
			FROM `discord_disabled_normalchannel`
			WHERE 1 = 1"""

	overwrite_where:Optional[str] = search.get("overwrite_where", None)
	overwrite_where_values:Union[tuple, dict, None] = search.get("overwrite_where_values", ())
	if overwrite_where:
		sql = overwrite_where
		values = overwrite_where_values

	# Other
	order_str:str = search.get("order_str", "ORDER BY `discord_disabled_normalchannel`.`id` ASC")
	sql += f" {order_str}"

	limit:Optional[int] = search.get("limit", None)
	offset:int = search.get("offset", 0)
	if limit:
		sql += f" LIMIT {limit}"
		if offset:
			sql += f" OFFSET {offset}"

	res:List[dict] = cls.BASE.PhaazeDB.selectQuery(ground_sql+sql, values)

	if count_mode:
		return res[0]['I']
	else:
		return [DiscordNormalDisabledChannel(x) for x in res]

# discord_disabled_quotechannel
async def getDiscordServerQuoteDisabledChannels(cls:"PhaazebotDiscord", **search) -> Union[List[DiscordQuoteDisabledChannel], int]:
	"""
	Get channels where quotes are disabled for a guild.
	Returns a list of DiscordQuoteDisabledChannel().

	Optional 'search' keywords:
	---------------------------
	* `entry_id` - Union[int, str, None] : (Default: None)
	* `guild_id` - Optional[str] : (Default: None)
	* `channel_id` - Optional[str] : (Default: None)

	Other:
	------
	* `order_str` - str : (Default: "ORDER BY discord_disabled_quotechannel.id ASC")
	* `limit` - Optional[int] : (Default: None)
	* `offset` - int : (Default: 0)

	Special:
	--------
	* `count_mode` - bool : (Default: False)
		* [returns COUNT(*) as int, disables: `limit`, `offset`]
	* `overwrite_where` - Optional[str] : (Default: None)
		* [Overwrites everything, appended after "1=1", so start with "AND field = %s"]
		* [Without `limit`, `offset`, `order` and `group by`]
	* `overwrite_where_values` - Union[tuple, dict, None] : (Default: ())
	"""
	# process
	ground_sql:str = """
		SELECT `discord_disabled_quotechannel`.* 
		FROM `discord_disabled_quotechannel`
		WHERE 1 = 1"""

	sql:str = ""
	values:tuple = ()

	# Optional 'search' keywords
	entry_id:Union[int, str, None] = search.get("entry_id", None)
	if entry_id is not None:
		sql += " AND `discord_disabled_quotechannel`.`id` = %s"
		values += (int(entry_id),)

	guild_id:Optional[str] = search.get("guild_id", None)
	if guild_id is not None:
		sql += " AND `discord_disabled_quotechannel`.`guild_id` = %s"
		values += (str(guild_id),)

	channel_id:Optional[str] = search.get("channel_id", None)
	if channel_id is not None:
		sql += " AND `discord_disabled_quotechannel`.`channel_id` = %s"
		values += (str(channel_id),)

	# Special
	count_mode:bool = search.get("count_mode", False)
	if count_mode:
		search["limit"] = None
		search["offset"] = None
		ground_sql: str = """
			SELECT COUNT(*) AS `I`
			FROM `discord_disabled_quotechannel`
			WHERE 1 = 1"""

	overwrite_where:Optional[str] = search.get("overwrite_where", None)
	overwrite_where_values:Union[tuple, dict, None] = search.get("overwrite_where_values", ())
	if overwrite_where:
		sql = overwrite_where
		values = overwrite_where_values

	# Other
	order_str:str = search.get("order_str", "ORDER BY `discord_disabled_quotechannel`.`id` ASC")
	sql += f" {order_str}"

	limit:Optional[int] = search.get("limit", None)
	offset:int = search.get("offset", 0)
	if limit:
		sql += f" LIMIT {limit}"
		if offset:
			sql += f" OFFSET {offset}"

	res:List[dict] = cls.BASE.PhaazeDB.selectQuery(ground_sql+sql, values)

	if count_mode:
		return res[0]['I']
	else:
		return [DiscordQuoteDisabledChannel(x) for x in res]

# discord_enabled_gamechannel
async def getDiscordServerGameEnabledChannels(cls:"PhaazebotDiscord", **search) -> Union[List[DiscordGameEnabledChannel], int]:
	"""
	Get channels where games are enabled for a guild.
	Returns a list of DiscordGameEnabledChannel().

	Optional 'search' keywords:
	---------------------------
	* `entry_id` - Union[int, str, None] : (Default: None)
	* `guild_id` - Optional[str] : (Default: None)
	* `channel_id` - Optional[str] : (Default: None)

	Other:
	------
	* `order_str` - str : (Default: "ORDER BY discord_enabled_gamechannel.id ASC")
	* `limit` - Optional[int] : (Default: None)
	* `offset` - int : (Default: 0)

	Special:
	--------
	* `count_mode` - bool : (Default: False)
		* [returns COUNT(*) as int, disables: `limit`, `offset`]
	* `overwrite_where` - Optional[str] : (Default: None)
		* [Overwrites everything, appended after "1=1", so start with "AND field = %s"]
		* [Without `limit`, `offset`, `order` and `group by`]
	* `overwrite_where_values` - Union[tuple, dict, None] : (Default: ())
	"""
	# process
	ground_sql:str = """
		SELECT `discord_enabled_gamechannel`.* 
		FROM `discord_enabled_gamechannel`
		WHERE 1 = 1"""

	sql:str = ""
	values:tuple = ()

	# Optional 'search' keywords
	entry_id:Union[int, str, None] = search.get("entry_id", None)
	if entry_id is not None:
		sql += " AND `discord_enabled_gamechannel`.`id` = %s"
		values += (int(entry_id),)

	guild_id:Optional[str] = search.get("guild_id", None)
	if guild_id is not None:
		sql += " AND `discord_enabled_gamechannel`.`guild_id` = %s"
		values += (str(guild_id),)

	channel_id:Optional[str] = search.get("channel_id", None)
	if channel_id is not None:
		sql += " AND `discord_enabled_gamechannel`.`channel_id` = %s"
		values += (str(channel_id),)

	# Special
	count_mode:bool = search.get("count_mode", False)
	if count_mode:
		search["limit"] = None
		search["offset"] = None
		ground_sql: str = """
			SELECT COUNT(*) AS `I`
			FROM `discord_enabled_gamechannel`
			WHERE 1 = 1"""

	overwrite_where:Optional[str] = search.get("overwrite_where", None)
	overwrite_where_values:Union[tuple, dict, None] = search.get("overwrite_where_values", ())
	if overwrite_where:
		sql = overwrite_where
		values = overwrite_where_values

	# Other
	order_str:str = search.get("order_str", "ORDER BY `discord_enabled_gamechannel`.`id` ASC")
	sql += f" {order_str}"

	limit:Optional[int] = search.get("limit", None)
	offset:int = search.get("offset", 0)
	if limit:
		sql += f" LIMIT {limit}"
		if offset:
			sql += f" OFFSET {offset}"

	res:List[dict] = cls.BASE.PhaazeDB.selectQuery(ground_sql+sql, values)

	if count_mode:
		return res[0]['I']
	else:
		return [DiscordGameEnabledChannel(x) for x in res]

# discord_enabled_nsfwchannel
async def getDiscordServerNsfwEnabledChannels(cls:"PhaazebotDiscord", **search) -> Union[List[DiscordNsfwEnabledChannel], int]:
	"""
	Get channels where nsfw commands are enabled.
	Returns a list of DiscordNsfwEnabledChannel().

	Optional 'search' keywords:
	---------------------------
	* `entry_id` - Union[int, str, None] : (Default: None)
	* `guild_id` - Optional[str] : (Default: None)
	* `channel_id` - Optional[str] : (Default: None)

	Other:
	------
	* `order_str` - str : (Default: "ORDER BY discord_enabled_nsfwchannel.id ASC")
	* `limit` - Optional[int] : (Default: None)
	* `offset` - int : (Default: 0)

	Special:
	--------
	* `count_mode` - bool : (Default: False)
		* [returns COUNT(*) as int, disables: `limit`, `offset`]
	* `overwrite_where` - Optional[str] : (Default: None)
		* [Overwrites everything, appended after "1=1", so start with "AND field = %s"]
		* [Without `limit`, `offset`, `order` and `group by`]
	* `overwrite_where_values` - Union[tuple, dict, None] : (Default: ())
	"""
	# process
	ground_sql:str = """
		SELECT `discord_enabled_nsfwchannel`.* 
		FROM `discord_enabled_nsfwchannel`
		WHERE 1 = 1"""

	sql:str = ""
	values:tuple = ()

	# Optional 'search' keywords
	entry_id:Union[int, str, None] = search.get("entry_id", None)
	if entry_id is not None:
		sql += " AND `discord_enabled_nsfwchannel`.`id` = %s"
		values += (int(entry_id),)

	guild_id:Optional[str] = search.get("guild_id", None)
	if guild_id is not None:
		sql += " AND `discord_enabled_nsfwchannel`.`guild_id` = %s"
		values += (str(guild_id),)

	channel_id:Optional[str] = search.get("channel_id", None)
	if channel_id is not None:
		sql += " AND `discord_enabled_nsfwchannel`.`channel_id` = %s"
		values += (str(channel_id),)

	# Special
	count_mode:bool = search.get("count_mode", False)
	if count_mode:
		search["limit"] = None
		search["offset"] = None
		ground_sql: str = """
			SELECT COUNT(*) AS `I`
			FROM `discord_enabled_nsfwchannel`
			WHERE 1 = 1"""

	overwrite_where:Optional[str] = search.get("overwrite_where", None)
	overwrite_where_values:Union[tuple, dict, None] = search.get("overwrite_where_values", ())
	if overwrite_where:
		sql = overwrite_where
		values = overwrite_where_values

	# Other
	order_str:str = search.get("order_str", "ORDER BY `discord_enabled_nsfwchannel`.`id` ASC")
	sql += f" {order_str}"

	limit:Optional[int] = search.get("limit", None)
	offset:int = search.get("offset", 0)
	if limit:
		sql += f" LIMIT {limit}"
		if offset:
			sql += f" OFFSET {offset}"

	res:List[dict] = cls.BASE.PhaazeDB.selectQuery(ground_sql+sql, values)

	if count_mode:
		return res[0]['I']
	else:
		return [DiscordNsfwEnabledChannel(x) for x in res]

# discord_log
async def getDiscordServerLogs(cls:"PhaazebotDiscord", **search) -> List[DiscordLog]:
	"""
	Get log entry's.
	Returns a list of DiscordLog().

	Optional 'search' keywords:
	---------------------------
	* `log_id` - Union[int, str, None] : (Default: None)
	* `guild_id` - Optional[str] : (Default: None)
	* `content` - Optional[str] : (Default: None)
	* `event_value` - Optional[int] : (Default: None)
	* `initiator_id` - Optional[str] : (Default: None)

	Optional 'contains' keywords:
	-----------------------------
	* `content_contains` Optional[str]: (Default: None) [DB uses LIKE on `content`]

	Optional 'between' keywords:
	----------------------------
	* `created_at_between` - Tuple[from:str, to:str] : (Default: None) [DB uses >= and <=]

	Other:
	------
	* `order_str` - str : (Default: "ORDER BY discord_log.id ASC")
	* `limit` - Optional[int] : (Default: None)
	* `offset` - int : (Default: 0)

	Special:
	--------
	* `count_mode` - bool : (Default: False)
		* [returns COUNT(*) as int, disables: `limit`, `offset`]
	* `overwrite_where` - Optional[str] : (Default: None)
		* [Overwrites everything, appended after "1=1", so start with "AND field = %s"]
		* [Without `limit`, `offset`, `order` and `group by`]
	* `overwrite_where_values` - Union[tuple, dict, None] : (Default: ())
	"""
	# process
	ground_sql:str = """
		SELECT `discord_log`.* FROM `discord_log`
		WHERE 1 = 1"""

	sql:str = ""
	values:tuple = ()

	# Optional 'search' keywords
	log_id:Union[str, int, None] = search.get("log_id", None)
	if log_id is not None:
		sql += " AND `discord_log`.`id` = %s"
		values += (int(log_id),)

	guild_id:Optional[str] = search.get("guild_id", None)
	if guild_id is not None:
		sql += " AND `discord_log`.`guild_id` = %s"
		values += (str(guild_id),)

	content:Optional[str] = search.get("content", None)
	if content is not None:
		sql += " AND `discord_log`.`content` = %s"
		values += (str(content),)

	event_value:Optional[int] = search.get("event_value", None)
	if event_value is not None:
		sql += " AND `discord_log`.`event_value` = %s"
		values += (int(event_value),)

	initiator_id:Optional[str] = search.get("initiator_id", None)
	if initiator_id is not None:
		sql += " AND `discord_log`.`initiator_id` = %s"
		values += (str(initiator_id),)

	# Optional 'contains' keywords
	content_contains:Optional[str] = search.get("content_contains", None)
	if content_contains is not None:
		content_contains = f"%{content_contains}%"
		sql += " AND `discord_log`.`content` LIKE %s"
		values += (str(content_contains),)

	# Optional 'between' keywords
	created_at_between:Optional[tuple] = search.get("created_at_between", None)
	if created_at_between is not None:
		from_:Optional[int] = created_at_between[0]
		to_:Optional[int] = created_at_between[1]

		if (from_ is not None) and (to_ is not None):
			sql += " AND `discord_log`.`created_at` BETWEEN %s AND %s"
			values += (str(from_), str(to_))

		if (from_ is not None) and (to_ is None):
			sql += " AND `discord_log`.`created_at` >= %s"
			values += (str(from_),)

		if (from_ is None) and (to_ is not None):
			sql += " AND `discord_log`.`created_at` <= %s"
			values += (str(to_),)

	# Special
	count_mode:bool = search.get("count_mode", False)
	if count_mode:
		search["limit"] = None
		search["offset"] = None
		ground_sql: str = """
			SELECT COUNT(*) AS `I`
			FROM `discord_log`
			WHERE 1 = 1"""

	overwrite_where:Optional[str] = search.get("overwrite_where", None)
	overwrite_where_values:Union[tuple, dict, None] = search.get("overwrite_where_values", ())
	if overwrite_where:
		sql = overwrite_where
		values = overwrite_where_values

	# Other
	order_str:str = search.get("order_str", "ORDER BY `discord_log`.`id` ASC")
	sql += f" {order_str}"

	limit:Optional[int] = search.get("limit", None)
	offset:int = search.get("offset", 0)
	if limit:
		sql += f" LIMIT {limit}"
		if offset:
			sql += f" OFFSET {offset}"

	res:List[dict] = cls.BASE.PhaazeDB.selectQuery(ground_sql+sql, values)

	if count_mode:
		return res[0]['I']
	else:
		return [DiscordLog(x) for x in res]
