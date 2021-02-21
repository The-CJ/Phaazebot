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
from Utils.Classes.discordusermedal import DiscordUserMedal
from Utils.Classes.extendedrequest import ExtendedRequest
from Utils.Classes.undefined import UNDEFINED
from Platforms.Web.utils import authDiscordWebUser
from Platforms.Discord.db import getDiscordUsersMedals, getDiscordSeverSettings
from Platforms.Discord.logging import loggingOnLevelmedalDelete
from Platforms.Web.Processing.Api.errors import apiMissingAuthorisation, apiMissingData

async def apiDiscordLevelsMedalsDelete(cls:"PhaazebotWeb", WebRequest:ExtendedRequest) -> Response:
	"""
	Default url: /api/discord/levels/medals/delete
	"""
	Data:WebRequestContent = WebRequestContent(WebRequest)
	await Data.load()

	# get required vars
	guild_id:str = Data.getStr("guild_id", UNDEFINED, must_be_digit=True)
	member_id:str = Data.getStr("member_id", UNDEFINED, must_be_digit=True)
	medal_id:str = Data.getStr("medal_id", UNDEFINED, must_be_digit=True)

	# checks
	if not guild_id:
		return await apiMissingData(cls, WebRequest, msg="missing or invalid 'guild_id'")

	if not member_id:
		return await apiMissingData(cls, WebRequest, msg="missing or invalid 'member_id'")

	if not medal_id:
		return await apiMissingData(cls, WebRequest, msg="missing or invalid 'medal_id'")

	PhaazeDiscord:"PhaazebotDiscord" = cls.BASE.Discord
	Guild:discord.Guild = discord.utils.get(PhaazeDiscord.guilds, id=int(guild_id))
	if not Guild:
		return await cls.Tree.Api.Discord.errors.apiDiscordGuildUnknown(cls, WebRequest)

	# get medal
	res_medal:list = await getDiscordUsersMedals(PhaazeDiscord, guild_id=guild_id, member_id=member_id, medal_id=medal_id)

	if not res_medal:
		return await cls.Tree.Api.Discord.Levels.Medals.errors.apiDiscordUserMedalNotExists(cls, WebRequest, medal_id=medal_id)

	MedalToDelete:DiscordUserMedal = res_medal.pop(0)

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

	cls.BASE.PhaazeDB.deleteQuery("""
		DELETE FROM `discord_user_medal` WHERE `guild_id` = %s AND `id` = %s""",
		(MedalToDelete.guild_id, MedalToDelete.medal_id)
	)

	# logging
	GuildSettings:DiscordServerSettings = await getDiscordSeverSettings(PhaazeDiscord, guild_id, prevent_new=True)
	log_coro:Coroutine = loggingOnLevelmedalDelete(PhaazeDiscord, GuildSettings,
		Deleter=CheckMember,
		medal_member_id=MedalToDelete.member_id,
		medal_name=MedalToDelete.name
	)
	asyncio.ensure_future(log_coro, loop=cls.BASE.DiscordLoop)

	cls.BASE.Logger.debug(f"(API/Discord) Medal: {guild_id=} deleted {medal_id=}", require="discord:medals")
	return cls.response(
		text=json.dumps(dict(msg="Medal: Deleted entry", deleted=MedalToDelete.name, status=200)),
		content_type="application/json",
		status=200
	)
