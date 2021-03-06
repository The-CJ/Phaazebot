from typing import TYPE_CHECKING, List
if TYPE_CHECKING:
	from Platforms.Discord.main_discord import PhaazebotDiscord
	from Platforms.Web.main_web import PhaazebotWeb

import json
import discord
from aiohttp.web import Response
from Utils.Classes.discordwhitelistedlink import DiscordWhitelistedLink
from Utils.Classes.authdiscordwebuser import AuthDiscordWebUser
from Utils.Classes.webrequestcontent import WebRequestContent
from Utils.Classes.extendedrequest import ExtendedRequest
from Utils.Classes.undefined import UNDEFINED
from Platforms.Discord.db import getDiscordServerWhitelistedLinks
from Platforms.Web.utils import authDiscordWebUser
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

async def apiDiscordConfigsWhitelistedLinkDelete(cls:"PhaazebotWeb", WebRequest:ExtendedRequest) -> Response:
	"""
	Default url: /api/discord/configs/exceptionroles/delete
	"""
	Data:WebRequestContent = WebRequestContent(WebRequest)
	await Data.load()

	# get required stuff
	guild_id:str = Data.getStr("guild_id", UNDEFINED, must_be_digit=True)
	link_id:str = Data.getStr("link_id", UNDEFINED, must_be_digit=True)

	# checks
	if not guild_id:
		return await apiMissingData(cls, WebRequest, msg="missing or invalid 'guild_id'")

	if not link_id:
		return await apiMissingData(cls, WebRequest, msg="missing or invalid 'link_id'")

	PhaazeDiscord:"PhaazebotDiscord" = cls.BASE.Discord
	Guild:discord.Guild = discord.utils.get(PhaazeDiscord.guilds, id=int(guild_id))
	if not Guild:
		return await apiDiscordGuildUnknown(cls, WebRequest)

	# get user info
	AuthDiscord:AuthDiscordWebUser = await authDiscordWebUser(cls, WebRequest)
	if not AuthDiscord.found:
		return await apiMissingAuthorisation(cls, WebRequest)

	# get member
	CheckMember:discord.Member = Guild.get_member(int(AuthDiscord.User.user_id))
	if not CheckMember:
		return await apiDiscordMemberNotFound(cls, WebRequest, guild_id=guild_id, user_id=AuthDiscord.User.user_id)

	# check permissions
	if not (CheckMember.guild_permissions.administrator or CheckMember.guild_permissions.manage_guild):
		return await apiDiscordMissingPermission(cls, WebRequest, guild_id=guild_id, user_id=AuthDiscord.User.user_id)

	# get links
	link_res:List[DiscordWhitelistedLink] = await getDiscordServerWhitelistedLinks(PhaazeDiscord, guild_id=guild_id, link_id=link_id)

	if not link_res:
		return await apiDiscordWhitelistedLinkNotExists(cls, WebRequest, link_id=link_id)

	LinkToDelete:DiscordWhitelistedLink = link_res.pop(0)

	cls.BASE.PhaazeDB.deleteQuery("""
		DELETE FROM `discord_blacklist_whitelistlink` WHERE `guild_id` = %s AND `id` = %s""",
		(LinkToDelete.guild_id, LinkToDelete.link_id)
	)

	cls.BASE.Logger.debug(f"(API/Discord) Linkwhitelist: {guild_id=} deleted {link_id=}", require="discord:configs")
	return cls.response(
		text=json.dumps(dict(msg=f"Linkwhitelist: Deleted entry", deleted=LinkToDelete.link, status=200)),
		content_type="application/json",
		status=200
	)
