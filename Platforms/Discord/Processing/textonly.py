from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Discord.main_discord import PhaazebotDiscord

from Utils.Classes.discordcommand import DiscordCommand
from Utils.Classes.discordcommandcontext import DiscordCommandContext
from Platforms.Discord.formater import responseFormater

async def textOnly(cls:"PhaazebotDiscord", Command:DiscordCommand, CommandContext:DiscordCommandContext) -> dict:

	replaceables:dict = {
		"user-name": CommandContext.Message.author.name,
		"user-mention": CommandContext.Message.author.mention,
		"channel-name": CommandContext.Message.channel.name,
		"channel-mention": CommandContext.Message.channel.mention,
		"server-name": CommandContext.Message.guild.name,
		"member-count": str(CommandContext.Message.guild.member_count),
		"uses": str(Command.uses),
		"cost": str(Command.required_currency)
	}

	additional_kwargs:dict = dict(
		DiscordGuild = CommandContext.Message.guild,
		CommandContext = CommandContext,

		var_dict = replaceables,
		enable_positions = True,
		enable_special = True
	)

	formated_content:str = await responseFormater(cls, Command.content, **additional_kwargs)

	return {"content": formated_content}
