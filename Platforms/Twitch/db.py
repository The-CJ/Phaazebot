from typing import TYPE_CHECKING, List
if TYPE_CHECKING:
	from Platforms.Twitch.main_twitch import PhaazebotTwitch

import twitch_irc

from Utils.Classes.twitchchannelsettings import TwitchChannelSettings

# twitch settings
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
