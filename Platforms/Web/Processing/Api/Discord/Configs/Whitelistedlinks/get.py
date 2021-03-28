from typing import TYPE_CHECKING, List, Dict, Any
if TYPE_CHECKING:
	from Platforms.Discord.main_discord import PhaazebotDiscord
	from Platforms.Web.main_web import PhaazebotWeb

import json
import discord
from aiohttp.web import Response
from Utils.Classes.discordwhitelistedlink import DiscordWhitelistedLink
from Utils.Classes.storagetransformer import StorageTransformer
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

DEFAULT_LIMIT:int = 50
MAX_LIMIT:int = 100

async def apiDiscordConfigsWhitelistedLinkGet(cls:"PhaazebotWeb", WebRequest:ExtendedRequest) -> Response:
	"""
	Default url: /api/discord/configs/whitelistedlinks/get
	"""
	Data:WebRequestContent = WebRequestContent(WebRequest)
	await Data.load()

	# get required stuff
	Search:StorageTransformer = StorageTransformer()
	Search["guild_id"] = Data.getStr("guild_id", UNDEFINED, must_be_digit=True)
	Search["link_id"] = Data.getStr("link_id", UNDEFINED, must_be_digit=True)
	Search["link"] = Data.getStr("link", UNDEFINED, len_min=1, len_max=128)
	Search["limit"] = Data.getInt("limit", DEFAULT_LIMIT, min_x=1, max_x=MAX_LIMIT)
	Search["offset"] = Data.getInt("offset", 0, min_x=0)

	# checks
	if not Search["guild_id"]:
		return await apiMissingData(cls, WebRequest, msg="missing or invalid 'guild_id'")

	PhaazeDiscord:"PhaazebotDiscord" = cls.BASE.Discord
	Guild:discord.Guild = discord.utils.get(PhaazeDiscord.guilds, id=int(Search["guild_id"]))
	if not Guild:
		return await apiDiscordGuildUnknown(cls, WebRequest)

	# get user info
	AuthDiscord:AuthDiscordWebUser = await authDiscordWebUser(cls, WebRequest)
	if not AuthDiscord.found:
		return await apiMissingAuthorisation(cls, WebRequest)

	# get member
	CheckMember:discord.Member = Guild.get_member(int(AuthDiscord.User.user_id))
	if not CheckMember:
		return await apiDiscordMemberNotFound(cls, WebRequest, guild_id=Search["guild_id"], user_id=AuthDiscord.User.user_id)

	# check permissions
	if not (CheckMember.guild_permissions.administrator or CheckMember.guild_permissions.manage_guild):
		return await apiDiscordMissingPermission(cls, WebRequest, guild_id=Search["guild_id"], user_id=AuthDiscord.User.user_id)

	link_res:List[DiscordWhitelistedLink] = await getDiscordServerWhitelistedLinks(PhaazeDiscord)

	result:Dict[str, Any] = dict(
		result=[Link.toJSON() for Link in link_res],
		limit=Search["limit"],
		offset=Search["offset"],
		total=await getDiscordServerWhitelistedLinks(PhaazeDiscord, count_mode=True, **Search.getAllTransform()),
		status=200
	)

	return cls.response(
		text=json.dumps(result),
		content_type="application/json",
		status=200
	)
