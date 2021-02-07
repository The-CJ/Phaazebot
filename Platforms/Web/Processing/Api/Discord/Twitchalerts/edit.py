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
from Utils.Classes.discordtwitchalert import DiscordTwitchAlert
from Utils.Classes.webrequestcontent import WebRequestContent
from Utils.Classes.extendedrequest import ExtendedRequest
from Utils.Classes.undefined import UNDEFINED
from Platforms.Web.utils import authDiscordWebUser
from Platforms.Discord.db import getDiscordServerTwitchAlerts, getDiscordSeverSettings
from Platforms.Discord.logging import loggingOnTwitchalertEdit

MAX_CONTENT_SIZE:int = 1750

async def apiDiscordTwitchalertsEdit(cls:"PhaazebotWeb", WebRequest:ExtendedRequest) -> Response:
	"""
	Default url: /api/discord/twitchalerts/edit
	"""
	Data:WebRequestContent = WebRequestContent(WebRequest)
	await Data.load()

	# get required stuff
	Edit:StorageTransformer = StorageTransformer()
	Edit["guild_id"] = Data.getStr("guild_id", UNDEFINED, must_be_digit=True)
	Edit["alert_id"] = Data.getStr("alert_id", UNDEFINED, must_be_digit=True)

	# checks
	if not Edit["alert_id"]:
		return await cls.Tree.Api.errors.apiMissingData(cls, WebRequest, msg="missing or invalid 'alert_id'")

	if not Edit["guild_id"]:
		return await cls.Tree.Api.errors.apiMissingData(cls, WebRequest, msg="missing or invalid 'guild_id'")

	# get/check discord
	PhaazeDiscord:"PhaazebotDiscord" = cls.BASE.Discord
	Guild:discord.Guild = discord.utils.get(PhaazeDiscord.guilds, id=int(Edit["guild_id"]))
	if not Guild:
		return await cls.Tree.Api.Discord.errors.apiDiscordGuildUnknown(cls, WebRequest)

	# get alert
	res_alerts:list = await getDiscordServerTwitchAlerts(PhaazeDiscord, discord_guild_id=Edit["guild_id"], alert_id=Edit["alert_id"])

	if not res_alerts:
		return await cls.Tree.Api.Discord.Twitchalerts.errors.apiDiscordAlertNotExists(cls, WebRequest, alert_id=Edit["guild_id"])

	CurrentEditAlert:DiscordTwitchAlert = res_alerts.pop(0)

	# check all update values
	update:dict = dict()

	Edit["custom_msg"] = Data.getStr("custom_msg", UNDEFINED, len_max=MAX_CONTENT_SIZE, allow_none=True)
	if Edit["custom_msg"] != UNDEFINED:
		update["custom_msg"] = Edit["custom_msg"]

	Edit["suppress_gamechange"] = Data.getBool("suppress_gamechange", UNDEFINED)
	if Edit["suppress_gamechange"] != UNDEFINED:
		update["suppress_gamechange"] = Edit["suppress_gamechange"]

	if not update:
		return await cls.Tree.Api.errors.apiWrongData(cls, WebRequest, msg=f"No changes, please add at least one")

	# get user info
	AuthDiscord:AuthDiscordWebUser = await authDiscordWebUser(cls, WebRequest)
	if not AuthDiscord.found:
		return await cls.Tree.Api.errors.apiMissingAuthorisation(cls, WebRequest)

	# get member
	CheckMember:discord.Member = Guild.get_member(int(AuthDiscord.User.user_id))
	if not CheckMember:
		return await cls.Tree.Api.Discord.errors.apiDiscordMemberNotFound(cls, WebRequest, guild_id=Edit["guild_id"], user_id=AuthDiscord.User.user_id)

	# check permissions
	if not (CheckMember.guild_permissions.administrator or CheckMember.guild_permissions.manage_guild):
		return await cls.Tree.Api.Discord.errors.apiDiscordMissingPermission(cls, WebRequest, guild_id=Edit["guild_id"], user_id=AuthDiscord.User.user_id)

	cls.BASE.PhaazeDB.updateQuery(
		table="discord_twitch_alert",
		content=update,
		where="`discord_twitch_alert`.`discord_guild_id` = %s AND `discord_twitch_alert`.`id` = %s",
		where_values=(CurrentEditAlert.guild_id, CurrentEditAlert.alert_id)
	)

	# logging
	GuildSettings:DiscordServerSettings = await getDiscordSeverSettings(PhaazeDiscord, Edit["guild_id"], prevent_new=True)
	log_coro:Coroutine = loggingOnTwitchalertEdit(PhaazeDiscord, GuildSettings,
		ChangeMember=CheckMember,
		twitch_channel=CurrentEditAlert.twitch_channel_name,
		discord_channel_id=CurrentEditAlert.discord_channel_id,
		changes=update
	)
	asyncio.ensure_future(log_coro, loop=cls.BASE.DiscordLoop)

	cls.BASE.Logger.debug(f"(API/Discord) Twitchalert: {Edit['guild_id']=} edited {Edit['alert_id']=}", require="discord:alerts")
	return cls.response(
		text=json.dumps(dict(msg="Twitchalert: Edited entry", changes=update, status=200)),
		content_type="application/json",
		status=200
	)
