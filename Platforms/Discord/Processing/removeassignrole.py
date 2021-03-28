from typing import TYPE_CHECKING, Coroutine
if TYPE_CHECKING:
	from Platforms.Discord.main_discord import PhaazebotDiscord

import asyncio
from Utils.Classes.discordcommand import DiscordCommand
from Utils.Classes.discordcommandcontext import DiscordCommandContext
from Utils.Classes.discordassignrole import DiscordAssignRole
from Platforms.Discord.db import getDiscordServerAssignRoles
from Platforms.Discord.logging import loggingOnAssignroleDelete

async def removeAssignRole(cls:"PhaazebotDiscord", Command:DiscordCommand, CommandContext:DiscordCommandContext) -> dict:

	specific_trigger:str = CommandContext.part(1)
	if not specific_trigger:
		return {"content": ":warning: You need to define the role-trigger to remove."}

	roles:list = await getDiscordServerAssignRoles(cls, guild_id=Command.server_id, trigger=specific_trigger)

	if not roles:
		return {"content": f":warning: There is no assign role with trigger `{specific_trigger}`"}

	Role:DiscordAssignRole = roles[0]

	cls.BASE.PhaazeDB.deleteQuery("""
		DELETE FROM `discord_assignrole`
		WHERE `discord_assignrole`.`guild_id` = %s
		AND `discord_assignrole`.`trigger` = %s""",
		(str(Role.guild_id), str(Role.trigger))
	)

	# Log
	log_coro:Coroutine = loggingOnAssignroleDelete(cls, CommandContext.ServerSettings, Deleter=CommandContext.Message.author, assign_role_trigger=Role.trigger)
	asyncio.ensure_future(log_coro, loop=cls.BASE.DiscordLoop)

	return {"content": f":white_check_mark: Assign role `{Role.trigger}` removed"}
