from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Discord.main_discord import PhaazebotDiscord

from Utils.Classes.discordcommand import DiscordCommand
from Utils.Classes.discordcommandcontext import DiscordCommandContext
from Platforms.Discord.utils import getDiscordServerCommands

MAX_SHOW_COMMANDS:int = 20

async def listCommands(cls:"PhaazebotDiscord", Command:DiscordCommand, CommandContext:DiscordCommandContext) -> dict:

	command_link:str = f"https://phaaze.net/discord/commands/{Command.server_id}"
	all_commands:list = await getDiscordServerCommands(cls, Command.server_id)

	finished_str:str = ":link: All commands on this server in one place\n"\
	f"{command_link}\n"\
	f"There are {str(len(all_commands))} Command(s) on this server\n"

	finished_str += "\n".join( [f"`{C.trigger.replace('`', '')}`" for C in all_commands[:MAX_SHOW_COMMANDS]] )

	if len(all_commands) > 20:
		finished_str += "\n and some more"

	return {"content": finished_str}
