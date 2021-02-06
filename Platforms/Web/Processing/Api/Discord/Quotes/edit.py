from typing import TYPE_CHECKING, Coroutine
if TYPE_CHECKING:
	from Platforms.Web.main_web import PhaazebotWeb
	from Platforms.Discord.main_discord import PhaazebotDiscord

import json
import asyncio
import discord
from aiohttp.web import Response
from Utils.Classes.discordserversettings import DiscordServerSettings
from Utils.Classes.storagetransformer import StorageTransformer
from Utils.Classes.authdiscordwebuser import AuthDiscordWebUser
from Utils.Classes.webrequestcontent import WebRequestContent
from Utils.Classes.extendedrequest import ExtendedRequest
from Utils.Classes.discordquote import DiscordQuote
from Utils.Classes.undefined import UNDEFINED
from Platforms.Discord.db import getDiscordServerQuotes, getDiscordSeverSettings
from Platforms.Discord.logging import loggingOnQuoteEdit
from Platforms.Web.utils import authDiscordWebUser

MAX_QUOTE_SIZE:int = 1750

async def apiDiscordQuotesEdit(cls:"PhaazebotWeb", WebRequest:ExtendedRequest) -> Response:
	"""
	Default url: /api/discord/quotes/edit
	"""
	Data:WebRequestContent = WebRequestContent(WebRequest)
	await Data.load()

	# get required stuff
	Edit:StorageTransformer = StorageTransformer()
	Edit["quote_id"] = Data.getStr("quote_id", UNDEFINED, must_be_digit=True)
	Edit["guild_id"] = Data.getStr("guild_id", UNDEFINED, must_be_digit=True)
	# content:str = Data.getStr("content", "")

	# checks
	if not Edit["quote_id"]:
		return await cls.Tree.Api.errors.apiMissingData(cls, WebRequest, msg="missing or invalid 'quote_id'")

	if not Edit["guild_id"]:
		return await cls.Tree.Api.errors.apiMissingData(cls, WebRequest, msg="missing or invalid 'guild_id'")

	PhaazeDiscord:"PhaazebotDiscord" = cls.BASE.Discord
	Guild:discord.Guild = discord.utils.get(PhaazeDiscord.guilds, id=int(Edit["guild_id"]))
	if not Guild:
		return await cls.Tree.Api.Discord.errors.apiDiscordGuildUnknown(cls, WebRequest)

	# check if exists
	res_quotes:list = await getDiscordServerQuotes(cls.BASE.Discord, guild_id=Edit["guild_id"], quote_id=Edit["quote_id"])

	if not res_quotes:
		return await cls.Tree.Api.Discord.Quotes.errors.apiDiscordQuotesNotExists(cls, WebRequest, quote_id=Edit["quote_id"])

	QuoteToEdit:DiscordQuote = res_quotes.pop(0)

	# check all update values
	update:dict = dict()

	Edit["content"] = Data.getStr("content", UNDEFINED, len_max=MAX_QUOTE_SIZE)
	if Edit["content"] != UNDEFINED:
		update["content"] = Edit["content"]

	# get user info
	AuthDiscord:AuthDiscordWebUser = await authDiscordWebUser(cls, WebRequest)
	if not AuthDiscord.found:
		return await cls.Tree.Api.errors.apiMissingAuthorisation(cls, WebRequest)

	# get member
	CheckMember:discord.Member = Guild.get_member(int(AuthDiscord.User.user_id))
	if not CheckMember:
		return await cls.Tree.Api.Discord.errors.apiDiscordMemberNotFound(cls, WebRequest, guild_id=Edit["guild_id"], user_id=AuthDiscord.User.user_id)

	# check permissions
	if not (CheckMember.guild_permissions.administrator or CheckMember.guild_permissions.manage_guild):
		return await cls.Tree.Api.Discord.errors.apiDiscordMissingPermission(cls, WebRequest, guild_id=Edit["guild_id"], user_id=AuthDiscord.User.user_id)

	cls.BASE.PhaazeDB.updateQuery(
		table="discord_quote",
		content=update,
		where="`discord_quote`.`guild_id` = %s AND `discord_quote`.`id` = %s",
		where_values=(QuoteToEdit.guild_id, QuoteToEdit.quote_id)
	)

	# logging
	GuildSettings:DiscordServerSettings = await getDiscordSeverSettings(PhaazeDiscord, Edit["guild_id"], prevent_new=True)
	log_coro:Coroutine = loggingOnQuoteEdit(
		PhaazeDiscord,
		GuildSettings,
		ChangeMember=CheckMember,
		quote_id=QuoteToEdit.quote_id,
		old_content=QuoteToEdit.content,
		new_content=Edit["content"]
	)
	asyncio.ensure_future(log_coro, loop=cls.BASE.DiscordLoop)

	cls.BASE.Logger.debug(f"(API/Discord) Quote: {Edit['guild_id']=} edited {Edit['quote_id']=}", require="discord:quotes")
	return cls.response(
		text=json.dumps(dict(msg="Quote: Edited entry", changes=update, status=200)),
		content_type="application/json",
		status=200
	)
