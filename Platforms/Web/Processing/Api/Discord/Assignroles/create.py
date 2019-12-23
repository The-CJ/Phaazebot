from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex
	from Platforms.Discord.main_discord import PhaazebotDiscord

import json
import discord
from aiohttp.web import Response, Request
from Utils.Classes.webrequestcontent import WebRequestContent
from Utils.Classes.discordwebuserinfo import DiscordWebUserInfo
from Platforms.Discord.utils import getDiscordRoleFromString
from Platforms.Web.Processing.Api.errors import (
	apiMissingData,
	apiMissingAuthorisation,
	apiWrongData
)
from Platforms.Web.Processing.Api.Discord.errors import (
	apiDiscordGuildUnknown,
	apiDiscordMemberNotFound,
	apiDiscordMissingPermission,
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

	# check if already exists and limits
	res:list = cls.Web.BASE.PhaazeDB.selectQuery("""
		SELECT
			COUNT(*) AS `all`,
			SUM(
				CASE WHEN `discord_assignrole`.`role_id` = %s OR LOWER(`discord_assignrole`.`trigger`) = LOWER(%s)
				THEN 1 ELSE 0 END
			) AS `match`
		FROM `discord_assignrole`
		WHERE `discord_assignrole`.`guild_id` = %s""",
		( role_id, trigger, guild_id )
	)

	if res[0]["match"]:
		return await apiDiscordAssignRoleExists(cls, WebRequest, role_id=role_id, trigger=trigger)

	if res[0]["all"] >= cls.Web.BASE.Limit.DISCORD_ASSIGNROLE_AMOUNT:
		return await apiDiscordAssignRoleLimit(cls, WebRequest)

	# get server role
	AssignRole:discord.Role = getDiscordRoleFromString(cls, Guild, role_id)
	if not AssignRole:
		return await apiMissingData(cls, WebRequest, msg=f"Could not find any role matching '{role_id}'")

	if AssignRole > Guild.me.top_role:
		return await apiWrongData(cls, WebRequest, msg=f"The Role `{AssignRole.name}` is to high")

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

	new_assign_role:dict = dict(
		guild_id = guild_id,
		trigger = trigger,
		role_id = role_id
	)

	cls.Web.BASE.PhaazeDB.insertQuery(table="discord_assignrole", content=new_assign_role)

	cls.Web.BASE.Logger.debug(f"(API/Discord) Created new assign role: S:{guild_id} T:'{trigger}' N:{str(new_assign_role)}", require="discord:role")

	return cls.response(
		text=json.dumps( dict(msg="new assign role successfull created", trigger=trigger, status=200) ),
		content_type="application/json",
		status=200
	)
