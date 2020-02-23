from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex
	from Platforms.Discord.main_discord import PhaazebotDiscord

import json
import discord
from aiohttp.web import Response, Request
from Utils.Classes.webrequestcontent import WebRequestContent
from Utils.Classes.discordtwitchalert import DiscordTwitchAlert
from Platforms.Discord.utils import getDiscordServerTwitchAlerts
from .errors import apiDiscordAlertNotExists
from Platforms.Web.Processing.Api.errors import apiMissingData, apiMissingAuthorisation
from Platforms.Web.Processing.Api.Discord.errors import apiDiscordGuildUnknown, apiDiscordMemberNotFound, apiDiscordMissingPermission
from Utils.Classes.discordwebuserinfo import DiscordWebUserInfo

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
	custom_msg:str = Data.getStr("custom_msg", "")

	# checks
	if not guild_id:
		return await apiMissingData(cls, WebRequest, msg="missing or invalid 'guild_id'")

	if not alert_id:
		return await apiMissingData(cls, WebRequest, msg="missing or invalid 'alert_id'")

	if not custom_msg or len(custom_msg) > MAX_CONTENT_SIZE:
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
	res_alerts:list = await getDiscordServerTwitchAlerts(cls.Web.BASE.Discord, guild_id, alert_id=alert_id)

	if not res_alerts:
		return await apiDiscordAlertNotExists(cls, WebRequest, alert_id=alert_id)

	CurrentEditAlert:DiscordTwitchAlert = res_alerts.pop(0)

	changes:dict = {"custom_msg": custom_msg}

	cls.Web.BASE.PhaazeDB.updateQuery(
		table = "discord_twitch_alert",
		content = changes,
		where = "`discord_twitch_alert`.`discord_guild_id` = %s AND `discord_twitch_alert`.`id` = %s",
		where_values = (CurrentEditAlert.guild_id, CurrentEditAlert.alert_id)
	)

	cls.Web.BASE.Logger.debug(f"(API/Discord) Twitchalert: {guild_id=} edited {alert_id=}", require="discord:alerts")
	return cls.response(
		text=json.dumps( dict(msg="Twitchalert: Edited entry", changes=changes, status=200) ),
		content_type="application/json",
		status=200
	)
