from typing import TYPE_CHECKING, Dict
if TYPE_CHECKING:
	from .main_twitch import PhaazebotTwitch

import twitch_irc
import traceback
import datetime
from Utils.Classes.twitchchannelsettings import TwitchChannelSettings

# there is only a small amount, because most things are handled by discord audit logs
TRACK_OPTIONS:Dict[str, int] = {
	"Config.edit": 1,
	"Quote.create": 1<<1,
	"Quote.edit": 1<<2,
	"Quote.delete": 1<<3,
	"Regular.create": 1<<4,
	"Regular.delete": 1<<5,
	"Level.edit": 1<<6,
}
EVENT_COLOR_POSITIVE:int = 0x00FF00
EVENT_COLOR_WARNING:int = 0xFFAA00
EVENT_COLOR_NEGATIVE:int = 0xFF0000
EVENT_COLOR_INFO:int = 0x00FFFF

def makeWebAccessLink(cls:"PhaazebotTwitch", channel_id:str or int, log_id:str or int) -> str:
	return f"{cls.BASE.Vars.web_root}/twitch/dashboard/{str(channel_id)}?view=logs&logs[log_id]={str(log_id)}"

# Config.edit : 1 : 1
async def loggingOnConfigEdit(cls:"PhaazebotTwitch", Settings:TwitchChannelSettings, **kwargs:dict) -> None:
	"""
	Logs the event when someone makes any changes to configs via web.
	If track option `Config.edit` is active, it will send a message to discord

	Required keywords:
	------------------
	* changes `dict`
	"""
	logging_signature:str = "Config.edit"
	changes:dict = kwargs["changes"]
