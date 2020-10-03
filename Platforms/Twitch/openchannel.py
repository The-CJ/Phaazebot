from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Twitch.main_twitch import PhaazebotTwitch

import twitch_irc

async def openChannel(cls:"PhaazebotTwitch", Message:twitch_irc.Message) -> None:

	pass
