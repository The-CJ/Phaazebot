from typing import TYPE_CHECKING, List
if TYPE_CHECKING:
	from Platforms.Twitch.main_twitch import PhaazebotTwitch

import twitch_irc
import Platforms.Twitch.const as TwitchConst
from Utils.Classes.twitchcommandcontext import TwitchCommandContext
from Utils.Classes.twitchpermission import TwitchPermission

async def clientNameChannel(cls:"PhaazebotTwitch", Message:twitch_irc.Message) -> None:

	Context:TwitchCommandContext = TwitchCommandContext(cls, Message)
	cmd_str = str(Context.part(0)).lower()

	if cmd_str.startswith("!join"):
		return joinUserChannel(cls, Message, Context)

	if cmd_str.startswith("!leave"):
		return leaveUserChannel(cls, Message, Context)
