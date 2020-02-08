from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex
	from Platforms.Discord.main_discord import PhaazebotDiscord

import re
import json
import discord
from aiohttp.web import Response, Request
from Utils.Classes.webrequestcontent import WebRequestContent
from Utils.Classes.discordwebuserinfo import DiscordWebUserInfo
from Utils.Classes.twitchuser import TwitchUser
from Utils.regex import Twitch as TwitchRe
from Platforms.Twitch.api import getTwitchUsers
from .errors import apiDiscordAlertExists, apiDiscordAlertSameTwitchChannelLimit
from Platforms.Web.Processing.Api.Twitch.errors import apiTwitchUserNotFound
from Platforms.Web.Processing.Api.errors import apiMissingData,	apiMissingAuthorisation
from Platforms.Web.Processing.Api.Discord.errors import (
	apiDiscordGuildUnknown,
	apiDiscordMemberNotFound,
	apiDiscordMissingPermission
)

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
	custom_msg:str = Data.getStr("custom_msg", "")

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
			discord_channel_id = discord_channel_id,
			twitch_channel_id = FoundUser.user_id
		)
	)

	if res[0]["twitch_channel_match"] >= MAX_SAME_TWITCH_ALERTS_PER_GUILD:
		return await apiDiscordAlertSameTwitchChannelLimit(cls, WebRequest, limit=MAX_SAME_TWITCH_ALERTS_PER_GUILD, twitch_name=FoundUser.display_name)

	if res[0]["discord_channel_match"] >= 1:
		# nothing... for now
		pass

	if res[0]["both_match"] >= 1:
		return await apiDiscordAlertExists(cls, WebRequest, twitch_name=FoundUser.name, discord_id=discord_channel_id)

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

	# new alert
	new:dict = dict(
		discord_guild_id = guild_id,
		discord_channel_id = discord_channel_id,
		twitch_channel_id = FoundUser.user_id,
		custom_msg = custom_msg
	)

	cls.Web.BASE.PhaazeDB.insertQuery(table="discord_twitch_alert", content=new)

	cls.Web.BASE.Logger.debug(f"(API/Discord) Created new twitch alert: S:{guild_id}", require="discord:alert")

	return cls.response(
		text=json.dumps( dict(msg="new alert successfull created", status=200) ),
		content_type="application/json",
		status=200
	)
