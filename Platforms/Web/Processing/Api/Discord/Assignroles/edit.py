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
from Utils.Classes.discordassignrole import DiscordAssignRole
from Utils.Classes.extendedrequest import ExtendedRequest
from Utils.Classes.undefined import UNDEFINED
from Platforms.Web.utils import authDiscordWebUser
from Platforms.Discord.db import getDiscordServerAssignRoles, getDiscordSeverSettings
from Platforms.Discord.utils import getDiscordRoleFromString
from Platforms.Discord.logging import loggingOnAssignroleEdit

async def apiDiscordAssignrolesEdit(cls:"PhaazebotWeb", WebRequest:ExtendedRequest) -> Response:
	"""
	Default url: /api/discord/assignroles/edit
	"""
	Data:WebRequestContent = WebRequestContent(WebRequest)
	await Data.load()

	# get required stuff
	Edit:StorageTransformer = StorageTransformer()
	Edit["assignrole_id"] = Data.getInt("assignrole_id", "", min_x=1)
	Edit["guild_id"] = Data.getStr("guild_id", "", must_be_digit=True)

	# checks
	if not Edit["assignrole_id"]:
		return await cls.Tree.Api.errors.apiMissingData(cls, WebRequest, msg="missing or invalid 'assignrole_id'")

	if not Edit["guild_id"]:
		return await cls.Tree.Api.errors.apiMissingData(cls, WebRequest, msg="missing or invalid 'guild_id'")

	PhaazeDiscord:"PhaazebotDiscord" = cls.BASE.Discord
	Guild:discord.Guild = discord.utils.get(PhaazeDiscord.guilds, id=int(Edit["guild_id"]))
	if not Guild:
		return await cls.Tree.Api.Discord.errors.apiDiscordGuildUnknown(cls, WebRequest)

	# check if exists
	res_assignroles:list = await getDiscordServerAssignRoles(PhaazeDiscord, guild_id=Edit["guild_id"], assignrole_id=Edit["assignrole_id"])

	if not res_assignroles:
		return await cls.Tree.Api.Discord.errors.apiDiscordAssignRoleNotExists(cls, WebRequest, assignrole_id=Edit["assignrole_id"])

	AssignRoleToEdit:DiscordAssignRole = res_assignroles.pop(0)

	# check all update values
	update:dict = dict()

	Edit["role_id"] = Data.getStr("role_id", UNDEFINED, must_be_digit=True)
	if Edit["role_id"] != UNDEFINED:
		AssignRole:discord.Role = getDiscordRoleFromString(PhaazeDiscord, Guild, Edit["role_id"])
		if not AssignRole:
			return await cls.Tree.Api.Discord.errors.apiDiscordRoleNotFound(cls, WebRequest, guild_name=Guild.name, guild_id=Guild.id, role_id=Edit["role_id"])

		if AssignRole > Guild.me.top_role or AssignRole == Guild.default_role:
			return await cls.Tree.Api.errors.apiWrongData(cls, WebRequest, msg=f"The Role `{AssignRole.name}` is to high")

		update["role_id"] = Edit["role_id"]

	Edit["trigger"] = Data.getStr("trigger", "").lower().split(" ")[0]
	if Edit["trigger"]:
		# try to get command with this trigger
		check_double_trigger:list = await getDiscordServerAssignRoles(cls.BASE.Discord, guild_id=Edit["guild_id"], trigger=Edit["trigger"])
		if check_double_trigger:
			AssignRoleToCheck:DiscordAssignRole = check_double_trigger.pop(0)
			# tried to set a trigger twice
			if str(AssignRoleToEdit.assignrole_id) != str(AssignRoleToCheck.assignrole_id):
				return await cls.Tree.Api.Discord.Assignroles.errors.apiDiscordAssignRoleExists(cls, WebRequest, trigger=Edit["trigger"])

		update["trigger"] = Edit["trigger"]

	# get user info
	AuthDiscord:AuthDiscordWebUser = await authDiscordWebUser(cls, WebRequest)
	if not AuthDiscord.found:
		return await cls.Tree.Api.errors.apiMissingAuthorisation(cls, WebRequest)

	# get member
	CheckMember:discord.Member = Guild.get_member(int(AuthDiscord.User.user_id))
	if not CheckMember:
		return await cls.Tree.Api.Discord.errors.apiDiscordMemberNotFound(cls, WebRequest, guild_id=Edit["guild_id"], user_id=AuthDiscord.User.user_id)

	# check permissions
	if not (CheckMember.guild_permissions.administrator or CheckMember.guild_permissions.manage_guild):
		return await cls.Tree.Api.Discord.errors.apiDiscordMissingPermission(cls, WebRequest, guild_id=Edit["guild_id"], user_id=AuthDiscord.User.user_id)

	if not update:
		return await cls.Tree.Api.errors.apiWrongData(cls, WebRequest, msg=f"No changes, please add at least one")

	cls.BASE.PhaazeDB.updateQuery(
		table="discord_assignrole",
		content=update,
		where="`discord_assignrole`.`guild_id` = %s AND `discord_assignrole`.`id` = %s",
		where_values=(AssignRoleToEdit.guild_id, AssignRoleToEdit.assignrole_id)
	)

	# logging
	GuildSettings:DiscordServerSettings = await getDiscordSeverSettings(PhaazeDiscord, Edit["guild_id"], prevent_new=True)
	log_coro:Coroutine = loggingOnAssignroleEdit(PhaazeDiscord, GuildSettings,
		Editor=CheckMember,
		assign_role_trigger=AssignRoleToEdit.trigger,
		changes=update
	)
	asyncio.ensure_future(log_coro, loop=cls.BASE.DiscordLoop)

	cls.BASE.Logger.debug(f"(API/Discord) Assignrole: {Edit['guild_id']=} edited {Edit['assignrole_id']=}", require="discord:role")
	return cls.response(
		text=json.dumps(dict(msg="Assignrole: Edited entry", changes=update, status=200)),
		content_type="application/json",
		status=200
	)
