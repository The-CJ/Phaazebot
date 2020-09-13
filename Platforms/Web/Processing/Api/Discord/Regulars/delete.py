from typing import TYPE_CHECKING, List, Coroutine
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex
	from Platforms.Discord.main_discord import PhaazebotDiscord

import json
import asyncio
import discord
from aiohttp.web import Response, Request
from Utils.Classes.discordserversettings import DiscordServerSettings
from Utils.Classes.discordwebuserinfo import DiscordWebUserInfo
from Utils.Classes.webrequestcontent import WebRequestContent
from Utils.Classes.discordregular import DiscordRegular
from Platforms.Discord.db import getDiscordServerRegulars, getDiscordSeverSettings
from Platforms.Discord.logging import loggingOnRegularDelete
from Platforms.Web.Processing.Api.errors import apiMissingAuthorisation, apiMissingData
from Platforms.Web.Processing.Api.Discord.errors import apiDiscordGuildUnknown, apiDiscordMemberNotFound, apiDiscordMissingPermission
from .errors import apiDiscordRegularNotExists

async def apiDiscordRegularsDelete(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
	Default url: /api/discord/regulars/delete
	"""
	Data:WebRequestContent = WebRequestContent(WebRequest)
	await Data.load()

	# get required vars
	guild_id:str = Data.getStr("guild_id", "", must_be_digit=True)
	regular_id:str = Data.getStr("regular_id", "", must_be_digit=True)

	# checks
	if not guild_id:
		return await apiMissingData(cls, WebRequest, msg="missing or invalid 'guild_id'")

	if not regular_id:
		return await apiMissingData(cls, WebRequest, msg="missing or invalid 'regular_id'")

	PhaazeDiscord:"PhaazebotDiscord" = cls.Web.BASE.Discord
	Guild:discord.Guild = discord.utils.get(PhaazeDiscord.guilds, id=int(guild_id))
	if not Guild:
		return await apiDiscordGuildUnknown(cls, WebRequest)

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

	# get regular
	regular_res:List[DiscordRegular] = await getDiscordServerRegulars(cls.Web.BASE.Discord, guild_id, regular_id=regular_id)

	if not regular_res:
		return await apiDiscordRegularNotExists(cls, WebRequest, regular_id=regular_id)

	RegularToDelete:DiscordRegular = regular_res.pop(0)

	cls.Web.BASE.PhaazeDB.deleteQuery("""
		DELETE FROM `discord_regular` WHERE `guild_id` = %s AND `id` = %s""",
		(RegularToDelete.guild_id, RegularToDelete.regular_id)
	)

	# logging
	GuildSettings:DiscordServerSettings = await getDiscordSeverSettings(PhaazeDiscord, guild_id, prevent_new=True)
	log_coro:Coroutine = loggingOnRegularDelete(PhaazeDiscord, GuildSettings, Remover=CheckMember, old_regular_id=RegularToDelete.member_id)
	asyncio.ensure_future(log_coro, loop=cls.Web.BASE.DiscordLoop)

	cls.Web.BASE.Logger.debug(f"(API/Discord) Regular: {guild_id=} deleted {regular_id=}", require="discord:regular")
	return cls.response(
		text=json.dumps( dict(msg="Regular: Deleted entry", deleted=RegularToDelete.member_id, status=200) ),
		content_type="application/json",
		status=200
	)
