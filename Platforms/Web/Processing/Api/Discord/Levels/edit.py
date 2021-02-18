from typing import TYPE_CHECKING, Coroutine
if TYPE_CHECKING:
	from Platforms.Discord.main_discord import PhaazebotDiscord
	from Platforms.Web.main_web import PhaazebotWeb

import json
import asyncio
import discord
from aiohttp.web import Response
from Utils.Classes.discordserversettings import DiscordServerSettings
from Utils.Classes.storagetransformer import StorageTransformer
from Utils.Classes.authdiscordwebuser import AuthDiscordWebUser
from Utils.Classes.extendedrequest import ExtendedRequest
from Utils.Classes.webrequestcontent import WebRequestContent
from Utils.Classes.discorduserstats import DiscordUserStats
from Utils.Classes.undefined import UNDEFINED
from Platforms.Discord.db import getDiscordServerUsers, getDiscordSeverSettings
from Platforms.Web.utils import authDiscordWebUser
from Platforms.Discord.logging import loggingOnLevelEdit

async def apiDiscordLevelsEdit(cls:"PhaazebotWeb", WebRequest:ExtendedRequest) -> Response:
	"""
	Default url: /api/discord/levels/edit
	"""
	Data:WebRequestContent = WebRequestContent(WebRequest)
	await Data.load()

	# get required stuff
	Edit:StorageTransformer = StorageTransformer()
	Edit["guild_id"] = Data.getStr("guild_id", "", must_be_digit=True)
	Edit["member_id"] = Data.getStr("member_id", "", must_be_digit=True)

	# checks
	if not Edit["guild_id"]:
		return await cls.Tree.Api.errors.apiMissingData(cls, WebRequest, msg="missing or invalid 'guild_id'")

	if not Edit["member_id"]:
		return await cls.Tree.Api.errors.apiMissingData(cls, WebRequest, msg="missing or invalid 'member_id'")

	PhaazeDiscord:"PhaazebotDiscord" = cls.BASE.Discord
	Guild:discord.Guild = discord.utils.get(PhaazeDiscord.guilds, id=int(Edit["guild_id"]))
	if not Guild:
		return await cls.Tree.Api.Discord.errors.apiDiscordGuildUnknown(cls, WebRequest)

	# get user info
	AuthDiscord:AuthDiscordWebUser = await authDiscordWebUser(cls, WebRequest)
	if not AuthDiscord.found:
		return await cls.Tree.Api.Discord.errors.apiMissingAuthorisation(cls, WebRequest)

	# get member
	CheckMember:discord.Member = Guild.get_member(int(AuthDiscord.User.user_id))
	if not CheckMember:
		return await cls.Tree.Api.Discord.errors.apiDiscordMemberNotFound(cls, WebRequest, guild_id=Edit["guild_id"], user_id=AuthDiscord.User.user_id)

	# check permissions
	# to edit configs, at least moderator rights are needed, (there can be options that require server only duh)
	if not (CheckMember.guild_permissions.administrator or CheckMember.guild_permissions.manage_guild):
		return await cls.Tree.Api.Discord.errors.apiDiscordMissingPermission(cls, WebRequest, guild_id=Edit["guild_id"], user_id=AuthDiscord.User.user_id)

	# get level user
	res_level:list = await getDiscordServerUsers(PhaazeDiscord, guild_id=Edit["guild_id"], member_id=Edit["member_id"])
	if not res_level:
		return await cls.Tree.Api.Discord.errors.apiDiscordGuildUnknown(cls, WebRequest, msg="Could not find a level for this user")
	CurrentLevelUser:DiscordUserStats = res_level.pop(0)

	# check all update values
	update:dict = dict()

	# currency
	Edit["currency"] = Data.getInt("currency", UNDEFINED, min_x=0)
	if Edit["currency"] != UNDEFINED:
		update["currency"] = Edit["currency"]

	# exp
	Edit["exp"] = Data.getInt("exp", UNDEFINED, min_x=0)
	if Edit["exp"] != UNDEFINED:
		update["exp"] = Edit["exp"]

		if Edit["exp"] != 0:
			update["edited"] = 1
		else:
			update["edited"] = 0

	# on_server
	Edit["on_server"] = Data.getBool("on_server", UNDEFINED)
	if Edit["on_server"] != UNDEFINED:
		if not Guild.owner == CheckMember:
			return await cls.Tree.Api.Discord.errors.apiDiscordMissingPermission(cls, WebRequest, guild_id=Edit["guild_id"], user_id=AuthDiscord.User.user_id, msg="changing 'on_server' require server owner")

		update["on_server"] = Edit["on_server"]

	if not update:
		return await cls.Tree.Api.errors.apiMissingData(cls, WebRequest, msg="No changes, please add at least one")

	cls.BASE.PhaazeDB.updateQuery(
		table="discord_user",
		content=update,
		where="`discord_user`.`guild_id` = %s AND `discord_user`.`member_id` = %s",
		where_values=(CurrentLevelUser.guild_id, CurrentLevelUser.member_id)
	)

	# logging
	GuildSettings:DiscordServerSettings = await getDiscordSeverSettings(PhaazeDiscord, Edit["guild_id"], prevent_new=True)
	log_coro:Coroutine = loggingOnLevelEdit(PhaazeDiscord, GuildSettings, Editor=CheckMember, changed_member_id=CurrentLevelUser.member_id, changes=update)
	asyncio.ensure_future(log_coro, loop=cls.BASE.DiscordLoop)

	cls.BASE.Logger.debug(f"(API/Discord) Level: {Edit['guild_id']=} {Edit['member_id']=} updated", require="discord:levels")
	return cls.response(
		text=json.dumps(dict(msg="Level: Updated", changes=update, status=200)),
		content_type="application/json",
		status=200
	)
