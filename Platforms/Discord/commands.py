from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from .main_discord import PhaazebotDiscord

import discord
from Utils.Classes.discordserversettings import DiscordServerSettings
from Utils.Classes.discordcommandcontext import DiscordCommandContext
from Utils.Classes.discordcommand import DiscordCommand



async def checkCommands(cls:"PhaazebotDiscord", Message:discord.Message, ServerSettings:DiscordServerSettings) -> None:

	CommandContext:DiscordCommandContext = DiscordCommandContext(cls, Message)
	await CommandContext.check()

	if CommandContext.found:
		Command:DiscordCommand = CommandContext.Command

		final_result:dict = await formatCommand(cls, Command, CommandContext)
		await Message.channel.send(**final_result)

async def formatCommand(cls:"PhaazebotDiscord", Command:DiscordCommand, CommandContext:DiscordCommandContext) -> dict:
	"""
		This function is suppost to do everything.
		It takes the placeholder in Command.content and replaces them with the wanted data.
		That also applies to module/function calls in Command.content.

		Let's say we have 3 stages of a command:
		1. Insert returns of Function calls
		2. Insert Variables
		3. Remove any unfound or failed stuff
	"""

	pass # TODO: x











	return { "content": "-", "embed": None }
