from typing import TYPE_CHECKING, Awaitable
if TYPE_CHECKING:
	from .main_discord import PhaazebotDiscord

import discord
import re
from Utils.Classes.discordserversettings import DiscordServerSettings
from Utils.Classes.discordcommandcontext import DiscordCommandContext
from Utils.Classes.discordcommand import DiscordCommand
from .commandindex import getDiscordCommandFunction
from Utils.regex import Discord as ReDiscord

async def checkCommands(cls:"PhaazebotDiscord", Message:discord.Message, ServerSettings:DiscordServerSettings) -> None:

	CommandContext:DiscordCommandContext = DiscordCommandContext(cls, Message)
	await CommandContext.check()

	if CommandContext.found:
		Command:DiscordCommand = CommandContext.Command
		await Command.increaseUse(cls)

		final_result:dict = await formatCommand(cls, Command, CommandContext)
		await Message.channel.send(**final_result)

async def formatCommand(cls:"PhaazebotDiscord", Command:DiscordCommand, CommandContext:DiscordCommandContext) -> dict:
	"""
		This function is suppost to do everything.
		It takes the placeholder in Command.content and replaces them with the wanted data.
		That also applies to module/function calls in Command.content.

		There are 2 main stages a command can have,
		a 'simple' commands that has one clear return from a function
		and 'complex' commands that may have multiple fields in which single return values from a funcion are inserted
	"""

	# it's a 'simple' function
	# get the associated function and execute it
	# and return content
	if not Command.complex:
		function_str:str = Command.function

		func:Awaitable = getDiscordCommandFunction("simple", function_str)

		return await func(cls, Command, CommandContext)

	else:
		FunctionHits = re.search(ReDiscord.CommandFunctionString, Command.content)
		print(FunctionHits)


		VarHits = re.search(ReDiscord.CommandVariableString, Command.content)
		print(VarHits)

		return { "content": "-", "embed": None }
