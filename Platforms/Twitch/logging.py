from typing import TYPE_CHECKING, Dict, Union
if TYPE_CHECKING:
	from Platforms.Twitch.main_twitch import PhaazebotTwitch

from Utils.Classes.twitchchannelsettings import TwitchChannelSettings

# there is only a small amount, because most things are handled by discord audit logs
TRACK_OPTIONS:Dict[str, int] = {
	"Config.edit": 1,
	"Quote.create": 1 << 1,
	"Quote.edit": 1 << 2,
	"Quote.delete": 1 << 3,
	"Regular.create": 1 << 4,
	"Regular.delete": 1 << 5,
	"Level.edit": 1 << 6,
	"Moderation.timeout": 1 << 7,
	"Moderation.ban": 1 << 8,
}
EVENT_COLOR_POSITIVE:int = 0x00FF00
EVENT_COLOR_WARNING:int = 0xFFAA00
EVENT_COLOR_NEGATIVE:int = 0xFF0000
EVENT_COLOR_INFO:int = 0x00FFFF

def makeWebAccessLink(cls:"PhaazebotTwitch", channel_id:Union[str, int], log_id:Union[str, int]) -> str:
	return f"{cls.BASE.Vars.web_root}/twitch/dashboard/{str(channel_id)}?view=logs&logs[log_id]={str(log_id)}"

# Config.edit : 1 : 1
async def loggingOnConfigEdit(_cls:"PhaazebotTwitch", _Settings:TwitchChannelSettings, **kwargs) -> None:
	"""
	Logs the event when someone makes any changes to configs via web.

	Required keywords:
	------------------
	* `changes` - dict
	"""
	_logging_signature:str = "Config.edit"
	_changes:dict = kwargs["changes"]

# Moderation.timeout : 128 : 10000000
async def loggingOnModerationTimeout(cls:"PhaazebotTwitch", Settings:TwitchChannelSettings, **kwargs) -> None:
	"""
	Logs the event when phaaze timeouts a user in chat.

	Required keywords:
	------------------
	* `user_name` - str
	* `user_id` - str
	* `reason` - str
	* `timeout` - int
	* `level` - int
	"""
	logging_signature:str = "Moderation.timeout"
	user_name:str = kwargs["user_name"]
	user_id:str = kwargs["user_id"]
	reason:str = kwargs["reason"]
	timeout:int = kwargs["timeout"]
	level:int = kwargs["level"]

	if level == 1: warn_level:str = "2nd warning"
	elif level == 2: warn_level:str = "Last warning"
	else: warn_level:str = "Warning"

	cls.BASE.PhaazeDB.insertQuery(
		table="twitch_log",
		content={
			"channel_id": Settings.channel_id,
			"event_value": TRACK_OPTIONS[logging_signature],
			"initiator_id": user_id,
			"initiator_name": user_name,
			"content": f"{user_name} got a '{warn_level}' and a {timeout}s timeout, triggered reason: {reason}"
		}
	)

# Moderation.ban : 256 : 100000000
async def loggingOnModerationBan(_cls:"PhaazebotTwitch", _Settings:TwitchChannelSettings, **kwargs) -> None:
	"""
	Logs the event when phaaze bans a user in chat.

	Required keywords:
	------------------
	* user_name `str`
	* user_id `str`
	* reason `str`
	"""
	_logging_signature:str = "Moderation.ban"
	_user_name:str = kwargs["user_name"]
	_user_id:str = kwargs["user_id"]
	_reason:str = kwargs["reason"]
