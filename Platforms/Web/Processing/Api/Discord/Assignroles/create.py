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
from Utils.Classes.undefined import UNDEFINED
from Platforms.Discord.logging import loggingOnAssignroleCreate
from Platforms.Discord.utils import getDiscordRoleFromString
from Platforms.Discord.db import getDiscordSeverSettings
from Platforms.Web.utils import authDiscordWebUser

async def apiDiscordAssignrolesCreate(cls:"PhaazebotWeb", WebRequest:ExtendedRequest) -> Response:
	"""
	Default url: /api/discord/assignroles/create
	"""
	Data:WebRequestContent = WebRequestContent(WebRequest)
	await Data.load()

	# get required stuff
	Create:StorageTransformer = StorageTransformer()
	Create["guild_id"] = Data.getStr("guild_id", UNDEFINED, must_be_digit=True)
	Create["role_id"] = Data.getStr("role_id", UNDEFINED, must_be_digit=True)
	Create["trigger"] = Data.getStr("trigger", "").lower().split(" ")[0] # only take the first argument trigger, since everything else can't be typed in a channel

	# checks
	if not Create["guild_id"]:
		return await cls.Tree.Api.errors.apiMissingData(cls, WebRequest, msg="missing or invalid 'guild_id'")

	if not Create["role_id"]:
		return await cls.Tree.Api.errors.apiMissingData(cls, WebRequest, msg="missing or invalid 'role_id'")

	if not Create["trigger"]:
		return await cls.Tree.Api.errors.apiMissingData(cls, WebRequest, msg="missing or invalid 'trigger'")

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

	# get server role
	AssignRole:discord.Role = getDiscordRoleFromString(PhaazeDiscord, Guild, Create["role_id"])
	if not AssignRole:
		return await cls.Tree.Api.Discord.errors.apiDiscordRoleNotFound(cls, WebRequest, guild_id=Guild.name, guild_name=Guild.name, role_id=Create["role_id"])

	if AssignRole >= Guild.me.top_role or AssignRole == Guild.default_role:
		return await cls.Tree.errors.piWrongData(cls, WebRequest, msg=f"The Role `{AssignRole.name}` is to high")

	# check if already exists and limits
	res:list = cls.BASE.PhaazeDB.selectQuery("""
		SELECT
			COUNT(*) AS `all`,
			SUM(
				CASE WHEN `discord_assignrole`.`role_id` = %s
				THEN 1 ELSE 0 END
			) AS `match_role_id`,
			SUM(
				CASE WHEN LOWER(`discord_assignrole`.`trigger`) = LOWER(%s)
				THEN 1 ELSE 0 END
			) AS `match_trigger`
		FROM `discord_assignrole`
		WHERE `discord_assignrole`.`guild_id` = %s""",
		(Create["role_id"], Create["trigger"], Create["guild_id"])
	)

	if res[0]["match_role_id"]:
		return await cls.Tree.Api.Discord.errors.apiDiscordAssignRoleExists(cls, WebRequest, role_id=Create["role_id"], role_name=AssignRole.name)

	if res[0]["match_trigger"]:
		return await cls.Tree.Api.Discord.errors.apiDiscordAssignRoleExists(cls, WebRequest, trigger=Create["trigger"])

	if res[0]["all"] >= cls.BASE.Limit.discord_assignrole_amount:
		return await cls.Tree.Api.Discord.errors.apiDiscordAssignRoleLimit(cls, WebRequest, limit=cls.BASE.Limit.discord_assignrole_amount)

	cls.BASE.PhaazeDB.insertQuery(
		table="discord_assignrole",
		content={
			"guild_id": Create["guild_id"],
			"trigger": Create["trigger"],
			"role_id": str(AssignRole.id)
		}
	)

	# logging
	GuildSettings:DiscordServerSettings = await getDiscordSeverSettings(PhaazeDiscord, Create["guild_id"], prevent_new=True)
	log_coro:Coroutine = loggingOnAssignroleCreate(PhaazeDiscord, GuildSettings,
		Creator=CheckMember,
		assign_role_id=Create["role_id"],
		trigger=Create["trigger"]
	)
	asyncio.ensure_future(log_coro, loop=cls.BASE.DiscordLoop)

	cls.BASE.Logger.debug(f"(API/Discord) Assignroles: {Create['guild_id']=} added: {Create['trigger']=}", require="discord:configs")
	return cls.response(
		text=json.dumps(dict(msg="Assignroles: Added new entry", entry=Create["trigger"], status=200)),
		content_type="application/json",
		status=200
	)
