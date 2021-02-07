from typing import TYPE_CHECKING, Coroutine
if TYPE_CHECKING:
	from Platforms.Discord.main_discord import PhaazebotDiscord
	from Platforms.Web.main_web import PhaazebotWeb

import re
import json
import asyncio
import discord
from aiohttp.web import Response
from Utils.Classes.discordserversettings import DiscordServerSettings
from Utils.Classes.storagetransformer import StorageTransformer
from Utils.Classes.authdiscordwebuser import AuthDiscordWebUser
from Utils.Classes.webrequestcontent import WebRequestContent
from Utils.Classes.extendedrequest import ExtendedRequest
from Utils.Classes.twitchuser import TwitchUser
from Utils.Classes.undefined import UNDEFINED
from Platforms.Discord.logging import loggingOnTwitchalertCreate
from Platforms.Discord.utils import getDiscordChannelFromString
from Platforms.Discord.db import getDiscordSeverSettings
from Platforms.Web.utils import authDiscordWebUser
from Platforms.Twitch.api import getTwitchUsers
from Utils.regex import Twitch as TwitchRe

# did i mention that it is sadness that i need to added this...
MAX_SAME_TWITCH_ALERTS_PER_GUILD:int = 3
MAX_CONTENT_SIZE:int = 1750

async def apiDiscordTwitchalertsCreate(cls:"PhaazebotWeb", WebRequest:ExtendedRequest) -> Response:
	"""
	Default url: /api/discord/twitchalerts/create
	"""
	Data:WebRequestContent = WebRequestContent(WebRequest)
	await Data.load()

	# get required stuff
	Create:StorageTransformer = StorageTransformer()
	Create["guild_id"] = Data.getStr("guild_id", UNDEFINED, must_be_digit=True)
	Create["discord_channel_id"] = Data.getStr("discord_channel_id", UNDEFINED, must_be_digit=True)
	Create["twitch_channel"] = Data.getStr("twitch_channel", UNDEFINED)
	Create["custom_msg"] = Data.getStr("custom_msg", None, len_max=MAX_CONTENT_SIZE, allow_none=True)
	Create["suppress_gamechange"] = Data.getBool("suppress_gamechange", False)

	# checks
	if not Create["guild_id"]:
		return await cls.Tree.Api.errors.apiMissingData(cls, WebRequest, msg="missing or invalid 'guild_id'")

	if not Create["discord_channel_id"]:
		return await cls.Tree.Api.errors.apiMissingData(cls, WebRequest, msg="missing or invalid 'discord_channel_id'")

	if not Create["twitch_channel"]:
		return await cls.Tree.Api.errors.apiMissingData(cls, WebRequest, msg="missing or invalid 'twitch_channel'")

	# get/check discord
	PhaazeDiscord:"PhaazebotDiscord" = cls.BASE.Discord
	Guild:discord.Guild = discord.utils.get(PhaazeDiscord.guilds, id=int(Create["guild_id"]))
	if not Guild:
		return await cls.Tree.Api.Discord.errors.apiDiscordGuildUnknown(cls, WebRequest)

	TargetDiscordChannel:discord.TextChannel = getDiscordChannelFromString(PhaazeDiscord, Guild, Create["discord_channel_id"], required_type="text")
	if not TargetDiscordChannel:
		return await cls.Tree.Api.Discord.errors.apiDiscordChannelNotFound(cls, WebRequest, msg=f"Could not find a valid text channel")

	Match:re.Match = TwitchRe().ChannelLink.match(Create["twitch_channel"])
	if Match:
		Create["twitch_channel"] = Match.group("name")

	user_res:list = await getTwitchUsers(cls.BASE, item=Create["twitch_channel"], item_type="login")
	if not user_res:
		return await cls.Tree.Api.Twitch.errors.apiTwitchUserNotFound(cls, WebRequest, user_name=Create["twitch_channel"])

	FoundUser:TwitchUser = user_res.pop(0)

	# check if already exists and limits
	res:list = cls.BASE.PhaazeDB.selectQuery("""
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
			discord_guild_id=Create["guild_id"],
			discord_channel_id=str(TargetDiscordChannel.id),
			twitch_channel_id=FoundUser.user_id
		)
	)

	if res[0]["twitch_channel_match"] >= MAX_SAME_TWITCH_ALERTS_PER_GUILD:
		return await cls.Tree.Api.Discord.Twitchalerts.errors.apiDiscordAlertSameTwitchChannelLimit(cls, WebRequest, limit=MAX_SAME_TWITCH_ALERTS_PER_GUILD, twitch_name=FoundUser.display_name)

	if res[0]["discord_channel_match"] >= 1:
		# nothing... for now
		pass

	if res[0]["both_match"] >= 1:
		return await cls.Tree.Api.Discord.Twitchalerts.errors.apiDiscordAlertExists(cls, WebRequest, twitch_name=FoundUser.name, discord_id=TargetDiscordChannel.id)

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
		table="discord_twitch_alert",
		content={
			"discord_guild_id": Create["guild_id"],
			"discord_channel_id": str(TargetDiscordChannel.id),
			"twitch_channel_id": FoundUser.user_id,
			"custom_msg": Create["custom_msg"],
			"suppress_gamechange": Create["suppress_gamechange"]
		}
	)

	# logging
	GuildSettings:DiscordServerSettings = await getDiscordSeverSettings(PhaazeDiscord, Create["guild_id"], prevent_new=True)
	log_coro:Coroutine = loggingOnTwitchalertCreate(PhaazeDiscord, GuildSettings, Creator=CheckMember, discord_channel=TargetDiscordChannel.name, twitch_channel=FoundUser.name)
	asyncio.ensure_future(log_coro, loop=cls.BASE.DiscordLoop)

	# some after work, with the new data
	await placeGatheredData(cls, FoundUser)
	cls.BASE.Logger.debug(f"(API/Discord) Twitchalert: {Create['guild_id']=} added {FoundUser.user_id=}", require="discord:alert")
	return cls.response(
		text=json.dumps(dict(msg="Twitchalert: Added new entry", entry=FoundUser.user_type, status=200)),
		content_type="application/json",
		status=200
	)

async def placeGatheredData(cls:"PhaazebotWeb", AlertUser:TwitchUser) -> None:

	# first thing we do, adding the name to twitch_user_name, so we get the name to a id without asking twitch again
	cls.BASE.PhaazeDB.insertQuery(
		update_on_duplicate=True,
		table="twitch_user_name",
		content={
			"user_id": AlertUser.user_id,
			"user_name": AlertUser.name,
			"user_display_name": AlertUser.display_name,
		}
	)

	# all alerts require the the twitch channel to be present in the "twitch_channel" table
	# (a "twitch_setting" entry is not necessary)
	exists:list = cls.BASE.PhaazeDB.selectQuery("""
		SELECT COUNT(*) AS `I`
		FROM `twitch_channel`
		WHERE `twitch_channel`.`channel_id` = %s""",
		(AlertUser.user_id,)
	)

	# it its not found, add it
	if exists[0]['I'] == 0:
		cls.BASE.PhaazeDB.insertQuery(
			table="twitch_channel",
			content={
				"channel_id": AlertUser.user_id,
				"managed": 0,
				"live": 0
			}
		)
