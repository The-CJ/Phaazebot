from typing import TYPE_CHECKING, List, Union, Optional
if TYPE_CHECKING:
	from Platforms.Twitch.main_twitch import PhaazebotTwitch

import twitch_irc

from Utils.Classes.twitchchannelsettings import TwitchChannelSettings
from Utils.Classes.twitchcommand import TwitchCommand
from Utils.Classes.twitchuserstats import TwitchUserStats

# twitch_settings
async def getTwitchChannelSettings(cls:"PhaazebotTwitch", origin:Union[twitch_irc.Message, str, int], prevent_new:bool=False) -> TwitchChannelSettings:
	"""
	Get channel settings for a twitch channel
	create new one if not prevented.
	Returns a TwitchChannelSettings()
	"""
	if type(origin) is twitch_irc.Message:
		channel_id:str = str(origin.room_id)

	elif type(origin) is int:
		channel_id:str = str(origin)

	else:
		channel_id:str = origin

	res:List[dict] = cls.BASE.PhaazeDB.selectQuery("""
		SELECT
			`twitch_setting`.*,
			(SELECT GROUP_CONCAT(`twitch_punish_wordblacklist`.`word` SEPARATOR ';;;') FROM `twitch_punish_wordblacklist` WHERE `twitch_punish_wordblacklist`.`channel_id` = `twitch_setting`.`channel_id`)
				AS `punish_wordblacklist`,
			(SELECT GROUP_CONCAT(`twitch_punish_linkwhitelist`.`link` SEPARATOR ';;;') FROM `twitch_punish_linkwhitelist` WHERE `twitch_punish_linkwhitelist`.`channel_id` = `twitch_setting`.`channel_id`)
				AS `punish_linkwhitelist`
		FROM `twitch_setting`
		WHERE `twitch_setting`.`channel_id` = %s
		GROUP BY `twitch_setting`.`channel_id`""",
		(channel_id,)
	)

	if res:
		return TwitchChannelSettings(res.pop(0))

	else:
		if prevent_new:
			# return a empty 'dummy'
			return TwitchChannelSettings({})
		else:
			return await makeTwitchChannelSettings(cls, channel_id)

async def makeTwitchChannelSettings(cls:"PhaazebotTwitch", channel_id:str) -> TwitchChannelSettings:
	"""
	Makes a new entry in the PhaazeDB for a twitch channel.
	Returns a TwitchChannelSettings()
	"""

	try:
		cls.BASE.PhaazeDB.insertQuery(
			table="twitch_setting",
			content=dict(channel_id=channel_id)
		)

		cls.BASE.Logger.info(f"(Twitch) New channel settings DB entry: {channel_id=}")
		return TwitchChannelSettings({"channel_id":channel_id})
	except:
		cls.BASE.Logger.critical(f"(Twitch) New channel settings failed: {channel_id=}")
		raise RuntimeError("Creating new DB entry failed")

# twitch_commands
async def getTwitchChannelCommands(cls:"PhaazebotTwitch", **search) -> Union[List[TwitchCommand], int]:
	"""
	Get channel commands.
	Returns a list of TwitchCommand()

	Optional 'search' keywords:
	---------------------------
	* `command_id` - Union[int, str, None] : (Default: None) [sets LIMIT to 1]
	* `channel_id` - Optional[str] : (Default: None)
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
	* `order_str` - str : (Default: "ORDER BY twitch_command.id ASC")
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
		SELECT `twitch_command`.*
		FROM `twitch_command`
		WHERE 1 = 1"""

	sql:str = ""
	values:tuple = ()

	# Optional 'search' keywords
	command_id:Union[str, int, None] = search.get("command_id", None)
	if command_id is not None:
		sql += " AND `twitch_command`.`id` = %s"
		values += (int(command_id),)

	channel_id:Optional[str] = search.get("channel_id", None)
	if channel_id is not None:
		sql += " AND `twitch_command`.`channel_id` = %s"
		values += (str(channel_id),)

	trigger:Optional[str] = search.get("trigger", None)
	if trigger is not None:
		sql += " AND `twitch_command`.`trigger` = %s"
		values += (str(trigger),)

	active:Optional[int] = search.get("active", 1)
	if active is not None:
		sql += " AND `twitch_command`.`active` = %s"
		values += (int(trigger),)

	complex_:Optional[int] = search.get("complex", None)
	if complex_ is not None:
		sql += " AND `twitch_command`.`complex` = %s"
		values += (int(complex_),)

	function:Optional[str] = search.get("function", None)
	if function is not None:
		sql += " AND `twitch_command`.`function` = %s"
		values += (str(function),)

	hidden:Optional[int] = search.get("hidden", 0)
	if hidden is not None:
		sql += " AND `twitch_command`.`hidden` = %s"
		values += (int(hidden),)

	require:Optional[int] = search.get("require", None)
	if require is not None:
		sql += " AND `twitch_command`.`require` = %s"
		values += (int(require),)

	# Optional 'contains' keywords
	content_contains:Optional[str] = search.get("content_contains", None)
	if content_contains is not None:
		content_contains = f"%{content_contains}%"
		sql += " AND `twitch_command`.`content` LIKE %s"
		values += (str(content_contains),)

	# Optional 'between' keywords
	cooldown_between:Optional[tuple] = search.get("cooldown_between", None)
	if cooldown_between is not None:
		from_:Optional[int] = cooldown_between[0]
		to_:Optional[int] = cooldown_between[1]

		if (from_ is not None) and (to_ is not None):
			sql += " AND `twitch_command`.`cooldown` BETWEEN %s AND %s"
			values += (int(from_), int(to_))

		if (from_ is not None) and (to_ is None):
			sql += " AND `twitch_command`.`cooldown` >= %s"
			values += (int(from_),)

		if (from_ is None) and (to_ is not None):
			sql += " AND `twitch_command`.`cooldown` <= %s"
			values += (int(to_),)

	required_currency_between:Optional[tuple] = search.get("required_currency_between", None)
	if required_currency_between is not None:
		from_:Optional[int] = required_currency_between[0]
		to_:Optional[int] = required_currency_between[1]

		if (from_ is not None) and (to_ is not None):
			sql += " AND `twitch_command`.`required_currency` BETWEEN %s AND %s"
			values += (int(from_), int(to_))

		if (from_ is not None) and (to_ is None):
			sql += " AND `twitch_command`.`required_currency` >= %s"
			values += (int(from_),)

		if (from_ is None) and (to_ is not None):
			sql += " AND `twitch_command`.`required_currency` <= %s"
			values += (int(to_),)

	uses_between:Optional[tuple] = search.get("uses_between", None)
	if uses_between is not None:
		from_:Optional[int] = uses_between[0]
		to_:Optional[int] = uses_between[1]

		if (from_ is not None) and (to_ is not None):
			sql += " AND `twitch_command`.`uses` BETWEEN %s AND %s"
			values += (int(from_), int(to_))

		if (from_ is not None) and (to_ is None):
			sql += " AND `twitch_command`.`uses` >= %s"
			values += (int(from_),)

		if (from_ is None) and (to_ is not None):
			sql += " AND `twitch_command`.`uses` <= %s"
			values += (int(to_),)

	# Special
	count_mode:bool = search.get("count_mode", False)
	if count_mode:
		search["limit"] = None
		search["offset"] = None
		ground_sql: str = """
			SELECT COUNT(*) AS `I`
			FROM `twitch_command`
			WHERE 1 = 1"""

	overwrite_where:Optional[str] = search.get("overwrite_where", None)
	overwrite_where_values: Union[tuple, dict, None] = search.get("overwrite_where_values", ())
	if overwrite_where:
		sql = overwrite_where
		values = overwrite_where_values

	# Other
	order_str:str = search.get("order_str", "ORDER BY `twitch_command`.`id` ASC")
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
		return [TwitchCommand(x) for x in res]

# twitch_user
async def getTwitchChannelUsers(cls:"PhaazebotTwitch", **search) -> Union[List[TwitchUserStats], int]:
	"""
	Get channel levels and stats.
	Returns a list of TwitchUserStats().

	Optional 'search' keywords:
	---------------------------
	* `user_id` - Optional[str] : (Default: None)
	* `channel_id` - Optional[str] : (Default: None)
	* `edited` - Optional[int] : (Default: None) [0 = not edited, 1 = only edited]
	* `name` - Optional[str] : (Default: None)
	* `display_name` - Optional[str] : (Default: None)

	Optional 'contains' keywords:
	-----------------------------
	* `name_contains` Optional[str]: (Default: None) [DB uses LIKE on `name`, `display_name`]

	Optional 'between' keywords:
	----------------------------
	* `rank_between` - Tuple[from:int, to:int] : (Default: None) [DB uses >= and <=]
	* `amount_currency_between` - Tuple[from:int, to:int] : (Default: None) [DB uses >= and <=]
	* `amount_time_between` - Tuple[from:int, to:int] : (Default: None) [DB uses >= and <=]

	Other:
	------
	* `order_str` - str : (Default: "ORDER BY twitch_user.id ASC")
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
		WITH `twitch_user` AS (
			SELECT
				`twitch_user`.*,
				`twitch_user_name`.`user_display_name` AS `display_name`,
				`twitch_user_name`.`user_name` AS `name`,
				RANK() OVER (PARTITION BY `twitch_user`.`channel_id` ORDER BY `twitch_user`.`amount_time` DESC) AS `rank`
			FROM `twitch_user`
			LEFT JOIN `twitch_user_name`
				ON `twitch_user`.`user_id` = `twitch_user_name`.`user_id`
			GROUP BY `twitch_user`.`channel_id`, `twitch_user`.`user_id`
		)
		SELECT `twitch_user`.* FROM `twitch_user` WHERE 1=1"""

	sql:str = ""
	values:tuple = ()

	# Optional 'search' keywords
	user_id:Optional[str] = search.get("user_id", None)
	if user_id is not None:
		sql += " AND `twitch_user`.`user_id` = %s"
		values += (str(user_id),)

	channel_id:Optional[str] = search.get("channel_id", None)
	if channel_id is not None:
		sql += " AND `twitch_user`.`channel_id` = %s"
		values += (str(channel_id),)

	edited:Optional[int] = search.get("edited", None)
	if edited is not None:
		sql += " AND `twitch_user`.`edited` = %s"
		values += (int(edited),)

	# regular:Optional[int] = search.get("regular", None)
	# if regular is not None:
		# sql += " AND `twitch_user`.`regular` = %s"
		# values += (int(regular),)

	name:Optional[str] = search.get("name", None)
	if name is not None:
		sql += " AND `twitch_user`.`name` = %s"
		values += (str(name),)

	display_name:Optional[str] = search.get("display_name", None)
	if display_name is not None:
		sql += " AND `twitch_user`.`display_name` = %s"
		values += (str(display_name),)

	# Optional 'contains' keywords
	name_contains:Optional[str] = search.get("name_contains", None)
	if name_contains is not None:
		name_contains = f"%{name_contains}%"
		sql += " AND ( 1 = 2"
		sql += " OR `twitch_user`.`name` LIKE %s"
		sql += " OR `twitch_user`.`display_name` LIKE %s"
		sql += " )"
		values += (str(name_contains),) * 2

	# Optional 'between' keywords
	rank_between:Optional[tuple] = search.get("rank_between", None)
	if rank_between is not None:
		from_:Optional[int] = rank_between[0]
		to_:Optional[int] = rank_between[1]

		if (from_ is not None) and (to_ is not None):
			sql += " AND `twitch_user`.`rank` BETWEEN %s AND %s"
			values += (int(from_), int(to_))

		if (from_ is not None) and (to_ is None):
			sql += " AND `twitch_user`.`rank` >= %s"
			values += (int(from_),)

		if (from_ is None) and (to_ is not None):
			sql += " AND `twitch_user`.`rank` <= %s"
			values += (int(to_),)

	amount_time_between:Optional[tuple] = search.get("amount_time_between", None)
	if amount_time_between is not None:
		from_:Optional[int] = amount_time_between[0]
		to_:Optional[int] = amount_time_between[1]

		if (from_ is not None) and (to_ is not None):
			sql += " AND `twitch_user`.`amount_time` BETWEEN %s AND %s"
			values += (int(from_), int(to_))

		if (from_ is not None) and (to_ is None):
			sql += " AND `twitch_user`.`amount_time` >= %s"
			values += (int(from_),)

		if (from_ is None) and (to_ is not None):
			sql += " AND `twitch_user`.`amount_time` <= %s"
			values += (int(to_),)

	amount_currency_between:Optional[tuple] = search.get("amount_currency_between", None)
	if amount_currency_between is not None:
		from_:Optional[int] = amount_currency_between[0]
		to_:Optional[int] = amount_currency_between[1]

		if (from_ is not None) and (to_ is not None):
			sql += " AND `twitch_user`.`amount_currency` BETWEEN %s AND %s"
			values += (int(from_), int(to_))

		if (from_ is not None) and (to_ is None):
			sql += " AND `twitch_user`.`amount_currency` >= %s"
			values += (int(from_),)

		if (from_ is None) and (to_ is not None):
			sql += " AND `twitch_user`.`amount_currency` <= %s"
			values += (int(to_),)

	# Special
	count_mode:bool = search.get("count_mode", False)
	if count_mode:
		search["limit"] = None
		search["offset"] = None
		ground_sql: str = """
			SELECT COUNT(*) AS `I`
			FROM `twitch_user`
			WHERE 1 = 1"""

	overwrite_where:Optional[str] = search.get("overwrite_where", None)
	overwrite_where_values: Union[tuple, dict, None] = search.get("overwrite_where_values", ())
	if overwrite_where:
		sql = overwrite_where
		values = overwrite_where_values

	# Other
	order_str:str = search.get("order_str", "ORDER BY `twitch_user`.`id` ASC")
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
		return [TwitchUserStats(x) for x in res]
