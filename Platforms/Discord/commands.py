from typing import TYPE_CHECKING, Awaitable
if TYPE_CHECKING:
	from .main_discord import PhaazebotDiscord

import discord
import asyncio
import re
from Utils.Classes.discordserversettings import DiscordServerSettings
from Utils.Classes.discorduserstats import DiscordUserStats
from Utils.Classes.discordcommandcontext import DiscordCommandContext
from Utils.Classes.discordcommand import DiscordCommand
from Utils.Classes.discordpermission import DiscordPermission
from Utils.regex import Discord as ReDiscord
from .utils import getDiscordServerUsers
from .commandindex import getDiscordCommandFunction

class GDCCS():
	"""
		i present the GDCCS, short for "Global Discord Command Cooldown Storage"
		after a command has been used, it's unique key is saved in where
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
	"""
		This function is run on every message and checks if there is a command to execute
		Returns True if a function is executed, else False
		(Thats needed for level stats, because commands dont give exp)
	"""

	CommandContext:DiscordCommandContext = DiscordCommandContext(cls, Message, Settings=ServerSettings)

	# get permission object
	AuthorPermission:DiscordPermission = DiscordPermission(Message)

	# random fact, even part 0 can be none, if a image is updated
	clean_nickname:str = (CommandContext.part(0) or '').replace('!', '')

	# direct call via @Phaazebot [command] (rest vars)
	# server owner only (for now)
	if AuthorPermission.rank >= 3 and str(Message.guild.me.mention) == clean_nickname:

		CommandContext.parts.pop(0)
		CommandContext.Message.mentions.pop(0)

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

		if not Command.active: return False

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
		if Command.cooldown < cls.BASE.Limit.DISCORD_COMMANDS_COOLDOWN_MIN:
			cls.BASE.Logger.debug(f"(Discord) command cooldown < DISCORD_COMMANDS_COOLDOWN_MIN cooldown={Command.cooldown}, id={Command.command_id}", require="discord:commands")
			Command.cooldown = cls.BASE.Limit.DISCORD_COMMANDS_COOLDOWN_MIN

		if Command.cooldown > cls.BASE.Limit.DISCORD_COMMANDS_COOLDOWN_MAX:
			cls.BASE.Logger.debug(f"(Discord) command cooldown > DISCORD_COMMANDS_COOLDOWN_MAX cooldown={Command.cooldown}, id={Command.command_id}", require="discord:commands")
			Command.cooldown = cls.BASE.Limit.DISCORD_COMMANDS_COOLDOWN_MAX

		# command requires a currency payment, check if user can affort it
		# except mods
		if Command.required_currency != 0 and AuthorPermission.rank < 2:
			res:list = await getDiscordServerUsers(cls, Message.guild.id, Message.author.id)
			if not res: return False
			DiscordUser:DiscordUserStats = res.pop(0)

			# not enough
			if not (DiscordUser.currency >= Command.required_currency):
				cls.BASE.Logger.debug(f"(Discord) Skipping command call because of insufficient currency: ({DiscordUser.currency} < {Command.required_currency})", require="discord:commands")
				return False

			await DiscordUser.editCurrency(cls, -Command.required_currency )

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

		# get function from fucntions index
		func:Awaitable = getDiscordCommandFunction(function_str)

		# this happens if a user enters @phaazebot and then some garbage
		if direct_call and func.__name__ == "textOnly":
			cls.BASE.Logger.debug(f"(Discord) direct call failed, user entered: '{function_str}'", require="discord:commands")
			return {}

		cls.BASE.Logger.debug(f"(Discord) execute command '{func.__name__}'", require="discord:commands")

		return await func(cls, Command, CommandContext)

	else:
		# TODO: to complex functions
		FunctionHits = re.search(ReDiscord.CommandFunctionString, Command.content)
		print(FunctionHits)
		VarHits = re.search(ReDiscord.CommandVariableString, Command.content)
		print(VarHits)

		return { "content": "Complex functions are under construction", "embed": None }
