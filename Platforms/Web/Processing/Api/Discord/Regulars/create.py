from typing import TYPE_CHECKING, Coroutine
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex
	from Platforms.Discord.main_discord import PhaazebotDiscord

import json
import asyncio
import discord
from aiohttp.web import Response, Request
from Utils.Classes.discordserversettings import DiscordServerSettings
from Utils.Classes.discordwebuser import DiscordWebUserInfo
from Utils.Classes.webrequestcontent import WebRequestContent
from Platforms.Discord.db import getDiscordSeverSettings
from Platforms.Discord.utils import getDiscordMemberFromString
from Platforms.Discord.logging import loggingOnRegularCreate
from Platforms.Web.Processing.Api.errors import (
	apiMissingData,
	apiMissingAuthorisation
)
from Platforms.Web.Processing.Api.Discord.errors import (
	apiDiscordGuildUnknown,
	apiDiscordMemberNotFound,
	apiDiscordMissingPermission
)
from .errors import apiDiscordRegularLimit, apiDiscordRegularExists

async def apiDiscordRegularsCreate(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
	Default url: /api/discord/regulars/create
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

	# get/check discord
	PhaazeDiscord:"PhaazebotDiscord" = cls.Web.BASE.Discord
	Guild:discord.Guild = discord.utils.get(PhaazeDiscord.guilds, id=int(guild_id))
	if not Guild:
		return await apiDiscordGuildUnknown(cls, WebRequest)

	ActionMember:discord.Member = getDiscordMemberFromString(PhaazeDiscord, Guild, member_id)
	if not ActionMember:
		return await apiDiscordMemberNotFound(cls, WebRequest, user_id=member_id)

	# check if already exists and limits
	res:list = cls.Web.BASE.PhaazeDB.selectQuery("""
		SELECT
			COUNT(*) AS `all`,
			SUM(
				CASE WHEN `discord_regular`.`member_id` = %s
				THEN 1 ELSE 0 END
			) AS `match`
		FROM `discord_regular`
		WHERE `discord_regular`.`guild_id` = %s""",
		( str(ActionMember.id), str(ActionMember.guild.id) )
	)

	if res[0]["match"]:
		return await apiDiscordRegularExists(cls, WebRequest)

	if res[0]["all"] >= cls.Web.BASE.Limit.discord_regular_amount:
		return await apiDiscordRegularLimit(cls, WebRequest)

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

	cls.Web.BASE.PhaazeDB.insertQuery(
		table="discord_regular",
		content={
			"guild_id": str(ActionMember.guild.id),
			"member_id": str(ActionMember.id)
		}
	)

	# logging
	GuildSettings:DiscordServerSettings = await getDiscordSeverSettings(PhaazeDiscord, guild_id, prevent_new=True)
	log_coro:Coroutine = loggingOnRegularCreate(PhaazeDiscord, GuildSettings, Creator=CheckMember, NewRegular=ActionMember)
	asyncio.ensure_future(log_coro, loop=cls.Web.BASE.DiscordLoop)

	cls.Web.BASE.Logger.debug(f"(API/Discord) Regular: {guild_id=} added new entry {member_id=}", require="discord:regulars")
	return cls.response(
		text=json.dumps( dict(msg="Regulars: Added new entry", entry=ActionMember.name, status=200) ),
		content_type="application/json",
		status=200
	)
