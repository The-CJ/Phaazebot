from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Discord.main_discord import PhaazebotDiscord

import discord
from Utils.Classes.discordcommand import DiscordCommand
from Utils.Classes.discordcommandcontext import DiscordCommandContext
from Platforms.Discord.utils import getDiscordServerAssignRoles

async def assignRole(cls:"PhaazebotDiscord", Command:DiscordCommand, CommandContext:DiscordCommandContext) -> dict:

	Perm:discord.Permissions = CommandContext.Message.channel.permissions_for(CommandContext.Message.guild.me)
	if not Perm.manage_roles:
		return {"content": ":no_entry_sign: Phaaze don't has a role with the `Manage Roles` permission."}

	role_trigger:str = CommandContext.part(1)

	if not role_trigger:
		return {"content": ":warning: Missing a role-trigger"}

	roles:list = await getDiscordServerAssignRoles(cls, Command.server_id, trigger=role_trigger)

	if not roles:
		return {"content": f":warning: Could not find any assign role associated with: `{role_trigger}`"}

	WantedDiscordRole:discord.Role = CommandContext.Message.guild.get_role(int( roles.pop(0).role_id ))

	if CommandContext.Message.guild.me.top_role < WantedDiscordRole:
		return {"content": f":no_entry_sign: The Role `{WantedDiscordRole.name}` is to high. Phaaze highest role has to be higher in hierarchy then `{WantedDiscordRole.name}`"}

	if WantedDiscordRole in CommandContext.Message.author.roles:
		await CommandContext.Message.author.remove_roles(WantedDiscordRole, reason=f"Removed via assignrole, trigger='{role_trigger}'")
		return {"content": f":white_check_mark: Successfull removed the role `{WantedDiscordRole.name}` from you."}

	else:
		await CommandContext.Message.author.add_roles(WantedDiscordRole, reason=f"Added via assignrole, trigger='{role_trigger}'")
		return {"content": f":white_check_mark: Successfull added you the role: `{WantedDiscordRole.name}`"}
