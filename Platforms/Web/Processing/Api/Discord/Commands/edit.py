from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex
	from Platforms.Discord.main_discord import PhaazebotDiscord

import json
import discord
from aiohttp.web import Response, Request
from Utils.Classes.webrequestcontent import WebRequestContent
from Platforms.Web.Processing.Api.errors import missingData, apiWrongData, apiMissingAuthorisation
from Platforms.Web.Processing.Api.Discord.errors import apiDiscordGuildUnknown, apiDiscordMemberNotFound, apiDiscordMissingPermission, apiDiscordCommandLimit, apiDiscordCommandNotExists, apiDiscordCommandExists
from Platforms.Discord.utils import getDiscordServerCommands
from Utils.Classes.discorduserinfo import DiscordUserInfo
from Utils.Classes.discordcommand import DiscordCommand
from Utils.dbutils import validateDBInput
from Platforms.Discord.commandindex import command_register

async def apiDiscordCommandsEdit(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
		Default url: /api/discord/commands/edit
	"""
	Data:WebRequestContent = WebRequestContent(WebRequest)
	await Data.load()

	# get stuff
	guild_id:str = Data.get("guild_id")
	command_id:str = Data.get("command_id")
	trigger:str = validateDBInput(str, Data.get("trigger"))
	complex_:str = validateDBInput(bool, Data.get("complex"))
	function:str = validateDBInput(str, Data.get("function"))
	content:str = validateDBInput(str, Data.get("content"))
	hidden:str = validateDBInput(bool, Data.get("hidden"))
	cooldown:str = validateDBInput(int, Data.get("cooldown"), 0)
	require:str = validateDBInput(int, Data.get("require"), 0)
	required_currency:str = validateDBInput(int, Data.get("required_currency"), 0)

	# guild id check
	if not guild_id:
		return await missingData(cls, WebRequest, msg="missing 'guild_id'")
	if not guild_id.isdigit():
		return await apiWrongData(cls, WebRequest, msg="'guild_id' must be a number")

	# check command id
	if not command_id:
		return await missingData(cls, WebRequest, msg="missing 'command_id'")

	# only take the first argument of trigger, since everything else can't be typed in a channel
	trigger = trigger.split(" ")[0]
	if not trigger:
		return await missingData(cls, WebRequest, msg="missing 'trigger'")

	#cooldown
	if not (cls.Web.BASE.Limit.DISCORD_COMMANDS_COOLDOWN <= int(cooldown) <= 600 ):
		return await apiWrongData(cls, WebRequest, msg="'cooldown' is wrong")

	#currency
	if not int(required_currency) >= 0 :
		return await apiWrongData(cls, WebRequest, msg="'required_currency' is wrong")

	# if not complex
	# check if the function actully exists
	if complex_ == "0":
		if not function:
			return await missingData(cls, WebRequest, msg="missing 'function'")
		if not function in [cmd["function"].__name__ for cmd in command_register]:
			return await apiWrongData(cls, WebRequest, msg=f"'{function}' is not a valid value for field 'function'")

	# check if command exists before edit
	commands:list = await getDiscordServerCommands(cls.Web.BASE.Discord, guild_id, command_id=command_id)
	if not commands:
		return await apiDiscordCommandNotExists(cls, WebRequest, command=trigger)

	# check if there is another command with the trigger that wants to be set, that is NOT the one currently editing
	check_double_trigger:list = await getDiscordServerCommands(cls.Web.BASE.Discord, guild_id, trigger=trigger)
	if check_double_trigger:
		CommandToCheck:DiscordCommand = check_double_trigger[0]
		if str(CommandToCheck.command_id) != str(command_id):
			return await apiDiscordCommandExists(cls, WebRequest, command=trigger)

	# get/check discord
	PhaazeDiscord:"PhaazebotDiscord" = cls.Web.BASE.Discord
	Guild:discord.Guild = discord.utils.get(PhaazeDiscord.guilds, id=int(guild_id))
	if not Guild:
		return await apiDiscordGuildUnknown(cls, WebRequest)

	# check limit
	commands:list = await getDiscordServerCommands(cls.Web.BASE.Discord, guild_id)
	if len(commands) >= cls.Web.BASE.Limit.DISCORD_COMMANDS_AMOUNT:
		return await apiDiscordCommandLimit(cls, WebRequest)

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

	update:dict = dict(
		trigger = trigger,
		complex = complex_,
		function = function,
		require = require,
		required_currency = required_currency,
		hidden = hidden,
		content = content,
		cooldown = cooldown
	)

	cls.Web.BASE.PhaazeDB.updateQuery(
		table = "discord_command",
		content = update,
		where = "discord_command.guild_id = %s AND discord_command.id = %s",
		where_values = (guild_id, command_id)
	)

	cls.Web.BASE.Logger.debug(f"(API/Discord) Edited command: S:{guild_id} T:{trigger}", require="discord:commands")

	return cls.response(
		text=json.dumps( dict(msg="new command successfull edited", command=trigger, status=200) ),
		content_type="application/json",
		status=200
	)