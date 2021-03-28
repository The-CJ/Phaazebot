from typing import TYPE_CHECKING, Coroutine
if TYPE_CHECKING:
	from Platforms.Web.main_web import PhaazebotWeb
	from Platforms.Discord.main_discord import PhaazebotDiscord

import json
import asyncio
import discord
from aiohttp.web import Response
from Utils.Classes.discordserversettings import DiscordServerSettings
from Utils.Classes.authdiscordwebuser import AuthDiscordWebUser
from Utils.Classes.webrequestcontent import WebRequestContent
from Utils.Classes.extendedrequest import ExtendedRequest
from Utils.Classes.discordquote import DiscordQuote
from Platforms.Web.utils import authDiscordWebUser
from Platforms.Discord.db import getDiscordServerQuotes, getDiscordSeverSettings
from Platforms.Discord.logging import loggingOnQuoteDelete
from Platforms.Web.Processing.Api.errors import apiMissingAuthorisation, apiMissingData

async def apiDiscordQuotesDelete(cls:"PhaazebotWeb", WebRequest:ExtendedRequest) -> Response:
	"""
	Default url: /api/discord/quotes/delete
	"""
	Data:WebRequestContent = WebRequestContent(WebRequest)
	await Data.load()

	# get required vars
	guild_id:str = Data.getStr("guild_id", "", must_be_digit=True)
	quote_id:str = Data.getStr("quote_id", "", must_be_digit=True)

	# checks
	if not guild_id:
		return await apiMissingData(cls, WebRequest, msg="missing or invalid 'guild_id'")

	if not quote_id:
		return await apiMissingData(cls, WebRequest, msg="missing or invalid 'quote_id'")

	PhaazeDiscord:"PhaazebotDiscord" = cls.BASE.Discord
	Guild:discord.Guild = discord.utils.get(PhaazeDiscord.guilds, id=int(guild_id))
	if not Guild:
		return await cls.Tree.Api.Discord.errors.apiDiscordGuildUnknown(cls, WebRequest)

	# get user info
	AuthDiscord:AuthDiscordWebUser = await authDiscordWebUser(cls, WebRequest)
	if not AuthDiscord.found:
		return await apiMissingAuthorisation(cls, WebRequest)

	# get member
	CheckMember:discord.Member = Guild.get_member(int(AuthDiscord.User.user_id))
	if not CheckMember:
		return await cls.Tree.Api.Discord.errors.apiDiscordMemberNotFound(cls, WebRequest, guild_id=guild_id, user_id=AuthDiscord.User.user_id)

	# check permissions
	if not (CheckMember.guild_permissions.administrator or CheckMember.guild_permissions.manage_guild):
		return await cls.Tree.Api.Discord.errors. apiDiscordMissingPermission(cls, WebRequest, guild_id=guild_id, user_id=AuthDiscord.User.user_id)

	# get quote
	quote_res:list = await getDiscordServerQuotes(cls.BASE.Discord, guild_id=guild_id, quote_id=quote_id)

	if not quote_res:
		return await cls.Tree.Api.Discord.Quotes.errors.apiDiscordQuotesNotExists(cls, WebRequest, quote_id=quote_id)

	QuoteToDelete:DiscordQuote = quote_res.pop(0)

	cls.BASE.PhaazeDB.deleteQuery("""
		DELETE FROM `discord_quote`	WHERE `guild_id` = %s AND `id` = %s""",
		(QuoteToDelete.guild_id, QuoteToDelete.quote_id)
	)

	# logging
	GuildSettings:DiscordServerSettings = await getDiscordSeverSettings(PhaazeDiscord, guild_id, prevent_new=True)
	log_coro:Coroutine = loggingOnQuoteDelete(PhaazeDiscord, GuildSettings, Deleter=CheckMember, quote_id=QuoteToDelete.quote_id, deleted_content=QuoteToDelete.content)
	asyncio.ensure_future(log_coro, loop=cls.BASE.DiscordLoop)

	cls.BASE.Logger.debug(f"(API/Discord) Quote: {guild_id=} deleted {quote_id=}", require="discord:quote")
	return cls.response(
		text=json.dumps(dict(msg="Quote: Deleted entry", deleted=QuoteToDelete.content, status=200)),
		content_type="application/json",
		status=200
	)
