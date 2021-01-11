from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex
	from Platforms.Discord.main_discord import PhaazebotDiscord

import json
import discord
from aiohttp.web import Response, Request
from Utils.Classes.webrequestcontent import WebRequestContent
from Utils.Classes.discordwebuser import DiscordWebUser
from Platforms.Web.Processing.Api.errors import apiMissingAuthorisation, apiMissingData
from Platforms.Web.Processing.Api.Discord.errors import (
	apiDiscordGuildUnknown,
	apiDiscordMemberNotFound,
	apiDiscordMissingPermission,
)
from .errors import apiDiscordWhitelistedLinkExists

async def apiDiscordConfigsWhitelistedLinkCreate(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
		Default url: /api/discord/configs/whitelistedlinks/create
	"""
	Data:WebRequestContent = WebRequestContent(WebRequest)
	await Data.load()

	# get required stuff
	guild_id:str = Data.getStr("guild_id", "", must_be_digit=True)
	link:str = Data.getStr("link", "", len_max=512)

	# checks
	if not guild_id:
		return await apiMissingData(cls, WebRequest, msg="missing or invalid 'guild_id'")

	if not link:
		return await apiMissingData(cls, WebRequest, msg="missing or invalid 'link'")

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

	# check if already exists
	res:list = cls.Web.BASE.PhaazeDB.selectQuery("""
		SELECT COUNT(*) AS `match`
		FROM `discord_blacklist_whitelistlink`
		WHERE `discord_blacklist_whitelistlink`.`guild_id` = %s
			AND `discord_blacklist_whitelistlink`.`link` = %s""",
		( guild_id, link )
	)

	if res[0]["match"]:
			return await apiDiscordWhitelistedLinkExists(cls, WebRequest, link=link)

	cls.Web.BASE.PhaazeDB.insertQuery(
		table = "discord_blacklist_whitelistlink",
		content = {
			"guild_id": guild_id,
			"link": link
		}
	)

	cls.Web.BASE.Logger.debug(f"(API/Discord) Linkwhitelist: {guild_id=} added: {link=}", require="discord:configs")
	return cls.response(
		text=json.dumps( dict(msg="Linkwhitelist: Added new entry", entry=link, status=200) ),
		content_type="application/json",
		status=200
	)
