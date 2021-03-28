from typing import TYPE_CHECKING, List, Union
if TYPE_CHECKING:
	from Platforms.Discord.main_discord import PhaazebotDiscord
	from Platforms.Web.main_web import PhaazebotWeb

import json
import discord
from aiohttp.web import Response
from Utils.Classes.extendedrequest import ExtendedRequest
from Utils.Classes.webrequestcontent import WebRequestContent
from Platforms.Web.index import PhaazeWebIndex

@PhaazeWebIndex.view("/api/discord/guild")
async def apiDiscordGuild(cls:"PhaazebotWeb", WebRequest:ExtendedRequest) -> Response:
	"""
	Default url: /api/discord/guild
	"""
	PhaazeDiscord:"PhaazebotDiscord" = cls.BASE.Discord
	if not PhaazeDiscord:
		return await cls.Tree.Api.errors.apiNotAllowed(cls, WebRequest, msg="Discord module is not active")

	Data:WebRequestContent = WebRequestContent(WebRequest)
	await Data.load()

	guild_id:str = Data.getStr("guild_id", "", must_be_digit=True)
	if not guild_id:
		return await cls.Tree.Api.errors.apiMissingData(cls, WebRequest, msg="invalid or missing 'guild_id'")

	Guild:discord.Guild = discord.utils.get(PhaazeDiscord.guilds, id=int(guild_id))

	if not Guild:
		return await cls.Tree.Api.Discord.errors.apiDiscordGuildUnknown(cls, WebRequest)

	res:List[dict] = cls.BASE.PhaazeDB.selectQuery("""
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
		id=str(Guild.id),
		name=Guild.name,
		owner_id=str(Guild.owner_id),
		icon=Guild.icon,
		banner=Guild.banner,
		description=Guild.description,
		features=Guild.features,
		splash=Guild.splash,
		premium_tier=Guild.premium_tier,
		premium_subscription_count=Guild.premium_subscription_count,
		member_count=Guild.member_count,
		channel_count=len(Guild.channels),
		channels=getAPIChannelList(Guild.channels),
		role_count=len(Guild.roles),
		roles=getAPIRoleList(Guild.roles),
		command_count=stats_info.get("command_count", 0),
		regular_count=stats_info.get("regular_count", 0),
		quote_count=stats_info.get("quote_count", 0),
		twitch_alert_count=stats_info.get("twitch_alert_count", 0),
		level_count=stats_info.get("level_count", 0)
	)

	return cls.response(
		body=json.dumps(dict(result=result, status=200)),
		status=200,
		content_type='application/json'
	)

def getAPIRoleList(discord_roles:List[discord.Role]) -> List[dict]:
	formatted_roles:List[dict] = []

	for Role in discord_roles:
		role_dict:dict = dict(id=str(Role.id), name=Role.name)

		role_dict["managed"] = True if Role.managed else False

		formatted_roles.append(role_dict)

	return formatted_roles

def getAPIChannelList(discord_channels:List[Union[discord.TextChannel, discord.VoiceChannel, discord.CategoryChannel, discord.abc.GuildChannel]]) -> List[dict]:
	formatted_channels:List[dict] = []

	for Channel in discord_channels:
		channel_dict:dict = dict(id=str(Channel.id), name=Channel.name)

		if type(Channel) is discord.TextChannel:
			channel_dict["channel_type"] = "text"

		elif type(Channel) is discord.VoiceChannel:
			channel_dict["channel_type"] = "voice"

		elif type(Channel) is discord.CategoryChannel:
			channel_dict["channel_type"] = "category"

		else:
			channel_dict["channel_type"] = "unknown"

		formatted_channels.append(channel_dict)

	return formatted_channels
