from typing import TYPE_CHECKING, Awaitable
if TYPE_CHECKING:
	from .main_discord import PhaazebotDiscord

import discord
import asyncio
import re
from Utils.Classes.discordserversettings import DiscordServerSettings
from Utils.Classes.discordcommandcontext import DiscordCommandContext
from Utils.Classes.discordcommand import DiscordCommand
from Utils.Classes.discordpermission import DiscordPermission
from .commandindex import getDiscordCommandFunction
from Utils.regex import Discord as ReDiscord

class GDCCS():
	"""
		i present the GDCCS, short for "Global Discord Command Cooldown Storage"
		after a command whas been used, it's unique key is saved in where
		while its in there, its in a cool down state, and wont be triggered again
		after cooldown is gone, remove unique key from here and unlock command
	"""
	def __init__(self):
		self.in_cooldown:dict = dict()

	def check(self, Command:DiscordCommand) -> bool:
		key:str = f"{Command.server_id}-{Command.trigger}"
		if self.in_cooldown.get(key, None): return True
		else: return False

	def cooldown(self, Command:DiscordCommand) -> None:
		asyncio.ensure_future(self.cooldownCoro(Command))

	async def cooldownCoro(self, Command:DiscordCommand) -> None:
		key:str = f"{Command.server_id}-{Command.trigger}"
		if self.in_cooldown.get(key, None): return

		# add
		self.in_cooldown[key] = True

		# wait
		await asyncio.sleep(Command.cooldown)

		# remove
		self.in_cooldown.pop(key, None)

GDCCS = GDCCS()

async def checkCommands(cls:"PhaazebotDiscord", Message:discord.Message, ServerSettings:DiscordServerSettings) -> bool:

	CommandContext:DiscordCommandContext = DiscordCommandContext(cls, Message, Settings=ServerSettings)

	# get permission object
	AuthorPermission:DiscordPermission = DiscordPermission(Message)

	# direct call via @Phaazebot [command] (rest vars)
	# server owner only (for now)
	if AuthorPermission.rank >= 3 and Message.guild.me.mention == CommandContext.part(0):
		CommandContext.parts.pop(0)

		command_data:dict = dict(
			command_id = 0,
			function = CommandContext.parts[0],
			require = 3,
			cooldown = 5,
			content = ""
		)

		Command:DiscordCommand = DiscordCommand(command_data, Message.guild.id)
		result:dict = await formatCommand(cls, Command, CommandContext, direct_call=True)
		if result: await Message.channel.send(**result)
		return True

	# a normal call, so we check first
	await CommandContext.check()

	if CommandContext.found:

		Command:DiscordCommand = CommandContext.Command

		# check if command is in cooldown
		if GDCCS.check(Command): return False

		# check caller access level and command require level
		if not AuthorPermission.rank >= Command.require: return False

		# owner disables normal commands serverwide,
		if ServerSettings.owner_disable_normal and Command.require == 0:
			# noone except the owner can use them
			if AuthorPermission.rank != 3: return False

		# owner disables regular commands serverwide,
		if ServerSettings.owner_disable_regular and Command.require == 1:
			# noone except the owner can use them
			if AuthorPermission.rank != 3: return False

		# owner disables mod commands serverwide,
		if ServerSettings.owner_disable_mod and Command.require == 2:
			# noone except the owner can use them
			if AuthorPermission.rank != 3: return False

		# always have a minimum cooldown
		if Command.cooldown < cls.BASE.Limit.DISCORD_COMMANDS_COOLDOWN:
			Command.cooldown = cls.BASE.Limit.DISCORD_COMMANDS_COOLDOWN

		# add command to cooldown
		GDCCS.cooldown(Command)

		# increase use
		await Command.increaseUse(cls)

		# throw it to formatCommand and send the return values
		final_result:dict = await formatCommand(cls, Command, CommandContext)

		# there a commands that not have a direct return value,
		# but are still valid and successfull
		if final_result:
			await Message.channel.send(**final_result)

		return True

	else:
		return False

async def formatCommand(cls:"PhaazebotDiscord", Command:DiscordCommand, CommandContext:DiscordCommandContext, direct_call:bool=False) -> dict:
	"""
		This function is suppost to do everything.
		It takes the placeholder in Command.content and replaces them with the wanted data.
		That also applies to module/function calls in Command.content.

		There are 2 main stages a command can have,
		a 'simple' commands that has one clear return from a function
		and 'complex' commands that may have multiple fields in which single return values from a function are inserted
	"""

	# it's a 'simple' function
	# get the associated function and execute it
	# and return content
	if not Command.complex:
		function_str:str = Command.function

		func:Awaitable = getDiscordCommandFunction(function_str)

		# this happens if a user enters @phaazebot and then some garbage
		if direct_call and func.__name__ == "textOnly": return {}

		cls.BASE.Logger.debug(f"(Discord) execute command '{func.__name__}'", require="discord:commands")

		return await func(cls, Command, CommandContext)

	else:
		# TODO: to complex functions
		FunctionHits = re.search(ReDiscord.CommandFunctionString, Command.content)
		print(FunctionHits)
		VarHits = re.search(ReDiscord.CommandVariableString, Command.content)
		print(VarHits)

		return { "content": "Complex functions are under construction", "embed": None }
