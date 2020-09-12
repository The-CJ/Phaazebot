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
from Utils.Classes.discordtwitchalert import DiscordTwitchAlert
from Utils.Classes.undefined import UNDEFINED
from Platforms.Discord.db import getDiscordServerTwitchAlerts, getDiscordSeverSettings
from Platforms.Discord.logging import loggingOnTwitchalertEdit
from Platforms.Web.Processing.Api.errors import apiMissingData, apiMissingAuthorisation, apiWrongData
from Platforms.Web.Processing.Api.Discord.errors import apiDiscordGuildUnknown, apiDiscordMemberNotFound, apiDiscordMissingPermission
from .errors import apiDiscordAlertNotExists

MAX_CONTENT_SIZE:int = 1750

async def apiDiscordTwitchalertsEdit(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
	Default url: /api/discord/twitchalerts/edit
	"""
	Data:WebRequestContent = WebRequestContent(WebRequest)
	await Data.load()

	# get required stuff
	guild_id:str = Data.getStr("guild_id", "", must_be_digit=True)
	alert_id:str = Data.getStr("alert_id", "", must_be_digit=True)
	custom_msg:str = Data.getStr("custom_msg", UNDEFINED, len_max=1750)
	suppress_gamechange:bool = Data.getBool("suppress_gamechange", UNDEFINED)

	# checks
	if not guild_id:
		return await apiMissingData(cls, WebRequest, msg="missing or invalid 'guild_id'")

	if not alert_id:
		return await apiMissingData(cls, WebRequest, msg="missing or invalid 'alert_id'")

	if custom_msg is UNDEFINED or len(custom_msg) > MAX_CONTENT_SIZE:
		return await apiMissingData(cls, WebRequest, msg="missing or invalid 'custom_msg'")

	# get/check discord
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
	if not (CheckMember.guild_permissions.administrator or CheckMember.guild_permissions.manage_guild):
		return await apiDiscordMissingPermission(cls, WebRequest, guild_id=guild_id, user_id=DiscordUser.user_id)

	# get alert
	res_alerts:list = await getDiscordServerTwitchAlerts(PhaazeDiscord, guild_id, alert_id=alert_id)

	if not res_alerts:
		return await apiDiscordAlertNotExists(cls, WebRequest, alert_id=alert_id)

	CurrentEditAlert:DiscordTwitchAlert = res_alerts.pop(0)

	changes:dict = {}

	if custom_msg != UNDEFINED:
		changes["custom_msg"] = custom_msg

	if suppress_gamechange != UNDEFINED:
		changes["suppress_gamechange"] = suppress_gamechange

	if not changes:
		return await apiWrongData(cls, WebRequest, msg=f"No changes, please add at least one")


	cls.Web.BASE.PhaazeDB.updateQuery(
		table = "discord_twitch_alert",
		content = changes,
		where = "`discord_twitch_alert`.`discord_guild_id` = %s AND `discord_twitch_alert`.`id` = %s",
		where_values = (CurrentEditAlert.guild_id, CurrentEditAlert.alert_id)
	)

	# logging
	GuildSettings:DiscordServerSettings = await getDiscordSeverSettings(PhaazeDiscord, guild_id, prevent_new=True)
	log_coro:Coroutine = loggingOnTwitchalertEdit(PhaazeDiscord, GuildSettings, ChangeMember=CheckMember, twitch_channel=CurrentEditAlert.twitch_channel_name, changes=changes)
	asyncio.ensure_future(log_coro, loop=cls.Web.BASE.DiscordLoop)

	cls.Web.BASE.Logger.debug(f"(API/Discord) Twitchalert: {guild_id=} edited {alert_id=}", require="discord:alerts")
	return cls.response(
		text=json.dumps( dict(msg="Twitchalert: Edited entry", changes=changes, status=200) ),
		content_type="application/json",
		status=200
	)
