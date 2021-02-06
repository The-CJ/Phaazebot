from typing import TYPE_CHECKING, Coroutine
if TYPE_CHECKING:
	from Platforms.Web.main_web import PhaazebotWeb
	from Platforms.Discord.main_discord import PhaazebotDiscord

import json
import asyncio
import discord
from aiohttp.web import Response
from Utils.Classes.discordserversettings import DiscordServerSettings
from Utils.Classes.authdiscordwebuser import AuthDiscordWebUser
from Utils.Classes.webrequestcontent import WebRequestContent
from Utils.Classes.discordassignrole import DiscordAssignRole
from Utils.Classes.extendedrequest import ExtendedRequest
from Platforms.Web.utils import authDiscordWebUser
from Platforms.Discord.db import getDiscordServerAssignRoles, getDiscordSeverSettings
from Platforms.Discord.logging import loggingOnAssignroleDelete
from Platforms.Web.Processing.Api.errors import apiMissingAuthorisation, apiMissingData

async def apiDiscordAssignrolesDelete(cls:"PhaazebotWeb", WebRequest:ExtendedRequest) -> Response:
	"""
	Default url: /api/discord/assignroles/delete
	"""
	Data:WebRequestContent = WebRequestContent(WebRequest)
	await Data.load()

	# get required vars
	guild_id:str = Data.getStr("guild_id", "", must_be_digit=True)
	assignrole_id:str = Data.getStr("assignrole_id", "", must_be_digit=True)
	role_id:str = Data.getStr("role_id", "", must_be_digit=True)

	# checks
	if not guild_id:
		return await apiMissingData(cls, WebRequest, msg="missing or invalid 'guild_id'")

	if (not assignrole_id) and (not role_id):
		return await apiMissingData(cls, WebRequest, msg="missing or invalid 'assignrole_id' or 'role_id'")

	PhaazeDiscord:"PhaazebotDiscord" = cls.BASE.Discord
	Guild:discord.Guild = discord.utils.get(PhaazeDiscord.guilds, id=int(guild_id))
	if not Guild:
		return await cls.Tree.Api.Discord.errors.apiDiscordGuildUnknown(cls, WebRequest)

	# get user info
	AuthDiscord:AuthDiscordWebUser = await authDiscordWebUser(cls, WebRequest)
	if not AuthDiscord.found:
		return await apiMissingAuthorisation(cls, WebRequest)

	# get member
	CheckMember:discord.Member = Guild.get_member(int(AuthDiscord.User.user_id))
	if not CheckMember:
		return await cls.Tree.Api.Discord.errors.apiDiscordMemberNotFound(cls, WebRequest, guild_id=guild_id, user_id=AuthDiscord.User.user_id)

	# check permissions
	if not (CheckMember.guild_permissions.administrator or CheckMember.guild_permissions.manage_guild):
		return await cls.Tree.Api.Discord.errors. apiDiscordMissingPermission(cls, WebRequest, guild_id=guild_id, user_id=AuthDiscord.User.user_id)

	# get assign roles
	res_assignroles:list = await getDiscordServerAssignRoles(PhaazeDiscord, guild_id=guild_id, assignrole_id=assignrole_id, role_id=role_id)

	if not res_assignroles:
		return await cls.Tree.Api.Discord.Assignroles.errors.apiDiscordAssignRoleNotExists(cls, WebRequest, role_id=role_id, assignrole_id=assignrole_id)

	AssignRoleToDelete:DiscordAssignRole = res_assignroles.pop(0)

	cls.BASE.PhaazeDB.deleteQuery("""
		DELETE FROM `discord_assignrole` WHERE `guild_id` = %s AND `id` = %s""",
		(AssignRoleToDelete.guild_id, AssignRoleToDelete.assignrole_id)
	)

	# logging
	GuildSettings:DiscordServerSettings = await getDiscordSeverSettings(PhaazeDiscord, guild_id, prevent_new=True)
	log_coro:Coroutine = loggingOnAssignroleDelete(PhaazeDiscord, GuildSettings,
		Deleter=CheckMember,
		assign_role_trigger=AssignRoleToDelete.trigger,
	)
	asyncio.ensure_future(log_coro, loop=cls.BASE.DiscordLoop)

	cls.BASE.Logger.debug(f"(API/Discord) Assignroles: {guild_id=} deleted [{role_id}, {assignrole_id=}]", require="discord:role")
	return cls.response(
		text=json.dumps(dict(msg="Assignroles: Deleted entry", deleted=AssignRoleToDelete.trigger, status=200)),
		content_type="application/json",
		status=200
	)
