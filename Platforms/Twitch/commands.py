from typing import TYPE_CHECKING, Awaitable, Dict
if TYPE_CHECKING:
	from Platforms.Twitch.main_twitch import PhaazebotTwitch

import twitch_irc
import asyncio
import Platforms.Twitch.const as TwitchConst
from Utils.Classes.twitchcommand import TwitchCommand
from Utils.Classes.twitchchannelsettings import TwitchChannelSettings
from Utils.Classes.twitchuserstats import TwitchUserStats
from Utils.Classes.twitchpermission import TwitchPermission
from Utils.Classes.twitchcommandcontext import TwitchCommandContext
from Platforms.Twitch.commandindex import getTwitchCommandFunction

class GTCCS():
	"""
	you know the point up now, "Global Twitch Command Cooldown Storage" it is
	after command is used, ID is saved in here.
	While its in there, its in a cool down state, and wont be triggered again
	after cooldown is gone, remove ID from here and unlock command
	"""
	def __init__(self):
		self.in_cooldown:Dict[str, bool] = {}

	def check(self, Command:TwitchCommand) -> bool:
		cmd_id:str = str(Command.command_id)
		if self.in_cooldown.get(cmd_id, None): return True
		else: return False

	def cooldown(self, Command:TwitchCommand) -> None:
		asyncio.ensure_future(self.cooldownCoro(Command))

	async def cooldownCoro(self, Command:TwitchCommand) -> None:
		cmd_id:str = str(Command.command_id)
		if self.in_cooldown.get(cmd_id, None): return

		# add
		self.in_cooldown[cmd_id] = True

		# wait
		await asyncio.sleep(Command.cooldown)

		# remove
		self.in_cooldown.pop(cmd_id, None)

GTCCS = GTCCS()

async def checkCommands(cls:"PhaazebotTwitch", Message:twitch_irc.Message, ChannelSettings:TwitchChannelSettings, TwitchUser:TwitchUserStats) -> bool:
	"""
	This function is run on every message and checks if there is a command to execute
	Returns True if a function is executed, else False
	(Thats needed for level stats, because commands dont give exp)
	"""

	CommandContext:TwitchCommandContext = TwitchCommandContext(cls, Message, Settings=ChannelSettings)

	# get permission object
	AuthorPermission:TwitchPermission = TwitchPermission(Message, TwitchUser)

	# a normal call, so we check first
	await CommandContext.check()

	if CommandContext.found:

		Command:TwitchCommand = CommandContext.Command

		if not Command.active: return False

		# check if command is in cooldown
		if GTCCS.check(Command): return False

		# check caller access level and command require level
		if not AuthorPermission.rank >= Command.require: return False

		# owner disables normal commands in the channel
		if ChannelSettings.owner_disable_normal and Command.require == TwitchConst.REQUIRE_EVERYONE:
			# noone except the owner can use them
			if AuthorPermission.rank < TwitchConst.REQUIRE_OWNER: return False

		# owner disables regular commands in the channel
		if ChannelSettings.owner_disable_regular and Command.require == TwitchConst.REQUIRE_REGULAR:
			# noone except the owner can use them
			if AuthorPermission.rank < TwitchConst.REQUIRE_OWNER: return False

		# owner disables mod commands serverwide,
		if ChannelSettings.owner_disable_mod and Command.require == TwitchConst.REQUIRE_MOD:
			# noone except the owner can use them
			if AuthorPermission.rank < TwitchConst.REQUIRE_OWNER: return False

		# always have a minimum cooldown
		Command.cooldown = max(Command.cooldown, TwitchConst.COOLDOWN_MIN)
		# but also be to long
		Command.cooldown = min(Command.cooldown, TwitchConst.COOLDOWN_MAX)

		# command requires a currency payment, check if user can affort it
		# except mods
		if Command.required_currency != 0 and AuthorPermission.rank < TwitchConst.REQUIRE_MOD:

			# not enough
			if not (TwitchUser.amount_currency >= Command.required_currency):
				cls.BASE.Logger.debug(f"(Twitch) Skipping command call because of insufficient currency: ({TwitchUser.amount_currency} < {Command.required_currency})", require="twitch:commands")
				return False

			await TwitchUser.editCurrency(cls, amount_by=-Command.required_currency )

		# add command to cooldown
		GTCCS.cooldown(Command)

		# increase use
		await Command.increaseUse(cls)

		# throw it to formatCommand and send the return values
		final_result:dict = await formatCommand(cls, Command, CommandContext)

		# there a commands that not have a direct return value,
		# but are still valid and successfull
		if final_result:
			return_content:str = final_result.get("content", None)
			if not return_content: return False
			await Message.Channel.sendMessage(cls, return_content)

		return True

	else:
		return False

async def formatCommand(cls:"PhaazebotTwitch", Command:TwitchCommand, CommandContext:TwitchCommandContext, direct_call:bool=False) -> dict:
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
		func:Awaitable = getTwitchCommandFunction(function_str)

		# this happens if a user enters @phaazebot and then some garbage
		if direct_call and func.__name__ == "textOnly":
			cls.BASE.Logger.debug(f"(Discord) direct call failed, user entered: '{function_str}'", require="twitch:commands")
			return {}

		cls.BASE.Logger.debug(f"(Twitch) execute command '{func.__name__}'", require="twitch:commands")

		return await func(cls, Command, CommandContext)

	else:
		# TODO: to complex functions
		return { "content": "Complex functions are under construction" }
