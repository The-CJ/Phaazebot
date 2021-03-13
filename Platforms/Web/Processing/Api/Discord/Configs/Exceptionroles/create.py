from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Discord.main_discord import PhaazebotDiscord
	from Platforms.Web.main_web import PhaazebotWeb

import json
import discord
from aiohttp.web import Response
from Utils.Classes.storagetransformer import StorageTransformer
from Utils.Classes.authdiscordwebuser import AuthDiscordWebUser
from Utils.Classes.webrequestcontent import WebRequestContent
from Utils.Classes.extendedrequest import ExtendedRequest
from Utils.Classes.undefined import UNDEFINED
from Platforms.Discord.utils import getDiscordRoleFromString
from Platforms.Web.utils import authDiscordWebUser

async def apiDiscordConfigsExceptionRolesCreate(cls:"PhaazebotWeb", WebRequest:ExtendedRequest) -> Response:
	"""
	Default url: /api/discord/configs/exceptionroles/create
	"""
	Data:WebRequestContent = WebRequestContent(WebRequest)
	await Data.load()

	# get required stuff
	Create:StorageTransformer = StorageTransformer()
	Create["guild_id"] = Data.getStr("guild_id", UNDEFINED, must_be_digit=True)
	Create["role_id"] = Data.getStr("role_id", UNDEFINED, len_max=512)

	# checks
	if not Create["guild_id"]:
		return await cls.Tree.Api.errors.apiMissingData(cls, WebRequest, msg="missing or invalid 'guild_id'")

	if not Create["role_id"]:
		return await cls.Tree.Api.errors.apiMissingData(cls, WebRequest, msg="missing or invalid 'role_id'")

	PhaazeDiscord:"PhaazebotDiscord" = cls.BASE.Discord
	Guild:discord.Guild = discord.utils.get(PhaazeDiscord.guilds, id=int(Create["guild_id"]))
	if not Guild:
		return await cls.Tree.Api.Discord.errors.apiDiscordGuildUnknown(cls, WebRequest)

	# get user info
	AuthDiscord:AuthDiscordWebUser = await authDiscordWebUser(cls, WebRequest)
	if not AuthDiscord.found:
		return await cls.Tree.Api.errors.apiMissingAuthorisation(cls, WebRequest)

	# get member
	CheckMember:discord.Member = Guild.get_member(int(AuthDiscord.User.user_id))
	if not CheckMember:
		return await cls.Tree.Api.Discord.errors.apiDiscordMemberNotFound(cls, WebRequest, guild_id=Create["guild_id"], user_id=AuthDiscord.User.user_id)

	# check permissions
	if not (CheckMember.guild_permissions.administrator or CheckMember.guild_permissions.manage_guild):
		return await cls.Tree.Api.Discord.errors.apiDiscordMissingPermission(cls, WebRequest, guild_id=Create["guild_id"], user_id=AuthDiscord.User.user_id)

	ActionRole:discord.Role = getDiscordRoleFromString(PhaazeDiscord, Guild, Create["role_id"])
	if not ActionRole:
		return await cls.Tree.Api.Discord.errors.apiDiscordRoleNotFound(cls, WebRequest, guild_id=Guild.id, guild_name=Guild.name, role_id=Create["role_id"])

	# check if already exists
	res:list = cls.BASE.PhaazeDB.selectQuery("""
		SELECT COUNT(*) AS `match`
		FROM `discord_blacklist_whitelistrole`
		WHERE `discord_blacklist_whitelistrole`.`guild_id` = %s
			AND `discord_blacklist_whitelistrole`.`role_id` = %s""",
		(Create["guild_id"], Create["role_id"])
	)

	if res[0]["match"]:
		return await cls.Tree.Api.Discord.Configs.Exceptionroles.errors.apiDiscordExceptionRoleExists(cls, WebRequest, role_id=Create["role_id"], role_name=ActionRole.name)

	cls.BASE.PhaazeDB.insertQuery(
		table="discord_blacklist_whitelistrole",
		content={
			"guild_id": Create["guild_id"],
			"role_id": Create["role_id"]
		}
	)

	cls.BASE.Logger.debug(f"(API/Discord) Exceptionrole: {Create['guild_id']=} added: {Create['role_id']=}", require="discord:configs")
	return cls.response(
		text=json.dumps(dict(msg="Exceptionrole: Added new entry", entry=Create["role_id"], status=200)),
		content_type="application/json",
		status=200
	)
