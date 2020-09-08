from typing import TYPE_CHECKING, Coroutine
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex
	from Platforms.Discord.main_discord import PhaazebotDiscord

import json
import asyncio
import discord
from aiohttp.web import Response, Request
from Utils.Classes.discordserversettings import DiscordServerSettings
from Utils.Classes.webrequestcontent import WebRequestContent
from Utils.Classes.discordwebuserinfo import DiscordWebUserInfo
from Platforms.Discord.db import getDiscordSeverSettings
from Platforms.Discord.logging import loggingOnQuoteCreate
from Platforms.Web.Processing.Api.errors import (
	apiMissingData,
	apiMissingAuthorisation
)
from Platforms.Web.Processing.Api.Discord.errors import (
	apiDiscordGuildUnknown,
	apiDiscordMemberNotFound,
	apiDiscordMissingPermission
)
from .errors import apiDiscordQuoteLimit

async def apiDiscordQuotesCreate(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
	Default url: /api/discord/quotes/create
	"""
	Data:WebRequestContent = WebRequestContent(WebRequest)
	await Data.load()

	# get required stuff
	guild_id:str = Data.getStr("guild_id", "", must_be_digit=True)
	content:str = Data.getStr("content", "")

	# checks
	if not guild_id:
		return await apiMissingData(cls, WebRequest, msg="missing or invalid 'guild_id'")

	if not content:
		return await apiMissingData(cls, WebRequest, msg="missing or invalid 'content'")

	# get/check discord
	PhaazeDiscord:"PhaazebotDiscord" = cls.Web.BASE.Discord
	Guild:discord.Guild = discord.utils.get(PhaazeDiscord.guilds, id=int(guild_id))
	if not Guild:
		return await apiDiscordGuildUnknown(cls, WebRequest)

	# check limit
	res:list = cls.Web.BASE.PhaazeDB.selectQuery("""
		SELECT COUNT(*) AS `I`
		FROM `discord_quote`
		WHERE `discord_quote`.`guild_id` = %s""",
		( guild_id, )
	)

	if res[0]['I'] >= cls.Web.BASE.Limit.DISCORD_QUOTES_AMOUNT:
		return await apiDiscordQuoteLimit(cls, WebRequest)

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

	new_quote_id:int = cls.Web.BASE.PhaazeDB.insertQuery(
		table="discord_quote",
		content={
			"guild_id": guild_id,
			"content": content
		}
	)

	GuildSettings:DiscordServerSettings = await getDiscordSeverSettings(PhaazeDiscord, guild_id, prevent_new=True)
	log_coro:Coroutine = loggingOnQuoteCreate(PhaazeDiscord, GuildSettings, Creator=CheckMember, quote_content=content, quote_id=new_quote_id)
	asyncio.ensure_future(log_coro, loop=cls.Web.BASE.DiscordLoop)

	cls.Web.BASE.Logger.debug(f"(API/Discord) Quote: {guild_id=} added new entry", require="discord:quotes")

	return cls.response(
		text=json.dumps( dict(msg="Quote: Added new entry", entry=content, status=200) ),
		content_type="application/json",
		status=200
	)
