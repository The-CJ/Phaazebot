from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex
	from Platforms.Discord.main_discord import PhaazebotDiscord

import json
import discord
from aiohttp.web import Response, Request
from Utils.Classes.webrequestcontent import WebRequestContent
from Platforms.Web.Processing.Api.errors import apiMissingData
from Utils.Classes.discorduserinfo import DiscordUserInfo
from Platforms.Web.Processing.Api.errors import apiMissingAuthorisation
from Platforms.Web.Processing.Api.Discord.errors import apiDiscordGuildUnknown, apiDiscordMemberNotFound, apiDiscordMissingPermission
from Utils.Classes.undefined import UNDEFINED

async def apiDiscordQuotesDelete(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
		Default url: /api/discord/quotes/delete
	"""
	Data:WebRequestContent = WebRequestContent(WebRequest)
	await Data.load()

	# get required vars
	guild_id:str = Data.getStr("guild_id", UNDEFINED, must_be_digit=True)
	quote_id:int = Data.getInt("quote_id", UNDEFINED, min_x=1)

	if not guild_id:
		return await apiMissingData(cls, WebRequest, msg="missing or invalid 'guild_id'")

	if not quote_id:
		return await apiMissingData(cls, WebRequest, msg="missing or invalid 'quote_id'")

	PhaazeDiscord:"PhaazebotDiscord" = cls.Web.BASE.Discord
	Guild:discord.Guild = discord.utils.get(PhaazeDiscord.guilds, id=int(guild_id))
	if not Guild:
		return await apiDiscordGuildUnknown(cls, WebRequest)

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
			msg = "'administrator' or 'manage_guild' permission required to delete quotes"
		)

	cls.Web.BASE.PhaazeDB.deleteQuery("""
		DELETE FROM `discord_quote`
		WHERE `discord_quote`.`guild_id` = %s
			AND `discord_quote`.`id` = %s""",
		(guild_id, quote_id)
	)

	cls.Web.BASE.Logger.debug(f"(API/Discord) Deleted quote: S:{guild_id} Q:{quote_id}", require="discord:quote")

	return cls.response(
		text=json.dumps( dict(msg="quote successfull deleted", quote_id=quote_id, status=200) ),
		content_type="application/json",
		status=200
	)
