from typing import TYPE_CHECKING, List
if TYPE_CHECKING:
	from Platforms.Twitch.main_twitch import PhaazebotTwitch

import twitch_irc

from Utils.Classes.twitchchannelsettings import TwitchChannelSettings
from Utils.Classes.twitchuserstats import TwitchUserStats

# twitch_settings
async def getTwitchChannelSettings(cls:"PhaazebotTwitch", origin:twitch_irc.Message or str or int, prevent_new:bool=False) -> TwitchChannelSettings:
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
			`twitch_setting`.*
		FROM `twitch_setting`
		WHERE `twitch_setting`.`channel_id` = %s
		GROUP BY `twitch_setting`.`channel_id`""",
		(channel_id,)
	)

	if res:
		return TwitchChannelSettings( infos = res.pop(0) )

	else:
		if prevent_new:
			# return a empty 'dummy'
			return TwitchChannelSettings()
		else:
			return await makeTwitchChannelSettings(cls, channel_id)

async def makeTwitchChannelSettings(cls:"PhaazebotTwitch", channel_id:str) -> TwitchChannelSettings:
	"""
	Makes a new entry in the PhaazeDB for a twitch channel.
	Returns a TwitchChannelSettings()
	"""

	try:
		cls.BASE.PhaazeDB.insertQuery(
			table = "twitch_setting",
			content = dict(channel_id = channel_id)
		)

		cls.BASE.Logger.info(f"(Twitch) New channel settings DB entry: {channel_id=}")
		return TwitchChannelSettings( infos = {"channel_id":channel_id} )
	except:
		cls.BASE.Logger.critical(f"(Twitch) New channel settings failed: {channel_id=}")
		raise RuntimeError("Creating new DB entry failed")

# twitch_user
async def getTwitchChannelUsers(cls:"PhaazebotTwitch", channel_id:str, **search:dict) -> List[TwitchUserStats]:
	"""
	Get channel levels and stats.
	Returns a list of TwitchUserStats().

	Optional keywords:
	------------------
	* user_id `str` : (Default: None)
	* edited `int`: (Default: 0) [0=all, 1=not edited, 2=only edited]
	* name `str`: (Default: None)
	* name_contains `str`: (Default: None) [DB uses LIKE]
	* order_str `str`: (Default: "ORDER BY id")
	* limit `int`: (Default: None)
	* offset `int`: (Default: 0)
	"""
	# unpack
	user_id:str = search.get("user_id", None)
	edited:int = search.get("edited", 0)
	name:str = search.get("name", None)
	name_contains:str = search.get("name_contains", None)
	order_str:str = search.get("order_str", "ORDER BY `id`")
	limit:int = search.get("limit", None)
	offset:int = search.get("offset", 0)

	# process
	sql:str = """
		WITH `twitch_user` AS (
			SELECT
				`twitch_user`.*,
				`twitch_user_name`.`user_display_name` AS `display_name`,
				`twitch_user_name`.`user_name` AS `name`,
				RANK() OVER (ORDER BY `amount_time` DESC) AS `rank`
			FROM `twitch_user`
			LEFT JOIN `twitch_user_name`
				ON `twitch_user`.`user_id` = `twitch_user_name`.`user_id`
			WHERE `twitch_user`.`channel_id` = %s
			GROUP BY `twitch_user`.`channel_id`, `twitch_user`.`user_id`
		)
		SELECT `twitch_user`.* FROM `twitch_user` WHERE 1=1"""

	values:tuple = ( str(channel_id), )

	if user_id:
		sql += " AND `twitch_user`.`user_id` = %s"
		values += ( str(user_id), )

	if name:
		sql += " AND (`twitch_user`.`name` = %s OR `twitch_user`.`display_name` = %s)"
		values += ( str(name), str(name) )

	if name_contains:
		name_contains = f"%{name_contains}%"
		sql += " AND (`twitch_user`.`name` LIKE %s OR `twitch_user`.`display_name` LIKE %s)"
		values += ( str(name_contains), str(name_contains) )

	if edited == 2:
		sql += " AND `twitch_user`.`edited` = 1"
	if edited == 1:
		sql += " AND `twitch_user`.`edited` = 0"

	sql += f" {order_str}"

	if limit:
		sql += f" LIMIT {limit}"
		if offset:
			sql += f" OFFSET {offset}"

	print(sql)
	res:List[dict] = cls.BASE.PhaazeDB.selectQuery(sql, values)

	if res:
		return [TwitchUserStats(x) for x in res]

	else:
		return []

async def getTwitchChannelUserAmount(cls:"PhaazebotTwitch", channel_id:str, where:str="1=1", where_values:tuple=()) -> int:

	sql:str = f"""
		SELECT COUNT(*) AS `I` FROM `twitch_user`
		WHERE `twitch_user`.`channel_id` = %s AND {where}"""

	values:tuple = (channel_id,) + where_values

	res:List[dict] = cls.BASE.PhaazeDB.selectQuery(sql, values)

	return res[0]["I"]
