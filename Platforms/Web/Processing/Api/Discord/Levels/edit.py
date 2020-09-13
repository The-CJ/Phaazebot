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
from Utils.Classes.discorduserstats import DiscordUserStats
from Utils.Classes.undefined import UNDEFINED
from Platforms.Discord.db import getDiscordServerUsers, getDiscordSeverSettings
from Platforms.Discord.logging import loggingOnLevelEdit
from Utils.dbutils import validateDBInput
from Platforms.Web.Processing.Api.errors import	apiMissingAuthorisation, apiMissingData
from Platforms.Web.Processing.Api.Discord.errors import (
	apiDiscordGuildUnknown,
	apiDiscordMemberNotFound,
	apiDiscordMissingPermission
)

async def apiDiscordLevelsEdit(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
	Default url: /api/discord/levels/edit
	"""
	Data:WebRequestContent = WebRequestContent(WebRequest)
	await Data.load()

	# get required stuff
	guild_id:str = Data.getStr("guild_id", "", must_be_digit=True)
	member_id:str = Data.getStr("member_id", "", must_be_digit=True)

	# checks
	if not guild_id:
		return await apiMissingData(cls, WebRequest, msg="missing or invalid 'guild_id'")

	if not member_id:
		return await apiMissingData(cls, WebRequest, msg="missing or invalid 'member_id'")

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
	# to edit configs, at least moderator rights are needed, (there can be options that require server only duh)
	if not (CheckMember.guild_permissions.administrator or CheckMember.guild_permissions.manage_guild):
		return await apiDiscordMissingPermission(cls, WebRequest, guild_id=guild_id, user_id=DiscordUser.user_id)

	# get level user
	res_level:list = await getDiscordServerUsers(PhaazeDiscord, guild_id=guild_id, member_id=member_id)
	if not res_level:
		return await apiDiscordGuildUnknown(cls, WebRequest, msg="Could not find a level for this user")
	CurrentLevelUser:DiscordUserStats = res_level.pop(0)

	changes:dict = dict()
	db_changes:dict = dict()

	# get all changed stuff and add changes to list
	# changes is for the user, so return with types, db_changes is with, well... db values
	# e.g.:
	# changes["x"] = true
	# db_changes["x"] = "1"

	# currency
	value:int = Data.getInt("currency", UNDEFINED, min_x=0)
	if value != UNDEFINED:
		db_changes["currency"] = validateDBInput(int, value)
		changes["currency"] = value

	# exp
	value:int = Data.getInt("exp", UNDEFINED, min_x=0)
	if value != UNDEFINED:
		db_changes["exp"] = validateDBInput(int, value)
		changes["exp"] = value

		if value != 0:
			db_changes["edited"] = validateDBInput(bool, True)
			changes["edited"] = True
		else:
			db_changes["edited"] = validateDBInput(bool, False)
			changes["edited"] = False

	# on_server
	value:bool = Data.getBool("on_server", UNDEFINED)
	if value != UNDEFINED:
		if not Guild.owner == CheckMember:
			return await apiDiscordMissingPermission(cls, WebRequest, guild_id=guild_id, user_id=DiscordUser.user_id, msg="changing 'on_server' require server owner")

		db_changes["on_server"] = validateDBInput(bool, value)
		changes["on_server"] = value

	if not db_changes:
		return await apiMissingData(cls, WebRequest, msg="No changes, please add at least one")

	cls.Web.BASE.PhaazeDB.updateQuery(
		table = "discord_user",
		content = db_changes,
		where = "`discord_user`.`guild_id` = %s AND `discord_user`.`member_id` = %s",
		where_values = (CurrentLevelUser.guild_id, CurrentLevelUser.member_id)
	)

	# logging
	GuildSettings:DiscordServerSettings = await getDiscordSeverSettings(PhaazeDiscord, guild_id, prevent_new=True)
	log_coro:Coroutine = loggingOnLevelEdit(PhaazeDiscord, GuildSettings, Editor=CheckMember, changed_member_id=CurrentLevelUser.member_id, changes=changes)
	asyncio.ensure_future(log_coro, loop=cls.Web.BASE.DiscordLoop)

	cls.Web.BASE.Logger.debug(f"(API/Discord) Level: {guild_id=} {member_id=} updated", require="discord:levels")
	return cls.response(
		text=json.dumps( dict(msg="Level: Updated", changes=changes, status=200) ),
		content_type="application/json",
		status=200
	)
