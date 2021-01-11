from typing import TYPE_CHECKING, Coroutine
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex
	from Platforms.Discord.main_discord import PhaazebotDiscord

import json
import asyncio
import discord
from aiohttp.web import Response, Request
from Utils.Classes.discordserversettings import DiscordServerSettings
from Utils.Classes.discordwebuser import DiscordWebUser
from Utils.Classes.webrequestcontent import WebRequestContent
from Platforms.Web.Processing.Api.errors import apiMissingData, apiMissingAuthorisation
from Platforms.Web.Processing.Api.Discord.errors import apiDiscordGuildUnknown, apiDiscordMemberNotFound, apiDiscordMissingPermission
from .errors import apiDiscordQuotesNotExists
from Platforms.Discord.db import getDiscordServerQuotes, getDiscordSeverSettings
from Platforms.Discord.logging import loggingOnQuoteEdit
from Utils.Classes.discordquote import DiscordQuote

MAX_QUOTE_SIZE:int = 1750

async def apiDiscordQuotesEdit(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
	Default url: /api/discord/quotes/edit
	"""
	Data:WebRequestContent = WebRequestContent(WebRequest)
	await Data.load()

	# get required stuff
	guild_id:str = Data.getStr("guild_id", "", must_be_digit=True)
	quote_id:str = Data.getStr("quote_id", "", must_be_digit=True)
	content:str = Data.getStr("content", "")

	# checks
	if not guild_id:
		return await apiMissingData(cls, WebRequest, msg="missing or invalid 'guild_id'")

	if not quote_id:
		return await apiMissingData(cls, WebRequest, msg="missing or invalid 'quote_id'")

	if content == "" or len(content) > MAX_QUOTE_SIZE:
		return await apiMissingData(cls, WebRequest, msg="missing or invalid 'content'")

	# get/check discord
	PhaazeDiscord:"PhaazebotDiscord" = cls.Web.BASE.Discord
	Guild:discord.Guild = discord.utils.get(PhaazeDiscord.guilds, id=int(guild_id))
	if not Guild:
		return await apiDiscordGuildUnknown(cls, WebRequest)

	# get user info
	DiscordUser:DiscordWebUser = await cls.getDiscordUserInfo(WebRequest)
	if not DiscordUser.found:
		return await apiMissingAuthorisation(cls, WebRequest)

	# get member
	CheckMember:discord.Member = Guild.get_member(int(DiscordUser.user_id))
	if not CheckMember:
		return await apiDiscordMemberNotFound(cls, WebRequest, guild_id=guild_id, user_id=DiscordUser.user_id)

	# check permissions
	if not (CheckMember.guild_permissions.administrator or CheckMember.guild_permissions.manage_guild):
		return await apiDiscordMissingPermission(cls, WebRequest, guild_id=guild_id, user_id=DiscordUser.user_id)

	# get quote
	res_quotes:list = await getDiscordServerQuotes(cls.Web.BASE.Discord, guild_id, quote_id=quote_id)

	if not res_quotes:
		return await apiDiscordQuotesNotExists(cls, WebRequest, quote_id=quote_id)

	CurrentEditQuote:DiscordQuote = res_quotes.pop(0)

	changes:dict = {"content": content}

	cls.Web.BASE.PhaazeDB.updateQuery(
		table = "discord_quote",
		content = changes,
		where = "`discord_quote`.`guild_id` = %s AND `discord_quote`.`id` = %s",
		where_values = (CurrentEditQuote.guild_id, CurrentEditQuote.quote_id)
	)

	# logging
	GuildSettings:DiscordServerSettings = await getDiscordSeverSettings(PhaazeDiscord, guild_id, prevent_new=True)
	log_coro:Coroutine = loggingOnQuoteEdit(
		PhaazeDiscord,
		GuildSettings,
		ChangeMember=CheckMember,
		quote_id=CurrentEditQuote.quote_id,
		old_content=CurrentEditQuote.content,
		new_content=changes.get("content", "")
	)
	asyncio.ensure_future(log_coro, loop=cls.Web.BASE.DiscordLoop)

	cls.Web.BASE.Logger.debug(f"(API/Discord) Quote: {guild_id=} edited {quote_id=}", require="discord:quotes")
	return cls.response(
		text=json.dumps( dict(msg="Quote: Edited entry", changes=changes, status=200) ),
		content_type="application/json",
		status=200
	)
