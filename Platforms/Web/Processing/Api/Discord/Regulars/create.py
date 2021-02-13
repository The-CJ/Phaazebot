from typing import TYPE_CHECKING, Coroutine
if TYPE_CHECKING:
	from Platforms.Discord.main_discord import PhaazebotDiscord
	from Platforms.Web.main_web import PhaazebotWeb

import json
import asyncio
import discord
from aiohttp.web import Response
from Utils.Classes.discordserversettings import DiscordServerSettings
from Utils.Classes.authdiscordwebuser import AuthDiscordWebUser
from Utils.Classes.storagetransformer import StorageTransformer
from Utils.Classes.webrequestcontent import WebRequestContent
from Utils.Classes.extendedrequest import ExtendedRequest
from Utils.Classes.undefined import UNDEFINED
from Platforms.Discord.utils import getDiscordMemberFromString
from Platforms.Discord.logging import loggingOnRegularCreate
from Platforms.Discord.db import getDiscordSeverSettings
from Platforms.Web.utils import authDiscordWebUser

async def apiDiscordRegularsCreate(cls:"PhaazebotWeb", WebRequest:ExtendedRequest) -> Response:
	"""
	Default url: /api/discord/regulars/create
	"""
	Data:WebRequestContent = WebRequestContent(WebRequest)
	await Data.load()

	# get required stuff
	Create:StorageTransformer = StorageTransformer()
	Create["guild_id"] = Data.getStr("guild_id", UNDEFINED, must_be_digit=True)
	Create["member_id"] = Data.getStr("member_id", UNDEFINED, must_be_digit=True)

	# checks
	if not Create["guild_id"]:
		return await cls.Tree.Api.errors.apiMissingData(cls, WebRequest, msg="missing or invalid 'guild_id'")

	if not Create["member_id"]:
		return await cls.Tree.Api.errors.apiMissingData(cls, WebRequest, msg="missing or invalid 'member_id'")

	# get/check discord
	PhaazeDiscord:"PhaazebotDiscord" = cls.BASE.Discord
	Guild:discord.Guild = discord.utils.get(PhaazeDiscord.guilds, id=int(Create["guild_id"]))
	if not Guild:
		return await cls.Tree.Api.Discord.errors.apiDiscordGuildUnknown(cls, WebRequest)

	ActionMember:discord.Member = getDiscordMemberFromString(PhaazeDiscord, Guild, Create["member_id"])
	if not ActionMember:
		return await cls.Tree.Api.Discord.errors.apiDiscordMemberNotFound(cls, WebRequest, user_id=Create["member_id"])

	# check if already exists and limits
	res:list = cls.BASE.PhaazeDB.selectQuery("""
		SELECT
			COUNT(*) AS `all`,
			SUM(
				CASE WHEN `discord_regular`.`member_id` = %s
				THEN 1 ELSE 0 END
			) AS `match`
		FROM `discord_regular`
		WHERE `discord_regular`.`guild_id` = %s""",
		(str(ActionMember.id), str(ActionMember.guild.id))
	)

	if res[0]["match"]:
		return await cls.Tree.Api.Discord.Regulars.errors.apiDiscordRegularExists(cls, WebRequest)

	if res[0]["all"] >= cls.BASE.Limit.discord_regular_amount:
		return await cls.Tree.Api.Discord.Regulars.errors.apiDiscordRegularLimit(cls, WebRequest)

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
		table="discord_regular",
		content={
			"guild_id": str(ActionMember.guild.id),
			"member_id": str(ActionMember.id)
		}
	)

	# logging
	GuildSettings:DiscordServerSettings = await getDiscordSeverSettings(PhaazeDiscord, Create["guild_id"], prevent_new=True)
	log_coro:Coroutine = loggingOnRegularCreate(PhaazeDiscord, GuildSettings, Creator=CheckMember, NewRegular=ActionMember)
	asyncio.ensure_future(log_coro, loop=cls.BASE.DiscordLoop)

	cls.BASE.Logger.debug(f"(API/Discord) Regular: {Create['guild_id']=} added new entry {Create['member_id']=}", require="discord:regulars")
	return cls.response(
		text=json.dumps(dict(msg="Regulars: Added new entry", entry=ActionMember.name, status=200)),
		content_type="application/json",
		status=200
	)
