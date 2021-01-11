from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex
	from Platforms.Discord.main_discord import PhaazebotDiscord

import json
import discord
from aiohttp.web import Response, Request
from Utils.Classes.webrequestcontent import WebRequestContent
from Utils.Classes.discordwebuser import DiscordWebUser
from Utils.Classes.discordleveldisabledchannel import DiscordLevelDisabledChannel
from Platforms.Discord.db import getDiscordServerLevelDisabledChannels
from Platforms.Web.Processing.Api.errors import (
	apiMissingAuthorisation,
	apiMissingData
)
from Platforms.Web.Processing.Api.Discord.errors import (
	apiDiscordGuildUnknown,
	apiDiscordMemberNotFound,
	apiDiscordMissingPermission
)
from .errors import apiDiscordConfigsLevelDisabledChannelNotExists

async def apiDiscordConfigsLevelDisabledChannelsDelete(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
		Default url: /api/discord/configs/leveldisabledchannels/delete
	"""
	Data:WebRequestContent = WebRequestContent(WebRequest)
	await Data.load()

	# get required stuff
	guild_id:str = Data.getStr("guild_id", "", must_be_digit=True)
	entry_id:str = Data.getStr("entry_id", "", must_be_digit=True)
	channel_id:str = Data.getStr("channel_id", "", must_be_digit=True)

	# checks
	if not guild_id:
		return await apiMissingData(cls, WebRequest, msg="missing or invalid 'guild_id'")

	if (not entry_id) and (not channel_id):
		return await apiMissingData(cls, WebRequest, msg="missing or invalid 'entry_id' or 'channel_id'")

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

	# get channel entry
	res_channel:list = await getDiscordServerLevelDisabledChannels(cls.Web.BASE.Discord, guild_id, entry_id=entry_id, channel_id=channel_id)

	if not res_channel:
		return await apiDiscordConfigsLevelDisabledChannelNotExists(cls, WebRequest, channel_id=channel_id)

	ChannelToDelete:DiscordLevelDisabledChannel = res_channel.pop(0)

	cls.Web.BASE.PhaazeDB.deleteQuery("""
		DELETE FROM `discord_disabled_levelchannel` WHERE `guild_id` = %s AND `id` = %s""",
		(ChannelToDelete.guild_id, ChannelToDelete.entry_id)
	)

	cls.Web.BASE.Logger.debug(f"(API/Discord) Level disabled channel: {guild_id=} deleted [{channel_id=}, {entry_id=}]", require="discord:configs")
	return cls.response(
		text=json.dumps( dict(msg=f"Level disabled channel: Deleted entry", deleted=ChannelToDelete.channel_id, status=200) ),
		content_type="application/json",
		status=200
	)
