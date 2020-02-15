from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Discord.main_discord import PhaazebotDiscord

from Utils.Classes.discordcommand import DiscordCommand
from Utils.Classes.discordcommandcontext import DiscordCommandContext
from Platforms.Discord.utils import getDiscordServerCommands

MAX_SHOW_COMMANDS:int = 20

async def listCommands(cls:"PhaazebotDiscord", Command:DiscordCommand, CommandContext:DiscordCommandContext) -> dict:

	command_link:str = f"{cls.BASE.Vars.WEB_ROOT}/discord/commands/{Command.server_id}"
	all_commands:list = await getDiscordServerCommands(cls, Command.server_id)

	finished_str:str = ":link: All commands on this server in one place\n"
	finished_str += f"{command_link}\n"
	finished_str += f"There are {str(len(all_commands))} Command(s) on this server\n"
	finished_str += "```\n"

	Command:DiscordCommand
	for Command in all_commands[:MAX_SHOW_COMMANDS]:
		cmd = Command.trigger.replace("```", '')
		finished_str += f"{cmd}\n"

	finished_str += "```"

	if len(all_commands) > MAX_SHOW_COMMANDS:
		finished_str += "\n and some more"

	return {"content": finished_str}
