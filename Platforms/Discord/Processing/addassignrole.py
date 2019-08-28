from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Discord.main_discord import PhaazebotDiscord

import discord
from Utils.Classes.discordcommand import DiscordCommand
from Utils.Classes.discordcommandcontext import DiscordCommandContext
from Platforms.Discord.utils import getDiscordRoleFromString

async def addAssignRole(cls:"PhaazebotDiscord", Command:DiscordCommand, CommandContext:DiscordCommandContext) -> dict:

	trigger:str = CommandContext.part(1)
	query_str:str = " ".join( CommandContext.parts[2:] )

	if not trigger or not query_str:
		return {"content": ":warning: You need to define a role-trigger and a role."}

	AssignRole:discord.Role = getDiscordRoleFromString(cls, CommandContext.Message.guild, query_str, Message=CommandContext.Message)

	if not AssignRole:
		return {"content": f":warning: Could not find any role matching: `{query_str}`"}

	cls.BASE.PhaazeDB.query("""
		INSERT INTO discord_giverole
		(`guild_id`, `role_id`, `trigger`)
		VALUES (%s, %s, %s)""",
		(Command.server_id, AssignRole.id, trigger)
	)

	return {"content": f":white_check_mark: Successfull added assign role `{str(AssignRole)}` with trigger `{trigger}`"}
