from typing import TYPE_CHECKING, Coroutine
if TYPE_CHECKING:
	from Platforms.Discord.main_discord import PhaazebotDiscord
	from Platforms.Web.main_web import PhaazebotWeb

import json
import asyncio
import discord
from aiohttp.web import Response
from Utils.Classes.discordserversettings import DiscordServerSettings
from Utils.Classes.storagetransformer import StorageTransformer
from Utils.Classes.authdiscordwebuser import AuthDiscordWebUser
from Utils.Classes.webrequestcontent import WebRequestContent
from Utils.Classes.extendedrequest import ExtendedRequest
from Utils.Classes.discordcommand import DiscordCommand
from Utils.Classes.undefined import UNDEFINED
from Platforms.Web.utils import authDiscordWebUser
from Platforms.Discord.db import getDiscordServerCommands, getDiscordSeverSettings
from Platforms.Discord.commandindex import command_register
from Platforms.Discord.logging import loggingOnCommandEdit

async def apiDiscordCommandsEdit(cls:"PhaazebotWeb", WebRequest:ExtendedRequest) -> Response:
	"""
	Default url: /api/discord/commands/edit
	"""
	Data:WebRequestContent = WebRequestContent(WebRequest)
	await Data.load()

	# get required stuff
	Edit:StorageTransformer = StorageTransformer()
	Edit["command_id"] = Data.getInt("command_id", "", min_x=1)
	Edit["guild_id"] = Data.getStr("guild_id", "", must_be_digit=True)

	# checks
	if not Edit["command_id"]:
		return await cls.Tree.Api.errors.apiMissingData(cls, WebRequest, msg="missing or invalid 'command_id'")

	if not Edit["guild_id"]:
		return await cls.Tree.Api.errors.apiMissingData(cls, WebRequest, msg="missing or invalid 'guild_id'")

	# get/check discord
	PhaazeDiscord:"PhaazebotDiscord" = cls.BASE.Discord
	Guild:discord.Guild = discord.utils.get(PhaazeDiscord.guilds, id=int(Edit["guild_id"]))
	if not Guild:
		return await cls.Tree.Api.Discord.errors.apiDiscordGuildUnknown(cls, WebRequest)

	# check if exists
	res_commands:list = await getDiscordServerCommands(PhaazeDiscord, guild_id=Edit["guild_id"], command_id=Edit["command_id"], active=None)
	if not res_commands:
		return await cls.Tree.Api.Discord.Commands.errors.apiDiscordCommandNotExists(cls, WebRequest, command_id=Edit["command_id"])

	CurrentEditCommand:DiscordCommand = res_commands.pop(0)

	# after this point we have a existing command
	# check all possible values if it should be edited
	update:dict = dict()

	# active
	Edit["active"] = Data.getBool("active", UNDEFINED)
	if Edit["active"] != UNDEFINED:
		update["active"] = Edit["active"]

	# trigger
	Edit["trigger"] = Data.getStr("trigger", "", len_max=128).lower().split(" ")[0]
	if Edit["trigger"]:
		# try to get command with this trigger
		check_double_trigger:list = await getDiscordServerCommands(PhaazeDiscord, guild_id=Edit["guild_id"], trigger=Edit["trigger"])
		if check_double_trigger:
			CommandToCheck:DiscordCommand = check_double_trigger.pop(0)
			# tried to set a trigger twice
			if str(CommandToCheck.command_id) != str(CurrentEditCommand.command_id):
				return await cls.Tree.Api.Discord.Commands.errors.apiDiscordCommandExists(cls, WebRequest, trigger=Edit["trigger"])

		update["trigger"] = Edit["trigger"]

	# cooldown
	Edit["cooldown"] = Data.getInt("cooldown", UNDEFINED, min_x=0)
	if Edit["cooldown"] != UNDEFINED:
		# wants a invalid cooldown
		if not (cls.BASE.Limit.discord_commands_cooldown_min <= Edit["cooldown"] <= cls.BASE.Limit.discord_commands_cooldown_max):
			return await cls.Tree.Api.errors.apiWrongData(cls, WebRequest, msg="'cooldown' is wrong")

		update["cooldown"] = Edit["cooldown"]

	# currency
	Edit["required_currency"] = Data.getInt("required_currency", UNDEFINED, min_x=0)
	if Edit["required_currency"] != UNDEFINED:
		update["required_currency"] = Edit["required_currency"]

	# require
	Edit["require"] = Data.getInt("require", UNDEFINED, min_x=0)
	if Edit["require"] != UNDEFINED:
		update["require"] = Edit["require"]

	# content
	Edit["content"] = Data.getStr("content", UNDEFINED, len_max=1750)
	if Edit["content"] != UNDEFINED:
		update["content"] = Edit["content"]

	# hidden
	Edit["hidden"] = Data.getBool("hidden", UNDEFINED)
	if Edit["hidden"] != UNDEFINED:
		update["hidden"] = Edit["hidden"]

	# function (and type)
	Edit["complex"] = Data.getBool("complex", False)
	Edit["function"] = Data.getStr("function", UNDEFINED, len_max=256)
	if not Edit["complex"] and Edit["function"] != UNDEFINED:
		# it its not complex, we need a function
		if Edit["function"] not in [cmd["function"].__name__ for cmd in command_register]:
			return await cls.Tree.Api.errors.apiWrongData(cls, WebRequest, msg=f"'{Edit['function']}' is not a valid value for field 'function'")

		update["complex"] = Edit["complex"]
		update["function"] = Edit["function"]

	if Edit["complex"] and not Edit["function"]:
		# it is complex, we need a content
		if not update.get("content", ""):
			return await cls.Tree.Api.errors.apiWrongData(cls, WebRequest, msg=f"'complex' is true, but missing 'content'")

		update["complex"] = Edit["complex"]
		update["function"] = ""

	# get user info
	AuthDiscord:AuthDiscordWebUser = await authDiscordWebUser(cls, WebRequest)
	if not AuthDiscord.found:
		return await cls.Tree.Api.errors.apiMissingAuthorisation(cls, WebRequest)

	# get member
	CheckMember:discord.Member = Guild.get_member(int(AuthDiscord.User.user_id))
	if not CheckMember:
		return await cls.Tree.Api.Discord.errors.apiDiscordMemberNotFound(cls, WebRequest, guild_id=Edit["guild_id"], user_id=AuthDiscord.User.user_id)

	# check permissions
	if not (CheckMember.guild_permissions.administrator or CheckMember.guild_permissions.manage_guild):
		return await cls.Tree.Api.Discord.errors.apiDiscordMissingPermission(cls, WebRequest, guild_id=Edit["guild_id"], user_id=AuthDiscord.User.user_id)

	if not update:
		return await cls.Tree.Api.errors.apiWrongData(cls, WebRequest, msg=f"No changes, please add at least one")

	cls.BASE.PhaazeDB.updateQuery(
		table="discord_command",
		content=update,
		where="`discord_command`.`guild_id` = %s AND `discord_command`.`id` = %s",
		where_values=(CurrentEditCommand.server_id, CurrentEditCommand.command_id)
	)

	# logging
	GuildSettings:DiscordServerSettings = await getDiscordSeverSettings(PhaazeDiscord, Edit["guild_id"], prevent_new=True)
	log_coro:Coroutine = loggingOnCommandEdit(PhaazeDiscord, GuildSettings, Editor=CheckMember, command_trigger=CurrentEditCommand.trigger, command_info=update)
	asyncio.ensure_future(log_coro, loop=cls.BASE.DiscordLoop)

	cls.BASE.Logger.debug(f"(API/Discord) Commands: {Edit['guild_id']=} edited {Edit['command_id']=}", require="discord:commands")
	return cls.response(
		text=json.dumps(dict(msg="Commands: Edited entry", changes=update, status=200)),
		content_type="application/json",
		status=200
	)
