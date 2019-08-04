from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex
	from Platforms.Discord.main_discord import PhaazebotDiscord

import json
import discord
from aiohttp.web import Response, Request
from Utils.Classes.webrequestcontent import WebRequestContent
from Platforms.Web.Processing.Api.errors import missingData
from Platforms.Discord.utils import getDiscordServerCommands
from Utils.Classes.discorduserinfo import DiscordUserInfo
from Platforms.Web.Processing.Api.errors import apiMissingAuthorisation
from Platforms.Web.Processing.Api.Discord.errors import apiDiscordGuildUnknown, apiDiscordMemberNotFound, apiDiscordMissingPermission
from Utils.dbutils import validateDBInput

async def apiDiscordCommandsGet(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
		Default url: /api/discord/commands/get
	"""
	Data:WebRequestContent = WebRequestContent(WebRequest)
	await Data.load()

	guild_id:str = Data.get("guild_id")
	if not guild_id:
		return await missingData(cls, WebRequest, msg="missing 'guild_id'")

	PhaazeDiscord:"PhaazebotDiscord" = cls.Web.BASE.Discord
	Guild:discord.Guild = discord.utils.get(PhaazeDiscord.guilds, id=int(guild_id))
	if not Guild:
		return await apiDiscordGuildUnknown(cls, WebRequest)

	command_id:str = Data.get("command_id")
	if not command_id:
		command_id = None

	commands:list = await getDiscordServerCommands(cls.Web.BASE.Discord, guild_id, command_id=command_id)

	show_hidden:bool = True if validateDBInput(bool, Data.get("show_hidden")) == "1" else False
	if show_hidden:
		# user requested to get full information about commands, requires authorisation

		DiscordUser:DiscordUserInfo = await cls.getDiscordUserInfo(WebRequest)
		if not DiscordUser.found:
			return await apiMissingAuthorisation(cls, WebRequest)

		# get member
		CheckMember:discord.Member = Guild.get_member(int(DiscordUser.user_id))
		if not CheckMember:
			return await apiDiscordMemberNotFound(cls, WebRequest, guild_id=guild_id, user_id=DiscordUser.user_id)

		# check permissions
		if not (CheckMember.guild_permissions.administrator or CheckMember.guild_permissions.manage_guild):
			return await apiDiscordMissingPermission(
				cls,
				WebRequest,
				guild_id=guild_id,
				user_id=DiscordUser.user_id,
				msg = "'administrator' or 'manage_guild' permission required to show commands with hidden properties"
			)

	# this point is only reached when command can be hidden or user requested hidden props has authorist
	api_return:list = list()
	for command in commands:

		cmd:dict = dict(
			trigger = command.trigger,
			name = command.name if show_hidden else (command.name if not command.hidden else None),
			function = command.function if show_hidden else (command.function if not command.hidden else None),
			description = command.description if show_hidden else (command.description if not command.hidden else None),
			content = command.content if show_hidden else (command.content if not command.hidden else None),
			complex = command.complex,
			cost = command.required_currency,
			uses = command.uses,
			require = command.require,
			hidden = command.hidden,
			id = command.command_id
		)

		api_return.append(cmd)

	return cls.response(
		text=json.dumps( dict(result=api_return, status=200) ),
		content_type="application/json",
		status=200
	)
