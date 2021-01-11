from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex
	from Platforms.Discord.main_discord import PhaazebotDiscord

import json
import discord
from aiohttp.web import Response, Request
from Utils.Classes.webrequestcontent import WebRequestContent
from Utils.Classes.discordwebuser import DiscordWebUser
from Platforms.Discord.utils import getDiscordChannelFromString
from Platforms.Web.Processing.Api.errors import apiMissingAuthorisation, apiMissingData
from Platforms.Web.Processing.Api.Discord.errors import (
	apiDiscordGuildUnknown,
	apiDiscordMemberNotFound,
	apiDiscordMissingPermission,
	apiDiscordChannelNotFound
)
from .errors import apiDiscordConfigsQuoteDisabledChannelExists

async def apiDiscordConfigsQuoteDisabledChannelsCreate(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
		Default url: /api/discord/configs/quotedisabledchannels/create
	"""
	Data:WebRequestContent = WebRequestContent(WebRequest)
	await Data.load()

	# get required stuff
	guild_id:str = Data.getStr("guild_id", "", must_be_digit=True)
	channel_id:str = Data.getStr("channel_id", "", must_be_digit=True)

	# checks
	if not guild_id:
		return await apiMissingData(cls, WebRequest, msg="missing or invalid 'guild_id'")

	if not channel_id:
		return await apiMissingData(cls, WebRequest, msg="missing or invalid 'channel_id'")

	PhaazeDiscord:"PhaazebotDiscord" = cls.Web.BASE.Discord
	Guild:discord.Guild = discord.utils.get(PhaazeDiscord.guilds, id=int(guild_id))
	if not Guild:
		return await apiDiscordGuildUnknown(cls, WebRequest)

	# get user info
	DiscordUser:DiscordWebUser = await cls.getDiscordUserInfo(WebRequest)
	if not DiscordUser.found:
		return await apiMissingAuthorisation(cls, WebRequest)

	# get member
	CheckMember:discord.Member = Guild.get_member(int(DiscordUser.user_id))
	if not CheckMember:
		return await apiDiscordMemberNotFound(cls, WebRequest, guild_id=guild_id, user_id=DiscordUser.user_id)

	# check permissions
	if not (CheckMember.guild_permissions.administrator or CheckMember.guild_permissions.manage_guild):
		return await apiDiscordMissingPermission(cls, WebRequest, guild_id=guild_id, user_id=DiscordUser.user_id)

	ActionChannel:discord.TextChannel = getDiscordChannelFromString(PhaazeDiscord, Guild, channel_id, required_type="text")
	if not ActionChannel:
		return await apiDiscordChannelNotFound(cls, WebRequest, channel_id=channel_id)

	# check if already exists
	res:list = cls.Web.BASE.PhaazeDB.selectQuery("""
		SELECT COUNT(*) AS `match`
		FROM `discord_disabled_quotechannel`
		WHERE `discord_disabled_quotechannel`.`guild_id` = %s
			AND `discord_disabled_quotechannel`.`channel_id` = %s""",
		( guild_id, channel_id )
	)

	if res[0]["match"]:
			return await apiDiscordConfigsQuoteDisabledChannelExists(cls, WebRequest, channel_id=channel_id, channel_name=ActionChannel.name)

	cls.Web.BASE.PhaazeDB.insertQuery(
		table = "discord_disabled_quotechannel",
		content = {
			"guild_id": guild_id,
			"channel_id": channel_id
		}
	)

	cls.Web.BASE.Logger.debug(f"(API/Discord) Quote disabled channel: {guild_id=} added: {channel_id=}", require="discord:configs")
	return cls.response(
		text=json.dumps( dict(msg="Quote disabled channel: Added new entry", entry=channel_id, status=200) ),
		content_type="application/json",
		status=200
	)
