from typing import TYPE_CHECKING, Coroutine
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex
	from Platforms.Discord.main_discord import PhaazebotDiscord

import re
import json
import asyncio
import discord
from aiohttp.web import Response, Request
from Utils.Classes.discordserversettings import DiscordServerSettings
from Utils.Classes.discordwebuser import DiscordWebUserInfo
from Utils.Classes.webrequestcontent import WebRequestContent
from Utils.Classes.twitchuser import TwitchUser
from Platforms.Twitch.api import getTwitchUsers
from Platforms.Discord.db import getDiscordSeverSettings
from Platforms.Discord.utils import getDiscordChannelFromString
from Platforms.Discord.logging import loggingOnTwitchalertCreate
from Utils.regex import Twitch as TwitchRe
from Platforms.Web.Processing.Api.Twitch.errors import apiTwitchUserNotFound
from Platforms.Web.Processing.Api.errors import apiMissingData,	apiMissingAuthorisation
from .errors import apiDiscordAlertExists, apiDiscordAlertSameTwitchChannelLimit
from Platforms.Web.Processing.Api.Discord.errors import (
	apiDiscordGuildUnknown,
	apiDiscordMemberNotFound,
	apiDiscordMissingPermission,
	apiDiscordChannelNotFound
)

# did i mention that it is sadness that i need to added this...
MAX_SAME_TWITCH_ALERTS_PER_GUILD:int = 3

async def apiDiscordTwitchalertsCreate(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
	Default url: /api/discord/twitchalerts/create
	"""
	Data:WebRequestContent = WebRequestContent(WebRequest)
	await Data.load()

	# get required stuff
	guild_id:str = Data.getStr("guild_id", "", must_be_digit=True)
	discord_channel_id:str = Data.getStr("discord_channel_id", "", must_be_digit=True)
	twitch_channel:str = Data.getStr("twitch_channel", "")
	custom_msg:str = Data.getStr("custom_msg", "", len_max=1750)
	suppress_gamechange:bool = Data.getBool("suppress_gamechange", False)

	# checks
	if not guild_id:
		return await apiMissingData(cls, WebRequest, msg="missing or invalid 'guild_id'")

	if not discord_channel_id:
		return await apiMissingData(cls, WebRequest, msg="missing or invalid 'discord_channel_id'")

	if not twitch_channel:
		return await apiMissingData(cls, WebRequest, msg="missing or invalid 'twitch_channel'")

	# get/check discord
	PhaazeDiscord:"PhaazebotDiscord" = cls.Web.BASE.Discord
	Guild:discord.Guild = discord.utils.get(PhaazeDiscord.guilds, id=int(guild_id))
	if not Guild:
		return await apiDiscordGuildUnknown(cls, WebRequest)

	TargetDiscordChannel:discord.TextChannel = getDiscordChannelFromString(PhaazeDiscord, Guild, discord_channel_id, required_type="text")
	if not TargetDiscordChannel:
		return await apiDiscordChannelNotFound(cls, WebRequest, msg=f"Could not find a valid text channel")

	Match:re.Match = TwitchRe().ChannelLink.match(twitch_channel)
	if Match:
		twitch_channel = Match.group("name")

	user_res:list = await getTwitchUsers(cls.Web.BASE, item=twitch_channel, item_type="login")
	if not user_res:
		return await apiTwitchUserNotFound(cls, WebRequest, user_name=twitch_channel)

	FoundUser:TwitchUser = user_res.pop(0)

	# check if already exists and limits
	res:list = cls.Web.BASE.PhaazeDB.selectQuery("""
		SELECT
			COUNT(*) AS `all`,
			SUM(
				CASE WHEN `discord_twitch_alert`.`twitch_channel_id` = %(twitch_channel_id)s
				THEN 1 ELSE 0 END
			) AS `twitch_channel_match`,
			SUM(
				CASE WHEN `discord_twitch_alert`.`discord_channel_id` = %(discord_channel_id)s
				THEN 1 ELSE 0 END
			) AS `discord_channel_match`,
			SUM(
				CASE WHEN `discord_twitch_alert`.`discord_channel_id` = %(discord_channel_id)s
					AND `discord_twitch_alert`.`twitch_channel_id` = %(twitch_channel_id)s
				THEN 1 ELSE 0 END
			) AS `both_match`
		FROM `discord_twitch_alert`
		WHERE `discord_twitch_alert`.`discord_guild_id` = %(discord_guild_id)s""",
		dict(
			discord_guild_id = guild_id,
			discord_channel_id = str(TargetDiscordChannel.id),
			twitch_channel_id = FoundUser.user_id
		)
	)

	if res[0]["twitch_channel_match"] >= MAX_SAME_TWITCH_ALERTS_PER_GUILD:
		return await apiDiscordAlertSameTwitchChannelLimit(cls, WebRequest, limit=MAX_SAME_TWITCH_ALERTS_PER_GUILD, twitch_name=FoundUser.display_name)

	if res[0]["discord_channel_match"] >= 1:
		# nothing... for now
		pass

	if res[0]["both_match"] >= 1:
		return await apiDiscordAlertExists(cls, WebRequest, twitch_name=FoundUser.name, discord_id=TargetDiscordChannel.id)

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
		table="discord_twitch_alert",
		content={
			"discord_guild_id": guild_id,
			"discord_channel_id": str(TargetDiscordChannel.id),
			"twitch_channel_id": FoundUser.user_id,
			"custom_msg": custom_msg,
			"suppress_gamechange": suppress_gamechange
		}
	)

	# logging
	GuildSettings:DiscordServerSettings = await getDiscordSeverSettings(PhaazeDiscord, guild_id, prevent_new=True)
	log_coro:Coroutine = loggingOnTwitchalertCreate(PhaazeDiscord, GuildSettings, Creator=CheckMember, discord_channel=TargetDiscordChannel.name, twitch_channel=FoundUser.name)
	asyncio.ensure_future(log_coro, loop=cls.Web.BASE.DiscordLoop)

	# some after work, with the new data
	await placeGatheredData(cls, FoundUser)
	cls.Web.BASE.Logger.debug(f"(API/Discord) Twitchalert: {guild_id=} added {FoundUser.user_id=}", require="discord:alert")
	return cls.response(
		text=json.dumps( dict(msg="Twitchalert: Added new entry", entry=FoundUser.user_type, status=200) ),
		content_type="application/json",
		status=200
	)

async def placeGatheredData(cls:"WebIndex", AlertUser:TwitchUser) -> None:

	# first thing we do, adding the name to twitch_user_name, so we get the name to a id without asking twitch again
	cls.Web.BASE.PhaazeDB.insertQuery(
		update_on_duplicate = True,
		table = "twitch_user_name",
		content = {
			"user_id": AlertUser.user_id,
			"user_name": AlertUser.name,
			"user_display_name": AlertUser.display_name,
		}
	)

	# all alerts require the the twitch channel to be present in the "twitch_channel" table
	# (a "twitch_setting" entry is not necessary)
	exists:list = cls.Web.BASE.PhaazeDB.selectQuery("""
		SELECT COUNT(*) AS `I`
		FROM `twitch_channel`
		WHERE `twitch_channel`.`channel_id` = %s""",
		(AlertUser.user_id,)
	)

	# it its not found, add it
	if exists[0]['I'] == 0:
		cls.Web.BASE.PhaazeDB.insertQuery(
			table = "twitch_channel",
			content = {
				"channel_id": AlertUser.user_id,
				"managed": 0,
				"live": 0
			}
		)
