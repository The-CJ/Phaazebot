from typing import TYPE_CHECKING, Callable, Dict
if TYPE_CHECKING:
	from Platforms.Discord.main_discord import PhaazebotDiscord

import discord
import asyncio
import re
# noinspection PyPep8Naming
import Platforms.Discord.const as DiscordConst
from Platforms.Discord.commandindex import getDiscordCommandFunction
from Utils.Classes.discordserversettings import DiscordServerSettings
from Utils.Classes.discorduserstats import DiscordUserStats
from Utils.Classes.discordcommandcontext import DiscordCommandContext
from Utils.Classes.discordcommand import DiscordCommand
from Utils.Classes.discordpermission import DiscordPermission
from Utils.regex import Discord as ReDiscord

class GlobalDiscordCommandCooldownStorage(object):
	"""
	i present the GDCCS, short for "Global Discord Command Cooldown Storage"
	after a command has been used, it's unique key is saved in here
	while its in there, its in a cool down state, and won't be triggered again
	after cooldown is gone, remove unique key from here and unlock command
	"""
	def __init__(self):
		self.in_cooldown:Dict[str, bool] = dict()

	def check(self, Command:DiscordCommand) -> bool:
		key:str = str(Command.command_id)
		if self.in_cooldown.get(key, False): return True
		else: return False

	def cooldown(self, Command:DiscordCommand) -> None:
		asyncio.ensure_future(self.cooldownCoro(Command))

	async def cooldownCoro(self, Command:DiscordCommand) -> None:
		key:str = str(Command.command_id)
		if self.in_cooldown.get(key, None): return

		# add
		self.in_cooldown[key] = True

		# wait
		await asyncio.sleep(Command.cooldown)

		# remove
		self.in_cooldown.pop(key, None)


GDCCS:GlobalDiscordCommandCooldownStorage = GlobalDiscordCommandCooldownStorage()

async def checkCommands(cls:"PhaazebotDiscord", Message:discord.Message, ServerSettings:DiscordServerSettings, DiscordUser:DiscordUserStats) -> bool:
	"""
	This function is run on every message and checks if there is a command to execute
	Returns True if a function is executed, else False
	(That's needed for level stats, because commands don't give exp)
	"""

	CommandContext:DiscordCommandContext = DiscordCommandContext(cls, Message, Settings=ServerSettings)

	# get permission object
	AuthorPermission:DiscordPermission = DiscordPermission(Message, DiscordUser)

	# random fact, even part 0 can be none, if a image is updated
	clean_nickname:str = (CommandContext.part(0) or '').replace('!', '')

	# direct call via @Phaazebot [command] (rest vars)
	# server owner only (for now)
	if AuthorPermission.rank >= DiscordConst.REQUIRE_OWNER and str(Message.guild.me.mention) == clean_nickname:

		CommandContext.parts.pop(0)
		CommandContext.Message.mentions.pop(0)

		command_data:dict = dict(
			command_id=0,
			guild_id=Message.guild.id,
			function=CommandContext.parts[0],
			require=3,
			cooldown=5,
			content=""
		)

		Command:DiscordCommand = DiscordCommand(command_data)
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
		if ServerSettings.owner_disable_normal and Command.require == DiscordConst.REQUIRE_EVERYONE:
			# no one except the owner can use them
			if AuthorPermission.rank != DiscordConst.REQUIRE_OWNER: return False

		# owner disables regular commands serverwide,
		if ServerSettings.owner_disable_regular and Command.require == DiscordConst.REQUIRE_REGULAR:
			# no one except the owner can use them
			if AuthorPermission.rank != DiscordConst.REQUIRE_OWNER: return False

		# owner disables mod commands serverwide,
		if ServerSettings.owner_disable_mod and Command.require == DiscordConst.REQUIRE_MOD:
			# no one except the owner can use them
			if AuthorPermission.rank != DiscordConst.REQUIRE_OWNER: return False

		# always have a minimum cooldown
		Command.cooldown = max(Command.cooldown, cls.BASE.Limit.discord_commands_cooldown_min, DiscordConst.COMMAND_COOLDOWN_MIN)

		# but also not be to long
		Command.cooldown = min(Command.cooldown, cls.BASE.Limit.discord_commands_cooldown_max, DiscordConst.COMMAND_COOLDOWN_MAX)

		# command requires a currency payment, check if user can afford it
		# except mods
		if Command.required_currency != 0 and AuthorPermission.rank < DiscordConst.REQUIRE_MOD:

			# not enough
			if not (DiscordUser.currency >= Command.required_currency):
				cls.BASE.Logger.debug(f"(Discord) Skipping command call because of insufficient currency: ({DiscordUser.currency} < {Command.required_currency})", require="discord:commands")
				return False

			await DiscordUser.editCurrency(cls, amount_by=-Command.required_currency)

		# add command to cooldown
		GDCCS.cooldown(Command)

		# increase use
		await Command.increaseUse(cls)

		# throw it to formatCommand and send the return values
		final_result:dict = await formatCommand(cls, Command, CommandContext)

		# there a commands that not have a direct return value,
		# but are still valid and successful
		if final_result:
			await Message.channel.send(**final_result)

		return True

	else:
		return False

async def formatCommand(cls:"PhaazebotDiscord", Command:DiscordCommand, CommandContext:DiscordCommandContext, direct_call:bool=False) -> dict:
	"""
	This function is suppose to do everything.
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

		# get function from functions index
		func:Callable = getDiscordCommandFunction(function_str)

		# this happens if a user enters @phaazebot and then some garbage
		if direct_call and func.__name__ == "textOnly":
			cls.BASE.Logger.debug(f"(Discord) direct call failed, user entered: '{function_str}'", require="discord:commands")
			return {}

		cls.BASE.Logger.debug(f"(Discord) execute command '{func.__name__}'", require="discord:commands")

		return await func(cls, Command, CommandContext)

	else:
		# TODO: complex functions
		FunctionHits = re.search(ReDiscord.CommandObjectVariableString, Command.content)
		print(FunctionHits)
		VarHits = re.search(ReDiscord.CommandVariableString, Command.content)
		print(VarHits)

		return {"content": "Complex functions are under construction", "embed": None}
