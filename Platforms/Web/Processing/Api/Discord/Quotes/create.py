from typing import TYPE_CHECKING, Coroutine
if TYPE_CHECKING:
	from Platforms.Discord.main_discord import PhaazebotDiscord
	from Platforms.Web.main_web import PhaazebotWeb

import json
import asyncio
import discord
from aiohttp.web import Response
from Utils.Classes.discordserversettings import DiscordServerSettings
from Utils.Classes.storagetransformer import StorageTransformer
from Utils.Classes.authdiscordwebuser import AuthDiscordWebUser
from Utils.Classes.webrequestcontent import WebRequestContent
from Utils.Classes.extendedrequest import ExtendedRequest
from Utils.Classes.undefined import UNDEFINED
from Platforms.Discord.logging import loggingOnQuoteCreate
from Platforms.Discord.db import getDiscordSeverSettings
from Platforms.Web.utils import authDiscordWebUser
from Platforms.Web.Processing.Api.errors import apiMissingData, apiMissingAuthorisation

MAX_QUOTE_SIZE:int = 1750

async def apiDiscordQuotesCreate(cls:"PhaazebotWeb", WebRequest:ExtendedRequest) -> Response:
	"""
	Default url: /api/discord/quotes/create
	"""
	Data:WebRequestContent = WebRequestContent(WebRequest)
	await Data.load()

	# get required stuff
	Create:StorageTransformer = StorageTransformer()
	Create["guild_id"] = Data.getStr("guild_id", UNDEFINED, must_be_digit=True)
	Create["content"] = Data.getStr("content", UNDEFINED, len_max=MAX_QUOTE_SIZE)

	# checks
	if not Create["guild_id"]:
		return await apiMissingData(cls, WebRequest, msg="missing or invalid 'guild_id'")

	if not Create["content"]:
		return await apiMissingData(cls, WebRequest, msg="missing or invalid 'content'")

	# get/check discord
	PhaazeDiscord:"PhaazebotDiscord" = cls.BASE.Discord
	Guild:discord.Guild = discord.utils.get(PhaazeDiscord.guilds, id=int(Create["guild_id"]))
	if not Guild:
		return await cls.Tree.Api.Discord.errors.apiDiscordGuildUnknown(cls, WebRequest)

	# check limit
	res:list = cls.BASE.PhaazeDB.selectQuery("""
		SELECT COUNT(*) AS `I`
		FROM `discord_quote`
		WHERE `discord_quote`.`guild_id` = %s""",
		(Create["guild_id"],)
	)

	if res[0]['I'] >= cls.BASE.Limit.discord_quotes_amount:
		return await cls.Tree.Api.Discord.Quotes.errors.apiDiscordQuoteLimit(cls, WebRequest)

	# get user info
	DiscordUser:AuthDiscordWebUser = await authDiscordWebUser(cls, WebRequest)
	if not DiscordUser.found:
		return await apiMissingAuthorisation(cls, WebRequest)

	# get member
	CheckMember:discord.Member = Guild.get_member(int(DiscordUser.User.user_id))
	if not CheckMember:
		return await cls.Tree.Api.Discord.errors.apiDiscordMemberNotFound(cls, WebRequest, guild_id=Create["guild_id"], user_id=DiscordUser.User.user_id)

	# check permissions
	if not (CheckMember.guild_permissions.administrator or CheckMember.guild_permissions.manage_guild):
		return await cls.Tree.Api.Discord.errors.apiDiscordMissingPermission(cls, WebRequest, guild_id=Create["guild_id"], user_id=DiscordUser.User.user_id)

	new_quote_id:int = cls.BASE.PhaazeDB.insertQuery(
		table="discord_quote",
		content={
			"guild_id": Create["guild_id"],
			"content": Create["content"]
		}
	)

	# logging
	GuildSettings:DiscordServerSettings = await getDiscordSeverSettings(PhaazeDiscord, Create["guild_id"], prevent_new=True)
	log_coro:Coroutine = loggingOnQuoteCreate(PhaazeDiscord, GuildSettings, Creator=CheckMember, quote_content=Create["content"], quote_id=new_quote_id)
	asyncio.ensure_future(log_coro, loop=cls.BASE.DiscordLoop)

	cls.BASE.Logger.debug(f"(API/Discord) Quote: {Create['guild_id']=} added new entry", require="discord:quotes")
	return cls.response(
		text=json.dumps(dict(msg="Quote: Added new entry", entry=Create["content"], status=200)),
		content_type="application/json",
		status=200
	)
