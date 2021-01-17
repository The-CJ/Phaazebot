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
		values += (int(trigger),)

	complex_:Optional[int] = search.get("complex", None)
	if complex_ is not None:
		sql += " AND `discord_command`.`complex_` = %s"
		values += (int(complex_),)

	function:Optional[str] = search.get("function", None)
	if function is not None:
		sql += " AND `discord_command`.`function` = %s"
		values += (str(function),)

	hidden:Optional[int] = search.get("hidden", 0)
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
				RANK() OVER (PARTITION BY `guild_id` ORDER BY `exp` DESC) AS `rank`,
				(`discord_regular`.`id` IS NOT NULL) AS `regular`
			FROM `discord_user`
			LEFT JOIN `discord_user_medal`
				ON `discord_user_medal`.`guild_id` = `discord_user`.`guild_id`
					AND `discord_user_medal`.`member_id` = `discord_user`.`member_id`
			LEFT JOIN `discord_regular`
				ON `discord_regular`.`guild_id` = `discord_user`.`guild_id`
					AND `discord_regular`.`member_id` = `discord_user`.`member_id`
			GROUP BY `discord_user`.`guild_id`, `discord_user`.`member_id`
		)
		SELECT `discord_user`.* FROM `discord_user` WHERE 1 = 1"""
	sql:str = ""
	values:tuple = ()

	# Optional 'search' keywords
	member_id:Optional[str] = search.get("member_id", None)
	if member_id is not None:
		sql += " AND `discord_user`.`member_id` = %s"
		values += (str(member_id),)

	guild_id:Optional[str] = search.get("guild_id", None)
	if guild_id is not None:
		sql += " AND `discord_user`.`guild_id` = %s"
		values += (str(guild_id),)

	edited:Optional[int] = search.get("edited", None)
	if edited is not None:
		sql += " AND `discord_user`.`edited` = %s"
		values += (int(edited),)

	on_server:int = search.get("on_server", 1)
	if on_server is not None:
		sql += " AND `discord_user`.`on_server` = %s"
		values += (int(on_server),)

	regular:int = search.get("regular", 1)
	if regular is not None:
		sql += " AND `discord_user`.`regular` = %s"
		values += (int(regular),)

	username:Optional[str] = search.get("username", None)
	if username is not None:
		sql += " AND `discord_user`.`username` = %s"
		values += (str(username),)

	nickname:Optional[str] = search.get("nickname", None)
	if nickname is not None:
		sql += " AND `discord_user`.`nickname` = %s"
		values += (str(nickname),)

	# Optional 'contains' keywords
	name_contains:Optional[str] = search.get("name_contains", None)
	if name_contains is not None:
		name_contains = f"%{name_contains}%"
		sql += " AND ( 1 = 2"
		sql += " OR `discord_user`.`username` LIKE %s"
		sql += " OR `discord_user`.`nickname` LIKE %s"
		sql += " )"
		values += (str(name_contains),) * 2

	# Optional 'between' keywords
	rank_between:Optional[tuple] = search.get("rank_between", None)
	if rank_between is not None:
		from_:Optional[int] = rank_between[0]
		to_:Optional[int] = rank_between[1]

		if (from_ is not None) and (to_ is not None):
			sql += " AND `discord_user`.`rank` BETWEEN %s AND %s"
			values += (int(from_), int(to_))

		if (from_ is not None) and (to_ is None):
			sql += " AND `discord_user`.`rank` >= %s"
			values += (int(from_),)

		if (from_ is None) and (to_ is not None):
			sql += " AND `discord_user`.`rank` <= %s"
			values += (int(to_),)

	exp_between:Optional[tuple] = search.get("exp_between", None)
	if exp_between is not None:
		from_:Optional[int] = exp_between[0]
		to_:Optional[int] = exp_between[1]

		if (from_ is not None) and (to_ is not None):
			sql += " AND `discord_user`.`exp` BETWEEN %s AND %s"
			values += (int(from_), int(to_))

		if (from_ is not None) and (to_ is None):
			sql += " AND `discord_user`.`exp` >= %s"
			values += (int(from_),)

		if (from_ is None) and (to_ is not None):
			sql += " AND `discord_user`.`exp` <= %s"
			values += (int(to_),)

	currency_between:Optional[tuple] = search.get("currency_between", None)
	if currency_between is not None:
		from_:Optional[int] = currency_between[0]
		to_:Optional[int] = currency_between[1]

		if (from_ is not None) and (to_ is not None):
			sql += " AND `discord_user`.`currency` BETWEEN %s AND %s"
			values += (int(from_), int(to_))

		if (from_ is not None) and (to_ is None):
			sql += " AND `discord_user`.`currency` >= %s"
			values += (int(from_),)

		if (from_ is None) and (to_ is not None):
			sql += " AND `discord_user`.`currency` <= %s"
			values += (int(to_),)

	# Special
	count_mode:bool = search.get("count_mode", False)
	if count_mode:
		search["limit"] = None
		search["offset"] = None
		ground_sql: str = """
			SELECT COUNT(*) AS `I`
			FROM `discord_user`
			WHERE 1 = 1"""

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
		WHERE `discord_quote`.`guild_id` = %s"""

	sql:str = ""
	values:tuple = ()

	# Optional 'search' keywords
	quote_id:Union[int, str, None] = search.get("quote_id", None)
	if quote_id is not None:
		sql += " AND `discord_quote`.`id` = %s"
		values += (int(quote_id),)

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
	if twitch_channel_name:
		sql += " AND `twitch_user_name`.`twitch_channel_name` = %s"
		values += (str(twitch_channel_name),)

	# Optional 'contains' keywords
	custom_msg_contains:Optional[str] = search.get("custom_msg_contains", None)
	if custom_msg_contains:
		custom_msg_contains = f"%{custom_msg_contains}%"
		sql += " AND `discord_twitch_alert`.`custom_msg` LIKE %s"
		values += (str(custom_msg_contains),)

	twitch_channel_name_contains:Optional[str] = search.get("twitch_channel_name_contains", None)
	if twitch_channel_name_contains:
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
	if word_contains:
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
async def getDiscordServerExceptionRoles(cls:"PhaazebotDiscord", guild_id:str, **search) -> List[DiscordWhitelistedRole]:
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
		SELECT `discord_blacklist_whitelistrole`.* FROM `discord_blacklist_whitelistrole`
		WHERE `discord_blacklist_whitelistrole`.`guild_id` = %s"""

	values:tuple = (str(guild_id),)

	if exceptionrole_id:
		sql += " AND `discord_blacklist_whitelistrole`.`id` = %s"
		values += (int(exceptionrole_id),)

	if role_id:
		sql += " AND `discord_blacklist_whitelistrole`.`role_id` = %s"
		values += (str(role_id),)

	sql += f" {order_str}"

	if limit:
		sql += f" LIMIT {limit}"
		if offset:
			sql += f" OFFSET {offset}"

	res:List[dict] = cls.BASE.PhaazeDB.selectQuery(sql, values)

	if res:
		return [DiscordWhitelistedRole(x) for x in res]

	else:
		return []

async def getDiscordServerExceptionRoleAmount(cls:"PhaazebotDiscord", guild_id:str, where:str="1=1", where_values:tuple=()) -> int:

	sql:str = f"""
		SELECT COUNT(*) AS `I` FROM `discord_blacklist_whitelistrole`
		WHERE `discord_blacklist_whitelistrole`.`guild_id` = %s AND {where}"""

	values:tuple = (str(guild_id),) + where_values

	res:List[dict] = cls.BASE.PhaazeDB.selectQuery(sql, values)

	return res[0]["I"]

# discord_blacklist_whitelistlink
async def getDiscordServerWhitelistedLinks(cls:"PhaazebotDiscord", guild_id:str, **search) -> List[DiscordWhitelistedLink]:
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
		SELECT `discord_blacklist_whitelistlink`.* FROM `discord_blacklist_whitelistlink`
		WHERE `discord_blacklist_whitelistlink`.`guild_id` = %s"""

	values:tuple = (str(guild_id),)

	if link_id:
		sql += " AND `discord_blacklist_whitelistlink`.`id` = %s"
		values += (int(link_id),)

	if link:
		sql += " AND `discord_blacklist_whitelistlink`.`link` = %s"
		values += (str(link),)

	sql += f" {order_str}"

	if limit:
		sql += f" LIMIT {limit}"
		if offset:
			sql += f" OFFSET {offset}"

	res:List[dict] = cls.BASE.PhaazeDB.selectQuery(sql, values)

	if res:
		return [DiscordWhitelistedLink(x) for x in res]

	else:
		return []

async def getDiscordServerWhitelistedLinkAmount(cls:"PhaazebotDiscord", guild_id:str, where:str="1=1", where_values:tuple=()) -> int:

	sql:str = f"""
		SELECT COUNT(*) AS `I` FROM `discord_blacklist_whitelistlink`
		WHERE `discord_blacklist_whitelistlink`.`guild_id` = %s AND {where}"""

	values:tuple = (str(guild_id),) + where_values

	res:List[dict] = cls.BASE.PhaazeDB.selectQuery(sql, values)

	return res[0]["I"]

# discord_disabled_levelchannel
async def getDiscordServerLevelDisabledChannels(cls:"PhaazebotDiscord", guild_id:str, **search) -> List[DiscordLevelDisabledChannel]:
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
		SELECT `discord_disabled_levelchannel`.* FROM `discord_disabled_levelchannel`
		WHERE `discord_disabled_levelchannel`.`guild_id` = %s"""

	values:tuple = (str(guild_id),)

	if entry_id:
		sql += " AND `discord_disabled_levelchannel`.`id` = %s"
		values += (int(entry_id),)

	if channel_id:
		sql += " AND `discord_disabled_levelchannel`.`channel_id` = %s"
		values += (str(channel_id),)

	sql += f" {order_str}"

	if limit:
		sql += f" LIMIT {limit}"
		if offset:
			sql += f" OFFSET {offset}"

	res:List[dict] = cls.BASE.PhaazeDB.selectQuery(sql, values)

	if res:
		return [DiscordLevelDisabledChannel(x) for x in res]

	else:
		return []

async def getDiscordServerLevelDisabledChannelAmount(cls:"PhaazebotDiscord", guild_id:str, where:str="1=1", where_values:tuple=()) -> int:

	sql:str = f"""
		SELECT COUNT(*) AS `I` FROM `discord_disabled_levelchannel`
		WHERE `discord_disabled_levelchannel`.`guild_id` = %s AND {where}"""

	values:tuple = (str(guild_id),) + where_values

	res:List[dict] = cls.BASE.PhaazeDB.selectQuery(sql, values)

	return res[0]["I"]

# discord_disabled_regularchannel
async def getDiscordServerRegularDisabledChannels(cls:"PhaazebotDiscord", guild_id:str, **search) -> List[DiscordRegularDisabledChannel]:
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
		SELECT `discord_disabled_regularchannel`.* FROM `discord_disabled_regularchannel`
		WHERE `discord_disabled_regularchannel`.`guild_id` = %s"""

	values:tuple = (str(guild_id),)

	if entry_id:
		sql += " AND `discord_disabled_regularchannel`.`id` = %s"
		values += (int(entry_id),)

	if channel_id:
		sql += " AND `discord_disabled_regularchannel`.`channel_id` = %s"
		values += (str(channel_id),)

	sql += f" {order_str}"

	if limit:
		sql += f" LIMIT {limit}"
		if offset:
			sql += f" OFFSET {offset}"

	res:List[dict] = cls.BASE.PhaazeDB.selectQuery(sql, values)

	if res:
		return [DiscordRegularDisabledChannel(x) for x in res]

	else:
		return []

async def getDiscordServerRegularDisabledChannelAmount(cls:"PhaazebotDiscord", guild_id:str, where:str="1=1", where_values:tuple=()) -> int:

	sql:str = f"""
		SELECT COUNT(*) AS `I` FROM `discord_disabled_regularchannel`
		WHERE `discord_disabled_regularchannel`.`guild_id` = %s AND {where}"""

	values:tuple = (str(guild_id),) + where_values

	res:List[dict] = cls.BASE.PhaazeDB.selectQuery(sql, values)

	return res[0]["I"]

# discord_disabled_normalchannel
async def getDiscordServerNormalDisabledChannels(cls:"PhaazebotDiscord", guild_id:str, **search) -> List[DiscordNormalDisabledChannel]:
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
		SELECT `discord_disabled_normalchannel`.* FROM `discord_disabled_normalchannel`
		WHERE `discord_disabled_normalchannel`.`guild_id` = %s"""

	values:tuple = (str(guild_id),)

	if entry_id:
		sql += " AND `discord_disabled_normalchannel`.`id` = %s"
		values += (int(entry_id),)

	if channel_id:
		sql += " AND `discord_disabled_normalchannel`.`channel_id` = %s"
		values += (str(channel_id),)

	sql += f" {order_str}"

	if limit:
		sql += f" LIMIT {limit}"
		if offset:
			sql += f" OFFSET {offset}"

	res:List[dict] = cls.BASE.PhaazeDB.selectQuery(sql, values)

	if res:
		return [DiscordNormalDisabledChannel(x) for x in res]

	else:
		return []

async def getDiscordServerNormalDisabledChannelAmount(cls:"PhaazebotDiscord", guild_id:str, where:str="1=1", where_values:tuple=()) -> int:

	sql:str = f"""
		SELECT COUNT(*) AS `I` FROM `discord_disabled_normalchannel`
		WHERE `discord_disabled_normalchannel`.`guild_id` = %s AND {where}"""

	values:tuple = (str(guild_id),) + where_values

	res:List[dict] = cls.BASE.PhaazeDB.selectQuery(sql, values)

	return res[0]["I"]

# discord_disabled_quotechannel
async def getDiscordServerQuoteDisabledChannels(cls:"PhaazebotDiscord", guild_id:str, **search) -> List[DiscordQuoteDisabledChannel]:
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
		SELECT `discord_disabled_quotechannel`.* FROM `discord_disabled_quotechannel`
		WHERE `discord_disabled_quotechannel`.`guild_id` = %s"""

	values:tuple = (str(guild_id),)

	if entry_id:
		sql += " AND `discord_disabled_quotechannel`.`id` = %s"
		values += (int(entry_id),)

	if channel_id:
		sql += " AND `discord_disabled_quotechannel`.`channel_id` = %s"
		values += (str(channel_id),)

	sql += f" {order_str}"

	if limit:
		sql += f" LIMIT {limit}"
		if offset:
			sql += f" OFFSET {offset}"

	res:List[dict] = cls.BASE.PhaazeDB.selectQuery(sql, values)

	if res:
		return [DiscordQuoteDisabledChannel(x) for x in res]

	else:
		return []

async def getDiscordServerQuoteDisabledChannelAmount(cls:"PhaazebotDiscord", guild_id:str, where:str="1=1", where_values:tuple=()) -> int:

	sql:str = f"""
		SELECT COUNT(*) AS `I` FROM `discord_disabled_quotechannel`
		WHERE `discord_disabled_quotechannel`.`guild_id` = %s AND {where}"""

	values:tuple = (str(guild_id),) + where_values

	res:List[dict] = cls.BASE.PhaazeDB.selectQuery(sql, values)

	return res[0]["I"]

# discord_enabled_gamechannel
async def getDiscordServerGameEnabledChannels(cls:"PhaazebotDiscord", guild_id:str, **search) -> List[DiscordGameEnabledChannel]:
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
		SELECT `discord_enabled_gamechannel`.* FROM `discord_enabled_gamechannel`
		WHERE `discord_enabled_gamechannel`.`guild_id` = %s"""

	values:tuple = (str(guild_id),)

	if entry_id:
		sql += " AND `discord_enabled_gamechannel`.`id` = %s"
		values += (int(entry_id),)

	if channel_id:
		sql += " AND `discord_enabled_gamechannel`.`channel_id` = %s"
		values += (str(channel_id),)

	sql += f" {order_str}"

	if limit:
		sql += f" LIMIT {limit}"
		if offset:
			sql += f" OFFSET {offset}"

	res:List[dict] = cls.BASE.PhaazeDB.selectQuery(sql, values)

	if res:
		return [DiscordGameEnabledChannel(x) for x in res]

	else:
		return []

async def getDiscordServerGameEnabledChannelAmount(cls:"PhaazebotDiscord", guild_id:str, where:str="1=1", where_values:tuple=()) -> int:

	sql:str = f"""
		SELECT COUNT(*) AS `I` FROM `discord_enabled_gamechannel`
		WHERE `discord_enabled_gamechannel`.`guild_id` = %s AND {where}"""

	values:tuple = (str(guild_id),) + where_values

	res:List[dict] = cls.BASE.PhaazeDB.selectQuery(sql, values)

	return res[0]["I"]

# discord_enabled_nsfwchannel
async def getDiscordServerNsfwEnabledChannels(cls:"PhaazebotDiscord", guild_id:str, **search) -> List[DiscordNsfwEnabledChannel]:
	"""
	Get channels where nsfw commands are enabled for a guild.
	Returns a list of DiscordNsfwEnabledChannel().

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
		SELECT `discord_enabled_nsfwchannel`.* FROM `discord_enabled_nsfwchannel`
		WHERE `discord_enabled_nsfwchannel`.`guild_id` = %s"""

	values:tuple = (str(guild_id),)

	if entry_id:
		sql += " AND `discord_enabled_nsfwchannel`.`id` = %s"
		values += (int(entry_id),)

	if channel_id:
		sql += " AND `discord_enabled_nsfwchannel`.`channel_id` = %s"
		values += (str(channel_id),)

	sql += f" {order_str}"

	if limit:
		sql += f" LIMIT {limit}"
		if offset:
			sql += f" OFFSET {offset}"

	res:List[dict] = cls.BASE.PhaazeDB.selectQuery(sql, values)

	if res:
		return [DiscordNsfwEnabledChannel(x) for x in res]

	else:
		return []

async def getDiscordServerNsfwEnabledChannelAmount(cls:"PhaazebotDiscord", guild_id:str, where:str="1=1", where_values:tuple=()) -> int:

	sql:str = f"""
		SELECT COUNT(*) AS `I` FROM `discord_enabled_nsfwchannel`
		WHERE `discord_enabled_nsfwchannel`.`guild_id` = %s AND {where}"""

	values:tuple = (str(guild_id),) + where_values

	res:List[dict] = cls.BASE.PhaazeDB.selectQuery(sql, values)

	return res[0]["I"]

# discord_log
async def getDiscordServerLogs(cls:"PhaazebotDiscord", guild_id:str, **search) -> List[DiscordLog]:
	"""
	Get log entry's from a guild.
	Returns a list of DiscordLog().

	Optional keywords:
	------------------
	* log_id `str` or `int`: (Default: None)
	* event_value `int`: (Default: None)
	* content `str`: (Default: None)
	* content_contains `str`: (Default: None) [DB uses LIKE]
	* date_from `str`: (Default: None)
	* date_to `str`: (Default: None)
	* order_str `str`: (Default: "ORDER BY id")
	* limit `int`: (Default: None)
	* offset `int`: (Default: 0)
	"""
	# unpack
	log_id:str or int = search.get("log_id", None)
	event_value:int = search.get("event_value", None)
	content:str = search.get("content", None)
	content_contains:str = search.get("content_contains", None)
	date_from:str = search.get("date_from", None)
	date_to:str = search.get("date_to", None)
	order_str:str = search.get("order_str", "ORDER BY `id`")
	limit:int = search.get("limit", None)
	offset:int = search.get("offset", 0)

	# process
	sql:str = """
		SELECT `discord_log`.* FROM `discord_log`
		WHERE `discord_log`.`guild_id` = %s"""

	values:tuple = (str(guild_id),)

	if log_id:
		sql += " AND `discord_log`.`id` = %s"
		values += (int(log_id),)

	if event_value:
		sql += " AND `discord_log`.`event_value` = %s"
		values += (int(event_value),)

	if content:
		sql += " AND `discord_log`.`content` = %s"
		values += (str(content),)

	if content_contains:
		content_contains = f"%{content_contains}%"
		sql += " AND `discord_log`.`content` LIKE %s"
		values += (str(content_contains),)

	if date_from:
		sql += " AND `discord_log`.`created_at` > %s"
		values += (str(date_from),)

	if date_to:
		sql += " AND `discord_log`.`created_at` < %s"
		values += (str(date_to),)

	sql += f" {order_str}"

	if limit:
		sql += f" LIMIT {limit}"
		if offset:
			sql += f" OFFSET {offset}"

	res:List[dict] = cls.BASE.PhaazeDB.selectQuery(sql, values)

	if res:
		return [DiscordLog(x) for x in res]

	else:
		return []

async def getDiscordServerLogAmount(cls:"PhaazebotDiscord", guild_id:str, where:str="1=1", where_values:tuple=()) -> int:

	sql:str = f"""
		SELECT COUNT(*) AS `I` FROM `discord_log`
		WHERE `discord_log`.`guild_id` = %s AND {where}"""

	values:tuple = (str(guild_id),) + where_values

	res:List[dict] = cls.BASE.PhaazeDB.selectQuery(sql, values)

	return res[0]["I"]
