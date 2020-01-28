from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex
	from Platforms.Discord.main_discord import PhaazebotDiscord

import json
import discord
from aiohttp.web import Response, Request
from Utils.Classes.webrequestcontent import WebRequestContent
from Platforms.Web.Processing.Api.errors import apiMissingData
from Platforms.Discord.utils import getDiscordServerCommands
from Utils.Classes.discordwebuserinfo import DiscordWebUserInfo
from Platforms.Web.Processing.Api.errors import apiMissingAuthorisation
from Platforms.Web.Processing.Api.Discord.errors import apiDiscordGuildUnknown, apiDiscordMemberNotFound, apiDiscordMissingPermission

DEFAULT_LIMIT:int = 50
MAX_LIMIT:int = 100

async def apiDiscordCommandsGet(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
		Default url: /api/discord/commands/get
	"""
	Data:WebRequestContent = WebRequestContent(WebRequest)
	await Data.load()

	# get required vars
	guild_id:str = Data.getStr("guild_id", "", must_be_digit=True)
	command_id:str = Data.getStr("command_id", "", must_be_digit=True)
	show_hidden:bool = Data.getBool("show_hidden", False)
	limit:int = Data.getInt("limit", DEFAULT_LIMIT, min_x=1, max_x=MAX_LIMIT)
	offset:int = Data.getInt("offset", 0, min_x=0)

	# checks
	if not guild_id:
		return await apiMissingData(cls, WebRequest, msg="missing or invalid 'guild_id'")

	PhaazeDiscord:"PhaazebotDiscord" = cls.Web.BASE.Discord
	Guild:discord.Guild = discord.utils.get(PhaazeDiscord.guilds, id=int(guild_id))
	if not Guild:
		return await apiDiscordGuildUnknown(cls, WebRequest)

	if show_hidden:
		# user requested to get full information about commands, requires authorisation

		DiscordUser:DiscordWebUserInfo = await cls.getDiscordUserInfo(WebRequest)
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

	res_commands:list = await getDiscordServerCommands(cls.Web.BASE.Discord, guild_id, command_id=command_id, show_nonactive=show_hidden, limit=limit, offset=offset)

	# this point is only reached when command can be hidden or user requested hidden props has authorist
	api_return:list = list()
	for Command in res_commands:
		api_return.append(Command.toJSON(show_hidden=show_hidden))

	return cls.response(
		text=json.dumps( dict(result=api_return, status=200) ),
		content_type="application/json",
		status=200
	)
