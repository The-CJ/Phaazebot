from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Twitch.main_twitch import PhaazebotTwitch

from Utils.Classes.twitchcommand import TwitchCommand
from Utils.Classes.twitchcommandcontext import TwitchCommandContext
from Platforms.Twitch.formater import responseFormater

async def textOnly(cls:"PhaazebotTwitch", Command:TwitchCommand, CommandContext:TwitchCommandContext) -> dict:

	replaceables:dict = {
		"user-name": CommandContext.Message.user_name,
		"user-display-name": CommandContext.Message.display_name,
		"channel-name": CommandContext.Message.room_id,
		"uses": str(Command.uses),
		"cost": str(Command.required_currency),
	}

	additional_kwargs:dict = dict(
		CommandContext = CommandContext,

		var_dict = replaceables,
		enable_positions = True,
	)

	if not Command.content:
		# should never happen?
		return {}

	formated_content:str = await responseFormater(cls, Command.content, **additional_kwargs)

	return {"content": formated_content}
