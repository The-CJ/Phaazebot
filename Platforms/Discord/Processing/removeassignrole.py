from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Discord.main_discord import PhaazebotDiscord

from Utils.Classes.discordassignrole import DiscordAssignRole
from Utils.Classes.discordcommand import DiscordCommand
from Utils.Classes.discordcommandcontext import DiscordCommandContext
from Platforms.Discord.utils import getDiscordServerAssignRoles

async def removeAssignRole(cls:"PhaazebotDiscord", Command:DiscordCommand, CommandContext:DiscordCommandContext) -> dict:

	specific_trigger:str = CommandContext.part(1)
	if not specific_trigger:
		return {"content": ":warning: You need to define the role-trigger to remove."}

	roles:list = await getDiscordServerAssignRoles(cls, Command.server_id, trigger=specific_trigger)

	if not roles:
		return {"content": f":warning: There is no assign role with trigger `{specific_trigger}`"}

	Role:DiscordAssignRole = roles[0]

	cls.BASE.PhaazeDB.deleteQuery("""
		DELETE FROM `discord_assignrole`
		WHERE `discord_assignrole`.`guild_id` = %s
		AND `discord_assignrole`.`trigger` = %s""",
		( str(Role.guild_id), str(Role.trigger) )
	)

	return {"content": f":white_check_mark: Assign role `{Role.trigger}` removed"}
