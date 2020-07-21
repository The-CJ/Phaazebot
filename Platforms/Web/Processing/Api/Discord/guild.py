from typing import TYPE_CHECKING, List
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex
	from Platforms.Discord.main_discord import PhaazebotDiscord

import json
import discord
from aiohttp.web import Response, Request
from Utils.Classes.webrequestcontent import WebRequestContent
from Platforms.Web.Processing.Api.errors import apiNotAllowed, apiMissingData
from Platforms.Web.Processing.Api.Discord.errors import apiDiscordGuildUnknown

async def apiDiscordGuild(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
	Default url: /api/discord/guild
	"""
	PhaazeDiscord:"PhaazebotDiscord" = cls.Web.BASE.Discord
	if not PhaazeDiscord: return await apiNotAllowed(cls, WebRequest, msg="Discord module is not active")

	Data:WebRequestContent = WebRequestContent(WebRequest)
	await Data.load()

	guild_id:str = Data.getStr("guild_id", "", must_be_digit=True)
	if not guild_id:
		return await apiMissingData(cls, WebRequest, msg="invalid or missing 'guild_id'")

	Guild:discord.Guild = discord.utils.get(PhaazeDiscord.guilds, id=int(guild_id))

	if not Guild:
		return await apiDiscordGuildUnknown(cls, WebRequest)

	res:List[dict] = cls.Web.BASE.PhaazeDB.selectQuery("""
		SELECT
			(SELECT COUNT(*) FROM `discord_regular` WHERE `discord_regular`.`guild_id` = %(guild_id)s) AS `regular_count`,
			(SELECT COUNT(*) FROM `discord_user` WHERE `discord_user`.`guild_id` = %(guild_id)s) AS `level_count`,
			(SELECT COUNT(*) FROM `discord_command` WHERE `discord_command`.`guild_id` = %(guild_id)s) AS `command_count`,
			(SELECT COUNT(*) FROM `discord_quote` WHERE `discord_quote`.`guild_id` = %(guild_id)s) AS `quote_count`,
			(SELECT COUNT(*) FROM `discord_twitch_alert` WHERE `discord_twitch_alert`.`discord_guild_id` = %(guild_id)s) AS `twitch_alert_count`""",
		{"guild_id": guild_id}
	)
	stats_info:dict = res.pop(0)

	result:dict = dict(
		id = str(Guild.id),
		name = Guild.name,
		owner_id = str(Guild.owner_id),
		icon = Guild.icon,
		banner = Guild.banner,
		description = Guild.description,
		features = Guild.features,
		splash = Guild.splash,
		premium_tier = Guild.premium_tier,
		premium_subscription_count = Guild.premium_subscription_count,
		member_count = Guild.member_count,
		channel_count = len(Guild.channels),
		channels = getAPIChannelList(Guild.channels),
		role_count = len(Guild.roles),
		roles = getAPIRoleList(Guild.roles),
		command_count = stats_info.get("command_count", 0),
		regular_count = stats_info.get("regular_count", 0),
		quote_count = stats_info.get("quote_count", 0),
		twitch_alert_count = stats_info.get("twitch_alert_count", 0),
		level_count = stats_info.get("level_count", 0)
	)

	return cls.response(
		body=json.dumps(dict(result=result, status=200)),
		status=200,
		content_type='application/json'
	)

def getAPIRoleList(discord_roles:List[discord.Role]) -> List[dict]:
	formated_roles:List[dict] = []

	for Role in discord_roles:
		role_dict:dict = dict( id=str(Role.id), name=Role.name )

		role_dict["managed"] = True if Role.managed else False

		formated_roles.append(role_dict)

	return formated_roles

def getAPIChannelList(discord_channels:List[discord.Channel]) -> List[dict]:
	formated_channels:List[dict] = []

	for Channel in discord_channels:
		channel_dict:dict = dict( id=str(Channel.id), name=Channel.name )

		if type(Channel) is discord.TextChannel:
			channel_dict["channel_type"] = "text"

		elif type(Channel) is discord.VoiceChannel:
			channel_dict["channel_type"] = "voice"

		elif type(Channel) is discord.CategoryChannel:
			channel_dict["channel_type"] = "category"

		else:
			channel_dict["channel_type"] = "unknown"

		formated_channels.append(channel_dict)

	return formated_channels
