from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex
	from Platforms.Discord.main_discord import PhaazebotDiscord

import json
import discord
from aiohttp.web import Response, Request
from Utils.Classes.webrequestcontent import WebRequestContent
from Platforms.Web.Processing.Api.errors import apiMissingData, apiMissingAuthorisation
from Platforms.Web.Processing.Api.Discord.errors import apiDiscordGuildUnknown, apiDiscordMemberNotFound, apiDiscordMissingPermission
from .errors import apiDiscordQuotesNotExists
from Platforms.Discord.utils import getDiscordServerQuotes
from Utils.Classes.discordwebuserinfo import DiscordWebUserInfo
from Utils.Classes.discordquote import DiscordQuote
from Utils.Classes.undefined import UNDEFINED

MAX_QUOTE_SIZE:int = 1750

async def apiDiscordQuotesEdit(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
		Default url: /api/discord/quotes/edit
	"""
	Data:WebRequestContent = WebRequestContent(WebRequest)
	await Data.load()

	# get required stuff
	guild_id:str = Data.getStr("guild_id", "", must_be_digit=True)
	quote_id:int = Data.getInt("quote_id", UNDEFINED, min_x=1)
	content:str = Data.getStr("content", "")

	# checks
	if not guild_id:
		return await apiMissingData(cls, WebRequest, msg="missing or invalid 'guild_id'")

	if not quote_id:
		return await apiMissingData(cls, WebRequest, msg="missing or invalid 'quote_id'")

	if content == "" or len(content) > MAX_QUOTE_SIZE:
		return await apiMissingData(cls, WebRequest, msg="missing or invalid 'content'")

	# get quote
	res_quotes:list = await getDiscordServerQuotes(cls.Web.BASE.Discord, guild_id, quote_id=quote_id)
	if not res_quotes:
		return await apiDiscordQuotesNotExists(cls, WebRequest, quote_id=quote_id)
	CurrentEditQuote:DiscordQuote = res_quotes.pop(0)

	# all checks done, authorise the user
	# get/check discord
	PhaazeDiscord:"PhaazebotDiscord" = cls.Web.BASE.Discord
	Guild:discord.Guild = discord.utils.get(PhaazeDiscord.guilds, id=int(guild_id))
	if not Guild:
		return await apiDiscordGuildUnknown(cls, WebRequest)

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

	cls.Web.BASE.PhaazeDB.updateQuery(
		table = "discord_quote",
		content = {"content": content},
		where = "`discord_quote`.`guild_id` = %s AND `discord_quote`.`id` = %s",
		where_values = (CurrentEditQuote.guild_id, CurrentEditQuote.quote_id)
	)

	cls.Web.BASE.Logger.debug(f"(API/Discord) Edited command: S:{guild_id} Q:{quote_id} C:{content}", require="discord:quotes")

	return cls.response(
		text=json.dumps( dict(msg="quote successfull edited", status=200) ),
		content_type="application/json",
		status=200
	)
