from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex
	from Platforms.Discord.main_discord import PhaazebotDiscord

import json
import discord
from aiohttp.web import Response, Request
from Utils.Classes.webrequestcontent import WebRequestContent
from Utils.Classes.discordwebuserinfo import DiscordWebUserInfo
from Utils.Classes.discordassignrole import DiscordAssignRole
from Platforms.Discord.utils import getDiscordServerAssignRoles
from Platforms.Web.Processing.Api.errors import apiMissingAuthorisation, apiMissingData
from Platforms.Web.Processing.Api.Discord.errors import (
	apiDiscordGuildUnknown,
	apiDiscordMemberNotFound,
	apiDiscordMissingPermission
)
from .errors import apiDiscordAssignRoleNotExists

async def apiDiscordAssignrolesDelete(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
		Default url: /api/discord/assignroles/delete
	"""
	Data:WebRequestContent = WebRequestContent(WebRequest)
	await Data.load()

	# get required vars
	guild_id:str = Data.getStr("guild_id", "", must_be_digit=True)
	assignrole_id:str = Data.getStr("assignrole_id", "", must_be_digit=True)

	# checks
	if not guild_id:
		return await apiMissingData(cls, WebRequest, msg="missing or invalid 'guild_id'")

	if not assignrole_id:
		return await apiMissingData(cls, WebRequest, msg="missing or invalid 'assignrole_id'")

	PhaazeDiscord:"PhaazebotDiscord" = cls.Web.BASE.Discord
	Guild:discord.Guild = discord.utils.get(PhaazeDiscord.guilds, id=int(guild_id))
	if not Guild:
		return await apiDiscordGuildUnknown(cls, WebRequest)

	# get assign roles
	res_assignroles:list = await getDiscordServerAssignRoles(cls.Web.BASE.Discord, guild_id, assignrole_id=assignrole_id)

	if not res_assignroles:
		return await apiDiscordAssignRoleNotExists(cls, WebRequest, assignrole_id=assignrole_id)

	AssignRoleToDelete:DiscordAssignRole = res_assignroles.pop(0)

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

	cls.Web.BASE.PhaazeDB.deleteQuery("""
		DELETE FROM `discord_assignrole`
		WHERE `discord_assignrole`.`guild_id` = %s
			AND `discord_assignrole`.`id` = %s""",
		(AssignRoleToDelete.guild_id, AssignRoleToDelete.assignrole_id)
	)

	cls.Web.BASE.Logger.debug(f"(API/Discord) Deleted command: S:{AssignRoleToDelete.guild_id} I:{AssignRoleToDelete.assignrole_id}", require="discord:role")

	return cls.response(
		text=json.dumps( dict(msg="assignrole successfull deleted", assignrole_id=AssignRoleToDelete.assignrole_id, status=200) ),
		content_type="application/json",
		status=200
	)
