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
from Utils.Classes.extendedrequest import ExtendedRequest
from Utils.Classes.undefined import UNDEFINED
from Platforms.Discord.logging import loggingOnLevelmedalCreate
from Platforms.Discord.db import getDiscordSeverSettings
from Platforms.Web.utils import authDiscordWebUser

async def apiDiscordLevelsMedalsCreate(cls:"PhaazebotWeb", WebRequest:ExtendedRequest) -> Response:
	"""
	Default url: /api/discord/levels/medals/create
	"""
	Data:WebRequestContent = WebRequestContent(WebRequest)
	await Data.load()

	# get required stuff
	Create:StorageTransformer = StorageTransformer()
	Create["guild_id"] = Data.getStr("guild_id", UNDEFINED, must_be_digit=True)
	Create["member_id"] = Data.getStr("member_id", UNDEFINED, must_be_digit=True)
	Create["name"] = Data.getStr("name", "", len_max=512)

	# checks
	if not Create["guild_id"]:
		return await cls.Tree.Api.errors.apiMissingData(cls, WebRequest, msg="missing or invalid 'guild_id'")

	if not Create["member_id"]:
		return await cls.Tree.Api.errors.apiMissingData(cls, WebRequest, msg="missing or invalid 'member_id'")

	if not Create["name"]:
		return await cls.Tree.Api.errors.apiMissingData(cls, WebRequest, msg="missing or invalid 'name'")

	# get/check discord
	PhaazeDiscord:"PhaazebotDiscord" = cls.BASE.Discord
	Guild:discord.Guild = discord.utils.get(PhaazeDiscord.guilds, id=int(Create["guild_id"]))
	if not Guild:
		return await cls.Tree.Api.Discord.errors.apiDiscordGuildUnknown(cls, WebRequest)

	# check limit
	res:list = cls.BASE.PhaazeDB.selectQuery("""
		SELECT
			COUNT(*) AS `all`,
			SUM(
				CASE WHEN LOWER(`discord_user_medal`.`name`) = LOWER(%s)
				THEN 1 ELSE 0 END
			) AS `match`
		FROM `discord_user_medal`
		WHERE `discord_user_medal`.`guild_id` = %s
			AND `discord_user_medal`.`member_id` = %s""",
		(Create["name"], Create["guild_id"], Create["member_id"])
	)

	if res[0]['match']:
		return await cls.Tree.Api.Discord.Levels.Medals.errors.apiDiscordUserMedalExists(cls, WebRequest)

	if res[0]['all'] >= cls.BASE.Limit.discord_level_medal_amount:
		return await cls.Tree.Api.Discord.Levels.Medals.errors.apiDiscordUserMedalLimit(cls, WebRequest)

	# get user info
	AuthDiscord:AuthDiscordWebUser = await authDiscordWebUser(cls, WebRequest)
	if not AuthDiscord.found:
		return await cls.Tree.Api.errors.apiMissingAuthorisation(cls, WebRequest)

	# get member
	CheckMember:discord.Member = Guild.get_member(int(AuthDiscord.User.user_id))
	if not CheckMember:
		return await cls.Tree.Api.Discord.errors.apiDiscordMemberNotFound(cls, WebRequest, guild_id=Create["guild_id"], user_id=AuthDiscord.User.user_id)

	# check permissions
	if not (CheckMember.guild_permissions.administrator or CheckMember.guild_permissions.manage_guild):
		return await cls.Tree.Api.Discord.errors.apiDiscordMissingPermission(cls, WebRequest, guild_id=Create["guild_id"], user_id=AuthDiscord.User.user_id)

	cls.BASE.PhaazeDB.insertQuery(
		table="discord_user_medal",
		content={
			"guild_id": Create["guild_id"],
			"member_id": Create["member_id"],
			"name": Create["name"]
		}
	)

	# logging
	GuildSettings:DiscordServerSettings = await getDiscordSeverSettings(PhaazeDiscord, Create["guild_id"], prevent_new=True)
	log_coro:Coroutine = loggingOnLevelmedalCreate(PhaazeDiscord, GuildSettings, Creator=CheckMember, medal_member_id=Create["member_id"], medal_name=Create["name"])
	asyncio.ensure_future(log_coro, loop=cls.BASE.DiscordLoop)

	cls.BASE.Logger.debug(f"(API/Discord) User medal: {Create['guild_id']=} {Create['member_id']=} added new entry", require="discord:medals")
	return cls.response(
		text=json.dumps(dict(msg="Medal: Added new entry", entry=Create["name"], status=200)),
		content_type="application/json",
		status=200
	)
