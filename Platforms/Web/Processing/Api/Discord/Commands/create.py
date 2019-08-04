from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex
	from Platforms.Discord.main_discord import PhaazebotDiscord

import json
import discord
from aiohttp.web import Response, Request
from Utils.Classes.webrequestcontent import WebRequestContent
from Platforms.Web.Processing.Api.errors import missingData, apiWrongData
from Platforms.Web.Processing.Api.Discord.errors import apiDiscordGuildUnknown, apiDiscordMemberNotFound, apiDiscordMissingPermission
from Platforms.Discord.utils import getDiscordServerCommands

from Utils.Classes.discorduserinfo import DiscordUserInfo

async def apiDiscordCommandsCreate(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
		Default url: /api/discord/commands/create
	"""
	Data:WebRequestContent = WebRequestContent(WebRequest)
	await Data.load()

	guild_id:str = Data.get("guild_id")
	if not guild_id:
		return await missingData(cls, WebRequest, msg="missing 'guild_id'")

	if not guild_id.isdigit():
		return await apiWrongData(cls, WebRequest, msg="'guild_id' must be a number")

	PhaazeDiscord:"PhaazebotDiscord" = cls.Web.BASE.Discord
	Guild:discord.Guild = discord.utils.get(PhaazeDiscord.guilds, id=int(guild_id))
	if not Guild:
		return await apiDiscordGuildUnknown(cls, WebRequest)

	DiscordUser:DiscordUserInfo = await cls.getDiscordUserInfo(WebRequest)
	CheckMember:discord.Member = Guild.get_member(int(DiscordUser.user_id))
	if not CheckMember:
		return await apiDiscordMemberNotFound(cls, WebRequest, guild_id=guild_id, user_id=DiscordUser.user_id)

	if not (CheckMember.guild_permissions.administrator or CheckMember.guild_permissions.manage_guild):
		return await apiDiscordMissingPermission(cls, WebRequest, guild_id=guild_id, user_id=DiscordUser.user_id)

	trigger:str = Data.get("trigger")
	if not trigger:
		return await missingData(cls, WebRequest, msg="missing 'trigger'")

	content:str = str(Data.get("content"))
	function:str = str(Data.get("function"))
	complex_:bool = bool(Data.get("complex"))
	hidden:bool = bool(Data.get("hidden"))
	require:str = str(Data.get("require"))
	required_currency:str = str(Data.get("required_currency"))

	cls.Web.BASE.PhaazeDB.query("""
		INSERT INTO discord_command
		(`guild_id`, `trigger`, `content`,
		 `function`, `complex`, `hidden`,
		 `require`, `required_currency`
		)
		VALUES (
		 %s, %s, %s,
		 %s, %s, %s,
		 %s, %s)""",
		(guild_id, trigger, content,
		function, complex_, hidden,
		require, required_currency)
	)

	commands:list = await getDiscordServerCommands(cls.Web.BASE.Discord, guild_id)
	print(len(commands))

	return cls.response(
		text=json.dumps( dict(result="", status=200) ),
		content_type="application/json",
		status=200
	)
