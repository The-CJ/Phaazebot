from typing import TYPE_CHECKING, Coroutine
if TYPE_CHECKING:
	from Platforms.Discord.main_discord import PhaazebotDiscord
	from Platforms.Web.main_web import PhaazebotWeb

import json
import asyncio
import discord
from aiohttp.web import Response
from Utils.Classes.discordserversettings import DiscordServerSettings
from Utils.Classes.discordtwitchalert import DiscordTwitchAlert
from Utils.Classes.authdiscordwebuser import AuthDiscordWebUser
from Utils.Classes.webrequestcontent import WebRequestContent
from Utils.Classes.extendedrequest import ExtendedRequest
from Utils.Classes.undefined import UNDEFINED
from Platforms.Web.Processing.Api.errors import apiMissingAuthorisation, apiMissingData
from Platforms.Discord.db import getDiscordServerTwitchAlerts, getDiscordSeverSettings
from Platforms.Discord.logging import loggingOnTwitchalertDelete
from Platforms.Web.utils import authDiscordWebUser

async def apiDiscordTwitchalertsDelete(cls:"PhaazebotWeb", WebRequest:ExtendedRequest) -> Response:
	"""
	Default url: /api/discord/twitchalerts/delete
	"""
	Data:WebRequestContent = WebRequestContent(WebRequest)
	await Data.load()

	# get required vars
	guild_id:str = Data.getStr("guild_id", UNDEFINED, must_be_digit=True)
	alert_id:str = Data.getStr("alert_id", UNDEFINED, must_be_digit=True)

	# checks
	if not guild_id:
		return await apiMissingData(cls, WebRequest, msg="missing or invalid 'guild_id'")

	if not alert_id:
		return await apiMissingData(cls, WebRequest, msg="missing or invalid 'alert_id'")

	PhaazeDiscord:"PhaazebotDiscord" = cls.BASE.Discord
	Guild:discord.Guild = discord.utils.get(PhaazeDiscord.guilds, id=int(guild_id))
	if not Guild:
		return await cls.Tree.Api.Discord.errors.apiDiscordGuildUnknown(cls, WebRequest)

	AuthDiscord:AuthDiscordWebUser = await authDiscordWebUser(cls, WebRequest)
	if not AuthDiscord.found:
		return await apiMissingAuthorisation(cls, WebRequest)

	# get member
	CheckMember:discord.Member = Guild.get_member(int(AuthDiscord.User.user_id))
	if not CheckMember:
		return await cls.Tree.Api.Discord.errors.apiDiscordMemberNotFound(cls, WebRequest, guild_id=guild_id, user_id=AuthDiscord.User.user_id)

	# check permissions
	if not (CheckMember.guild_permissions.administrator or CheckMember.guild_permissions.manage_guild):
		return await cls.Tree.Api.Discord.errors.apiDiscordMissingPermission(cls, WebRequest, guild_id=guild_id, user_id=AuthDiscord.User.user_id)

	# get alert
	alert_res:list = await getDiscordServerTwitchAlerts(PhaazeDiscord, guild_id=guild_id, alert_id=alert_id)

	if not alert_res:
		return await cls.Tree.Api.Discord.Twitchalerts.errors.apiDiscordAlertNotExists(cls, WebRequest, alert_id=alert_id)

	AlertToDelete:DiscordTwitchAlert = alert_res.pop(0)

	cls.BASE.PhaazeDB.deleteQuery("""
		DELETE FROM `discord_twitch_alert` WHERE `discord_guild_id` = %s AND `id` = %s""",
		(AlertToDelete.guild_id, AlertToDelete.alert_id)
	)

	# logging
	GuildSettings:DiscordServerSettings = await getDiscordSeverSettings(PhaazeDiscord, guild_id, prevent_new=True)
	log_coro:Coroutine = loggingOnTwitchalertDelete(PhaazeDiscord, GuildSettings,
		Deleter=CheckMember,
		twitch_channel=AlertToDelete.twitch_channel_name,
		discord_channel_id=AlertToDelete.discord_channel_id
	)
	asyncio.ensure_future(log_coro, loop=cls.BASE.DiscordLoop)

	cls.BASE.Logger.debug(f"(API/Discord) Twitchalert: {guild_id=} deleted {alert_id=}", require="discord:alert")
	return cls.response(
		text=json.dumps(dict(msg="Twitchalerts: Entry deleted", deleted=AlertToDelete.twitch_channel_name, status=200)),
		content_type="application/json",
		status=200
	)
