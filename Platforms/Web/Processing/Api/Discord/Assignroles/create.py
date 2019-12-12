from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex
	from Platforms.Discord.main_discord import PhaazebotDiscord

import json
import discord
from aiohttp.web import Response, Request
from Utils.Classes.webrequestcontent import WebRequestContent
from Platforms.Web.Processing.Api.errors import missingData, apiMissingAuthorisation
from Utils.Classes.discorduserinfo import DiscordUserInfo
from Platforms.Web.Processing.Api.Discord.errors import (
	apiDiscordGuildUnknown,
	apiDiscordMemberNotFound,
	apiDiscordMissingPermission,
	apiDiscordAssignRoleExists,
	apiDiscordAssignRoleLimit
)

async def apiDiscordAssignrolesCreate(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
		Default url: /api/discord/commands/create
	"""
	Data:WebRequestContent = WebRequestContent(WebRequest)
	await Data.load()

	# get required stuff
	guild_id:str = Data.getStr("guild_id", "", must_be_digit=True)
	role_id:str = Data.getStr("role_id", "", must_be_digit=True)
	trigger:str = Data.getStr("trigger", "").split(" ")[0] # only take the first argument trigger, since everything else can't be typed in a channel

	# checks
	if not guild_id:
		return await missingData(cls, WebRequest, msg="missing or invalid 'guild_id'")

	if not role_id:
		return await missingData(cls, WebRequest, msg="missing or invalid 'role_id'")

	if not trigger:
		return await missingData(cls, WebRequest, msg="missing or invalid 'trigger'")

	PhaazeDiscord:"PhaazebotDiscord" = cls.Web.BASE.Discord
	Guild:discord.Guild = discord.utils.get(PhaazeDiscord.guilds, id=int(guild_id))
	if not Guild:
		return await apiDiscordGuildUnknown(cls, WebRequest)

	# check if already exists and limits
	res:list = cls.Web.BASE.PhaazeDB.selectQuery("""
		SELECT
			COUNT(*) AS `all`,
			SUM(
				CASE WHEN `discord_giverole`.`role_id` = %s OR LOWER(`discord_giverole`.`trigger`) = LOWER(%s)
				THEN 1 ELSE 0 END
			) AS `match`
		FROM `discord_giverole`
		WHERE `discord_giverole`.`guild_id` = %s""",
		( role_id, trigger, guild_id )
	)

	if res[0]["match"]:
		return await apiDiscordAssignRoleExists(cls, WebRequest, role_id=role_id, trigger=trigger)

	if res[0]["all"] >= cls.Web.BASE.Limit.DISCORD_ADDROLE_AMOUNT:
		return await apiDiscordAssignRoleLimit(cls, WebRequest)

	# get user info
	DiscordUser:DiscordUserInfo = await cls.getDiscordUserInfo(WebRequest)
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

	cls.Web.BASE.PhaazeDB.insertQuery(table="discord_giverole", content=new_assign_role)

	cls.Web.BASE.Logger.debug(f"(API/Discord) Created new assign role: S:{guild_id} T:{trigger} N:{str(new_assign_role)}", require="discord:role")

	return cls.response(
		text=json.dumps( dict(msg="new assign role successfull created", trigger=trigger, status=200) ),
		content_type="application/json",
		status=200
	)
