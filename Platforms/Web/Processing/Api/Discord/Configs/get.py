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

	guild_id:str = Data.get("guild_id")
	if not guild_id:
		return await missingData(cls, WebRequest, msg="missing 'guild_id'")

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
		ban_links = Configs.ban_links,
		ban_links_role = Configs.ban_links_role,
		ban_links_whitelist = Configs.ban_links_whitelist,
		blacklist_words = Configs.blacklist_words,
		blacklist_punishment = Configs.blacklist_punishment,
		currency_name = Configs.currency_name,
		currency_name_multi = Configs.currency_name_multi,
		disable_chan_level = Configs.disable_chan_level,
		disable_chan_normal = Configs.disable_chan_normal,
		disable_chan_quotes = Configs.disable_chan_quotes,
		enable_chan_game = Configs.enable_chan_game,
		enable_chan_nsfw = Configs.enable_chan_nsfw,
		level_announce_channel = Configs.level_announce_channel,
		level_custom_message = Configs.level_custom_message,
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
