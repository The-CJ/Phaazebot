from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Discord.main_discord import PhaazebotDiscord

import discord
from tabulate import tabulate
from Utils.Classes.discordcommand import DiscordCommand
from Utils.Classes.discordcommandcontext import DiscordCommandContext
from Platforms.Discord.utils import getDiscordServerAssignRoles

async def listAssignRole(cls:"PhaazebotDiscord", Command:DiscordCommand, CommandContext:DiscordCommandContext) -> dict:

	all_roles:list = await getDiscordServerAssignRoles(cls, Command.server_id)

	if not all_roles:
		return {"content": ":warning: This server does not have any assigned roles."}

	format_role_list:list = [ ["Trigger", "Role"], ["---", "---"]]
	for Ro in all_roles:
		DiscordRole:discord.Role = CommandContext.Message.guild.get_role( int(Ro.role_id) )
		if not DiscordRole:
			format_role_list.append([Ro.trigger, "DELETED ROLE"])

		else:
			format_role_list.append([Ro.trigger, DiscordRole.name])

	table:str = tabulate(format_role_list, tablefmt="plain")
	finished_str:str = f":notepad_spiral: All assigned roles on this server\n```{table}```"

	return {"content": finished_str}
