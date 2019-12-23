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
from Utils.Classes.undefined import UNDEFINED
from Utils.dbutils import validateDBInput
from Platforms.Discord.utils import getDiscordRoleFromString, getDiscordServerAssignRoles
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
	apiDiscordAssignRoleExists,
	apiDiscordAssignRoleNotExists
)

async def apiDiscordAssignrolesEdit(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
		Default url: /api/discord/assignroles/edit
	"""
	Data:WebRequestContent = WebRequestContent(WebRequest)
	await Data.load()

	# get required stuff
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

	# check if exists
	res_assignroles:list = await getDiscordServerAssignRoles(PhaazeDiscord, guild_id, assignrole_id=assignrole_id)

	if not res_assignroles:
		return await apiDiscordAssignRoleNotExists(cls, WebRequest)

	AssignRoleToEdit:DiscordAssignRole = res_assignroles.pop(0)

	# check all update values
	db_update:dict = dict()
	update:dict = dict()

	value:str = Data.getStr("role_id", UNDEFINED, must_be_digit=True)
	if value != UNDEFINED:
		AssignRole:discord.Role = getDiscordRoleFromString(cls, Guild, value)
		if not AssignRole:
			return await apiMissingData(cls, WebRequest, msg=f"Could not find any role matching '{value}'")

		if AssignRole > Guild.me.top_role:
			return await apiWrongData(cls, WebRequest, msg=f"The Role `{AssignRole.name}` is to high")

		db_update["role_id"] = validateDBInput(str, value)
		update["role_id"] = value

	value:str = Data.getStr("trigger", "").lower().split(" ")[0]
	if value:
		# try to get command with this trigger
		check_double_trigger:list = await getDiscordServerAssignRoles(cls.Web.BASE.Discord, guild_id, trigger=value)
		if check_double_trigger:
			AssignRoleToCheck:DiscordAssignRole = check_double_trigger.pop(0)
			# tryed to set a trigger twice
			if str(AssignRoleToEdit.assignrole_id) != str(AssignRoleToCheck.assignrole_id):
				return await apiDiscordAssignRoleExists(cls, WebRequest, trigger=value)

		db_update["trigger"] = validateDBInput(str, value)
		update["trigger"] = value

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

	if not update:
		return await apiWrongData(cls, WebRequest, msg=f"No changes, please add at least one")

	cls.Web.BASE.PhaazeDB.updateQuery(
		table = "discord_assignrole",
		content = db_update,
		where = "`discord_assignrole`.`guild_id` = %s AND `discord_assignrole`.`id` = %s",
		where_values = (AssignRoleToEdit.guild_id, AssignRoleToEdit.assignrole_id)
	)

	cls.Web.BASE.Logger.debug(f"(API/Discord) Created new assign role: S:{guild_id} T:{assignrole_id} N:{str(update)}", require="discord:role")

	return cls.response(
		text=json.dumps( dict(msg="assign role successfull updated", changes=update, status=200) ),
		content_type="application/json",
		status=200
	)
