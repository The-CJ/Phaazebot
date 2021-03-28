from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Twitch.main_twitch import PhaazebotTwitch

from Utils.Classes.twitchcommand import TwitchCommand
from Utils.Classes.twitchcommandcontext import TwitchCommandContext
from Platforms.Twitch.formatter import responseFormatter

async def textOnly(cls:"PhaazebotTwitch", Command:TwitchCommand, CommandContext:TwitchCommandContext) -> dict:

	replaceable:dict = {
		"user-name": CommandContext.Message.user_name,
		"user-display-name": CommandContext.Message.display_name,
		"channel-name": CommandContext.Message.room_id,
		"uses": str(Command.uses),
		"cost": str(Command.required_currency),
	}

	additional_kwargs:dict = dict(
		CommandContext=CommandContext,

		var_dict=replaceable,
		enable_positions=True,
	)

	if not Command.content:
		# should never happen?
		return {}

	formatted_content:str = await responseFormatter(cls, Command.content, **additional_kwargs)

	return {"content": formatted_content}
