from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex
	from Platforms.Discord.main_discord import PhaazebotDiscord

import json
import discord
from aiohttp.web import Response, Request
from Platforms.Discord.commandindex import command_register
from Utils.Classes.webrequestcontent import WebRequestContent
from Utils.Classes.undefined import UNDEFINED
from Utils.Classes.discordwebuserinfo import DiscordWebUserInfo
from Utils.Classes.discordcommand import DiscordCommand
from Platforms.Discord.utils import getDiscordServerCommands
from Utils.dbutils import validateDBInput
from Platforms.Web.Processing.Api.errors import (
	apiMissingData,
	apiWrongData,
	apiMissingAuthorisation
)
from Platforms.Web.Processing.Api.Discord.errors import (
	apiDiscordGuildUnknown,
	apiDiscordMemberNotFound,
	apiDiscordMissingPermission
)
from .errors import (
	apiDiscordCommandExists,
	apiDiscordCommandNotExists
)

async def apiDiscordCommandsEdit(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
		Default url: /api/discord/commands/edit
	"""
	Data:WebRequestContent = WebRequestContent(WebRequest)
	await Data.load()

	# get required stuff
	guild_id:str = Data.getStr("guild_id", "", must_be_digit=True)
	command_id:str = Data.getStr("command_id", "", must_be_digit=True)

	# checks
	if not guild_id:
		return await apiMissingData(cls, WebRequest, msg="missing or invalid 'guild_id'")

	if not command_id:
		return await apiMissingData(cls, WebRequest, msg="missing or invalid 'command_id'")

	# get command
	res_commands:list = await getDiscordServerCommands(cls.Web.BASE.Discord, guild_id, command_id=command_id, show_nonactive=True)
	if not res_commands:
		return await apiDiscordCommandNotExists(cls, WebRequest, command_id=command_id)

	CurrentEditCommand:DiscordCommand = res_commands.pop(0)

	# after this point we have a existing command
	# check all possible values if it should be edited
	# db_update is for the database
	# update is the return for the user
	db_update:dict = dict()
	update:dict = dict()

	# active
	value:bool = Data.getBool("active", UNDEFINED)
	if value != UNDEFINED:
		db_update["active"] = validateDBInput(bool, value)
		update["active"] = value

	# trigger
	value:str = Data.getStr("trigger", "").lower().split(" ")[0]
	if value:
		# try to get command with this trigger
		check_double_trigger:list = await getDiscordServerCommands(cls.Web.BASE.Discord, guild_id, trigger=value)
		if check_double_trigger:
			CommandToCheck:DiscordCommand = check_double_trigger.pop(0)
			# tryed to set a trigger twice
			if str(CommandToCheck.command_id) != str(CurrentEditCommand.command_id):
				return await apiDiscordCommandExists(cls, WebRequest, command=value)

		db_update["trigger"] = validateDBInput(str, value)
		update["trigger"] = value

	# cooldown
	value:int = Data.getInt("cooldown", UNDEFINED, min_x=0)
	if value != UNDEFINED:
		# wants a invalid cooldown
		if not (cls.Web.BASE.Limit.DISCORD_COMMANDS_COOLDOWN_MIN <= value <= cls.Web.BASE.Limit.DISCORD_COMMANDS_COOLDOWN_MAX ):
			return await apiWrongData(cls, WebRequest, msg="'cooldown' is wrong")

		db_update["cooldown"] = validateDBInput(int, value)
		update["cooldown"] = value

	# currency
	value:int = Data.getInt("required_currency", UNDEFINED, min_x=0)
	if value != UNDEFINED:
		db_update["required_currency"] = validateDBInput(int, value)
		update["required_currency"] = value

	# require
	value:int = Data.getInt("require", UNDEFINED, min_x=0)
	if value != UNDEFINED :
		db_update["require"] = validateDBInput(int, value)
		update["require"] = value

	# content
	value:str = Data.getStr("content", UNDEFINED)
	if value != UNDEFINED:
		db_update["content"] = validateDBInput(str, value)
		update["content"] = value

	# hidden
	value:bool = Data.getBool("hidden", UNDEFINED)
	if value != UNDEFINED:
		db_update["hidden"] = validateDBInput(bool, value)
		update["hidden"] = value

	# function (and type)
	complex_:bool = Data.getBool("complex", False)
	function:str = Data.getStr("function", UNDEFINED)
	if (complex_ == False) and (function != UNDEFINED):
		# it its not complex, we need a function
		if not function in [cmd["function"].__name__ for cmd in command_register]:
			return await apiWrongData(cls, WebRequest, msg=f"'{function}' is not a valid value for field 'function'")

		db_update["complex"] = validateDBInput(bool, complex_)
		db_update["function"] = validateDBInput(str, function)
		update["complex"] = complex_
		update["function"] = function

	if (complex_ == True) and (not function):
		# it is complex, we need a content
		if not update.get("content", False):
			return await apiWrongData(cls, WebRequest, msg=f"'complex' is true, but missing 'content'")

		db_update["complex"] = validateDBInput(bool, complex_)
		db_update["function"] = ""
		update["complex"] = complex_

	# get/check discord
	PhaazeDiscord:"PhaazebotDiscord" = cls.Web.BASE.Discord
	Guild:discord.Guild = discord.utils.get(PhaazeDiscord.guilds, id=int(guild_id))
	if not Guild:
		return await apiDiscordGuildUnknown(cls, WebRequest)

	# get user info
	DiscordUser:DiscordWebUserInfo = await cls.getDiscordUserInfo(WebRequest)
	if not DiscordUser.found:
		return await apiMissingAuthorisation(cls, WebRequest)

	# get member
	CheckMember:discord.Member = Guild.get_member(int(DiscordUser.user_id))
	if not CheckMember:
		return await apiDiscordMemberNotFound(cls, WebRequest, guild_id=guild_id, user_id=DiscordUser.user_id)

	# check permissions
	if not (CheckMember.guild_permissions.administrator or CheckMember.guild_permissions.manage_guild):
		return await apiDiscordMissingPermission(cls, WebRequest, guild_id=guild_id, user_id=DiscordUser.user_id)

	if not update:
		return await apiWrongData(cls, WebRequest, msg=f"No changes, please add at least one")

	cls.Web.BASE.PhaazeDB.updateQuery(
		table = "discord_command",
		content = db_update,
		where = "`discord_command`.`guild_id` = %s AND `discord_command`.`id` = %s",
		where_values = (guild_id, command_id)
	)

	cls.Web.BASE.Logger.debug(f"(API/Discord) Edited command: S:{guild_id} C:{command_id} U:{str(db_update)}", require="discord:commands")

	return cls.response(
		text=json.dumps( dict(msg="new command successfull edited", command=CurrentEditCommand.trigger, changes=update, status=200) ),
		content_type="application/json",
		status=200
	)
