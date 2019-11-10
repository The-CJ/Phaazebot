from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex
	from Platforms.Discord.main_discord import PhaazebotDiscord

import json
import discord
from aiohttp.web import Response, Request
from Utils.Classes.webrequestcontent import WebRequestContent
from Platforms.Web.Processing.Api.errors import missingData
from Platforms.Discord.utils import getDiscordSeverSettings
from Utils.Classes.discordserversettings import DiscordServerSettings
from Utils.Classes.discorduserinfo import DiscordUserInfo
from Platforms.Web.Processing.Api.errors import apiMissingAuthorisation
from Platforms.Web.Processing.Api.Discord.errors import apiDiscordGuildUnknown, apiDiscordMemberNotFound, apiDiscordMissingPermission

async def apiDiscordConfigsGet(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
		Default url: /api/discord/configs/get
	"""
	Data:WebRequestContent = WebRequestContent(WebRequest)
	await Data.load()

	guild_id:str = Data.getStr("guild_id", "", must_be_digit=True)
	if not guild_id:
		return await missingData(cls, WebRequest, msg="missing or invalid 'guild_id'")

	PhaazeDiscord:"PhaazebotDiscord" = cls.Web.BASE.Discord
	Guild:discord.Guild = discord.utils.get(PhaazeDiscord.guilds, id=int(guild_id))
	if not Guild:
		return await apiDiscordGuildUnknown(cls, WebRequest)

	# get user info
	DiscordUser:DiscordUserInfo = await cls.getDiscordUserInfo(WebRequest)
	if not DiscordUser.found:
		return await apiMissingAuthorisation(cls, WebRequest)

	# get member
	CheckMember:discord.Member = Guild.get_member(int(DiscordUser.user_id))
	if not CheckMember:
		return await apiDiscordMemberNotFound(cls, WebRequest, guild_id=guild_id, user_id=DiscordUser.user_id)

	# check permissions
	if not (CheckMember.guild_permissions.administrator or CheckMember.guild_permissions.manage_guild):
		return await apiDiscordMissingPermission(cls, WebRequest, guild_id=guild_id, user_id=DiscordUser.user_id)

	Configs:DiscordServerSettings = await getDiscordSeverSettings(PhaazeDiscord, origin=guild_id, prevent_new=True)

	if not Configs:
		return await apiDiscordGuildUnknown(cls, WebRequest, msg="Could not find configs for this guild")

	conf:dict = dict(
		autorole = None,
		blacklist_ban_links = Configs.blacklist_ban_links,
		blacklist_whitelistroles = Configs.blacklist_whitelistroles,
		blacklist_whitelistlinks = Configs.blacklist_whitelistlinks,
		blacklist_blacklistwords = Configs.blacklist_blacklistwords,
		blacklist_punishment = Configs.blacklist_punishment,
		currency_name = Configs.currency_name,
		currency_name_multi = Configs.currency_name_multi,
		disabled_levelchannels = Configs.disabled_levelchannels,
		disabled_quotechannels = Configs.disabled_quotechannels,
		disabled_normalchannels = Configs.disabled_normalchannels,
		disabled_regularchannels = Configs.disabled_regularchannels,
		enabled_gamechannels = Configs.enabled_gamechannels,
		enabled_nsfwchannels = Configs.enabled_nsfwchannels,
		level_announce_chan = Configs.level_announce_chan,
		level_custom_msg = Configs.level_custom_msg,
		leave_msg = Configs.leave_msg,
		leave_chan = Configs.leave_chan,
		owner_disable_level = Configs.owner_disable_level,
		owner_disable_normal = Configs.owner_disable_normal,
		owner_disable_regular = Configs.owner_disable_regular,
		owner_disable_mod = Configs.owner_disable_mod,
		track_channel = Configs.track_channel,
		track_options = Configs.track_options,
		welcome_chan = Configs.welcome_chan,
		welcome_msg = Configs.welcome_msg,
		welcome_msg_priv = Configs.welcome_msg_priv,
	)

	return cls.response(
		text=json.dumps( dict(result=conf, status=200) ),
		content_type="application/json",
		status=200
	)
