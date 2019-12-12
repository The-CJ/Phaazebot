from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Discord.main_discord import PhaazebotDiscord

import discord
from Utils.Classes.discordcommand import DiscordCommand
from Utils.Classes.discordcommandcontext import DiscordCommandContext
from Platforms.Discord.utils import getDiscordRoleFromString

async def addAssignRole(cls:"PhaazebotDiscord", Command:DiscordCommand, CommandContext:DiscordCommandContext) -> dict:

	Perm:discord.Permissions = CommandContext.Message.channel.permissions_for(CommandContext.Message.guild.me)
	if not Perm.manage_roles:
		return {"content": ":no_entry_sign: Phaaze don't has a role with the `Manage Roles` permission."}

	trigger:str = CommandContext.part(1)
	query_str:str = " ".join( CommandContext.parts[2:] )

	res:list = cls.BASE.PhaazeDB.query("""
		SELECT COUNT(*) AS `I`
		FROM `discord_assignrole`
		WHERE `discord_assignrole`.`guild_id` = %s""",
		(Command.server_id,)
	)

	if res[0]["I"] >= cls.BASE.Limit.DISCORD_ADDROLE_AMOUNT:
		return {"content": ":no_entry_sign: This server hit the assign role limit, please remove some first."}

	if not trigger or not query_str:
		return {"content": ":warning: You need to define a role-trigger and a role."}

	AssignRole:discord.Role = getDiscordRoleFromString(cls, CommandContext.Message.guild, query_str, Message=CommandContext.Message)

	if not AssignRole:
		return {"content": f":warning: Could not find any role matching: `{query_str}`"}

	if CommandContext.Message.guild.me.top_role < AssignRole:
		return {"content": f":no_entry_sign: The Role `{AssignRole.name}` is to high. Phaaze highest role has to be higher in hierarchy then `{AssignRole.name}`"}

	cls.BASE.PhaazeDB.insertQuery(
		table = "discord_assignrole",
		content = dict(
			guild_id = Command.server_id,
			role_id = AssignRole.id,
			trigger = trigger
		)
	)

	return {"content": f":white_check_mark: Successfull added assign role `{str(AssignRole)}` with trigger `{trigger}`"}
