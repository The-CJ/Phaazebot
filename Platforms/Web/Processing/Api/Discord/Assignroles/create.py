from typing import TYPE_CHECKING, Coroutine
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex
	from Platforms.Discord.main_discord import PhaazebotDiscord

import json
import asyncio
import discord
from aiohttp.web import Response, Request
from Utils.Classes.discordserversettings import DiscordServerSettings
from Utils.Classes.discordwebuserinfo import DiscordWebUserInfo
from Utils.Classes.webrequestcontent import WebRequestContent
from Platforms.Discord.db import getDiscordSeverSettings
from Platforms.Discord.utils import getDiscordRoleFromString
from Platforms.Discord.logging import loggingOnAssignroleCreate
from Platforms.Web.Processing.Api.errors import (
	apiMissingData,
	apiMissingAuthorisation,
	apiWrongData
)
from Platforms.Web.Processing.Api.Discord.errors import (
	apiDiscordGuildUnknown,
	apiDiscordMemberNotFound,
	apiDiscordMissingPermission,
	apiDiscordRoleNotFound
)
from .errors import (
	apiDiscordAssignRoleLimit,
	apiDiscordAssignRoleExists
)

async def apiDiscordAssignrolesCreate(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
	Default url: /api/discord/assignroles/create
	"""
	Data:WebRequestContent = WebRequestContent(WebRequest)
	await Data.load()

	# get required stuff
	guild_id:str = Data.getStr("guild_id", "", must_be_digit=True)
	role_id:str = Data.getStr("role_id", "", must_be_digit=True)
	trigger:str = Data.getStr("trigger", "").lower().split(" ")[0] # only take the first argument trigger, since everything else can't be typed in a channel

	# checks
	if not guild_id:
		return await apiMissingData(cls, WebRequest, msg="missing or invalid 'guild_id'")

	if not role_id:
		return await apiMissingData(cls, WebRequest, msg="missing or invalid 'role_id'")

	if not trigger:
		return await apiMissingData(cls, WebRequest, msg="missing or invalid 'trigger'")

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

	# get server role
	AssignRole:discord.Role = getDiscordRoleFromString(cls, Guild, role_id)
	if not AssignRole:
		return await apiDiscordRoleNotFound(cls, WebRequest, guild_id=Guild.name, guild_name=Guild.name, role_id=role_id)

	if AssignRole >= Guild.me.top_role or AssignRole == Guild.default_role:
		return await apiWrongData(cls, WebRequest, msg=f"The Role `{AssignRole.name}` is to high")

	# check if already exists and limits
	res:list = cls.Web.BASE.PhaazeDB.selectQuery("""
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
		( role_id, trigger, guild_id )
	)

	if res[0]["match_role_id"]:
		return await apiDiscordAssignRoleExists(cls, WebRequest, role_id=role_id, role_name=AssignRole.name)

	if res[0]["match_trigger"]:
		return await apiDiscordAssignRoleExists(cls, WebRequest, trigger=trigger)

	if res[0]["all"] >= cls.Web.BASE.Limit.discord_assignrole_amount:
		return await apiDiscordAssignRoleLimit(cls, WebRequest, limit=cls.Web.BASE.Limit.discord_assignrole_amount)

	cls.Web.BASE.PhaazeDB.insertQuery(
		table="discord_assignrole",
		content={
			"guild_id": guild_id,
			"trigger": trigger,
			"role_id": str(AssignRole.id)
		}
	)

	# logging
	GuildSettings:DiscordServerSettings = await getDiscordSeverSettings(PhaazeDiscord, guild_id, prevent_new=True)
	log_coro:Coroutine = loggingOnAssignroleCreate(PhaazeDiscord, GuildSettings,
		Creator=CheckMember,
		assign_role_id=role_id,
		trigger=trigger
	)
	asyncio.ensure_future(log_coro, loop=cls.Web.BASE.DiscordLoop)

	cls.Web.BASE.Logger.debug(f"(API/Discord) Assignroles: {guild_id=} added: {trigger=}", require="discord:configs")
	return cls.response(
		text=json.dumps( dict(msg="Assignroles: Added new entry", entry=trigger, status=200) ),
		content_type="application/json",
		status=200
	)
