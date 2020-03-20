from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex
	from Platforms.Discord.main_discord import PhaazebotDiscord

import json
import discord
from aiohttp.web import Response, Request
from Utils.Classes.webrequestcontent import WebRequestContent
from Utils.Classes.discordwebuserinfo import DiscordWebUserInfo
from Utils.Classes.discordwhitelistedlink import DiscordWhitelistedLink
from Platforms.Discord.utils import getDiscordServerWhitelistedLinks
from Platforms.Web.Processing.Api.errors import (
	apiMissingAuthorisation,
	apiMissingData
)
from Platforms.Web.Processing.Api.Discord.errors import (
	apiDiscordGuildUnknown,
	apiDiscordMemberNotFound,
	apiDiscordMissingPermission
)
from .errors import apiDiscordWhitelistedLinkNotExists

async def apiDiscordConfigsWhitelistedLinkDelete(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
		Default url: /api/discord/configs/exceptionroles/delete
	"""
	Data:WebRequestContent = WebRequestContent(WebRequest)
	await Data.load()

	# get required stuff
	guild_id:str = Data.getStr("guild_id", "", must_be_digit=True)
	link_id:str = Data.getStr("link_id", "", must_be_digit=True)
	link:str = Data.getStr("link", "")

	# checks
	if not guild_id:
		return await apiMissingData(cls, WebRequest, msg="missing or invalid 'guild_id'")

	if (not link_id) and (not link):
		return await apiMissingData(cls, WebRequest, msg="missing or invalid 'link_id' or 'link'")

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

	# get links
	link_res:list = await getDiscordServerWhitelistedLinks(cls.Web.BASE.Discord, guild_id, link_id=link_id, link=link)

	if not link_res:
		return await apiDiscordWhitelistedLinkNotExists(cls, WebRequest, link_id=link_id, link=link)

	LinkToDelete:DiscordWhitelistedLink = link_res.pop(0)

	cls.Web.BASE.PhaazeDB.deleteQuery("""
		DELETE FROM `discord_blacklist_whitelistlink` WHERE `guild_id` = %s AND `id` = %s""",
		(LinkToDelete.guild_id, LinkToDelete.link_id)
	)

	cls.Web.BASE.Logger.debug(f"(API/Discord) Linkwhitelist: {guild_id=} deleted [{link_id=}, {link=}]", require="discord:configs")
	return cls.response(
		text=json.dumps( dict(msg=f"Linkwhitelist: Deleted entry", deleted=LinkToDelete.link, status=200) ),
		content_type="application/json",
		status=200
	)
