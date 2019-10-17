from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex
	from Platforms.Discord.main_discord import PhaazebotDiscord

import json
import discord
from aiohttp.web import Response, Request
from Utils.Classes.webrequestcontent import WebRequestContent
from Platforms.Web.Processing.Api.errors import missingData, apiWrongData, apiMissingAuthorisation
from Platforms.Web.Processing.Api.Discord.errors import apiDiscordGuildUnknown, apiDiscordMemberNotFound, apiDiscordMissingPermission, apiDiscordCommandNotExists, apiDiscordCommandExists
from Platforms.Discord.utils import getDiscordServerCommands
from Utils.Classes.discorduserinfo import DiscordUserInfo
from Utils.Classes.discordcommand import DiscordCommand
from Platforms.Discord.commandindex import command_register

async def apiDiscordCommandsEdit(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
		Default url: /api/discord/commands/edit
	"""
	Data:WebRequestContent = WebRequestContent(WebRequest)
	await Data.load()

	# get required stuff
	guild_id:str = Data.getStr("guild_id", "", must_be_digit=True)
	command_id:str = Data.getStr("command_id", "0", must_be_digit=True)

	# guild id check
	if not guild_id:
		return await missingData(cls, WebRequest, msg="missing or invalid 'guild_id'")

	# check command id
	if not command_id:
		return await missingData(cls, WebRequest, msg="missing or invalid 'command_id'")

	# check if command exists before edit
	commands:list = await getDiscordServerCommands(cls.Web.BASE.Discord, guild_id, command_id=command_id)
	if not commands:
		return await apiDiscordCommandNotExists(cls, WebRequest, command_id=command_id)

	CurrentEditCommand:DiscordCommand = commands.pop()

	# after this point we have a existing command
	# check all possible values if it should be edited
	update:dict = dict()

	# change trigger?
	trigger:str = Data.getStr("trigger", "")
	if trigger:
		# only take the first argument of trigger, since everything else can't be typed in a channel
		trigger = trigger.split(" ")[0]
		if not trigger:
			# should never happen
			return await missingData(cls, WebRequest, msg="missing 'trigger'")

		# check if there is another command with the trigger that wants to be set, that is NOT the one currently editing
		check_double_trigger:list = await getDiscordServerCommands(cls.Web.BASE.Discord, guild_id, trigger=trigger)
		if check_double_trigger:
			CommandToCheck:DiscordCommand = check_double_trigger.pop()
			if str(CommandToCheck.command_id) != str(CurrentEditCommand.command_id):
				return await apiDiscordCommandExists(cls, WebRequest, command=trigger)

		update["trigger"] = trigger

	# change cooldown
	cooldown:int = Data.getInt("cooldown", None, min_x=0)
	if cooldown != None:
		# wants a invalid cooldown
		if not (cls.Web.BASE.Limit.DISCORD_COMMANDS_COOLDOWN_MIN <= cooldown <= cls.Web.BASE.Limit.DISCORD_COMMANDS_COOLDOWN_MAX ):
			return await apiWrongData(cls, WebRequest, msg="'cooldown' is wrong")

		update["cooldown"] = cooldown

	# change currency
	required_currency:int = Data.getInt("required_currency", None, min_x=0)
	if required_currency != None:
		update["required_currency"] = required_currency

	# change require
	require:int = Data.getInt("require", None, min_x=0)
	if require != None :
		update["require"] = require

	# change content
	content:str = Data.getStr("content", None)
	if content != None:
		update["content"] = content

	# change hidden
	hidden:bool = Data.getBool("hidden", None)
	if hidden != None:
		update["hidden"] = hidden

	# change function
	complex_:bool = Data.getBool("complex", False)
	function:str = Data.getStr("function", "")
	if not complex_:
		# it its not complex, we need a function
		if not function:
			return await missingData(cls, WebRequest, msg="missing 'function'")
		if not function in [cmd["function"].__name__ for cmd in command_register]:
			return await apiWrongData(cls, WebRequest, msg=f"'{function}' is not a valid value for field 'function'")

		update["complex"] = complex_
		update["function"] = function

	else:
		# it is complex, we need a content
		if not content:
			return await apiWrongData(cls, WebRequest, msg=f"'complex' is true, but missing 'content'")

	# all checks done, authorise the user

	# get/check discord
	PhaazeDiscord:"PhaazebotDiscord" = cls.Web.BASE.Discord
	Guild:discord.Guild = discord.utils.get(PhaazeDiscord.guilds, id=int(guild_id))
	if not Guild:
		return await apiDiscordGuildUnknown(cls, WebRequest)

	# get user info
	DiscordUser:DiscordUserInfo = await cls.getDiscordUserInfo(WebRequest)
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
		content = update,
		where = "discord_command.guild_id = %s AND discord_command.id = %s",
		where_values = (guild_id, command_id)
	)

	cls.Web.BASE.Logger.debug(f"(API/Discord) Edited command: S:{guild_id} T:{trigger} U:{str(update)}", require="discord:commands")

	return cls.response(
		text=json.dumps( dict(msg="new command successfull edited", command=trigger, status=200) ),
		content_type="application/json",
		status=200
	)
