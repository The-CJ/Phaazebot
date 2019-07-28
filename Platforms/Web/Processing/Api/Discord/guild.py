from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex
	from Platforms.Discord.main_discord import PhaazebotDiscord

import json
import discord
from aiohttp.web import Response, Request
from Utils.Classes.webrequestcontent import WebRequestContent
# from Utils.Classes.discorduserinfo import DiscordUserInfo
from ..errors import apiNotAllowed, missingData, apiWrongData # apiMissingAuthorisation

async def apiDiscordGuild(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
		Default url: /api/discord/guild
	"""
	PhaazeDiscord:"PhaazebotDiscord" = cls.Web.BASE.Discord
	if not PhaazeDiscord: return await apiNotAllowed(cls, WebRequest, msg="Discord module is not active")

	Data:WebRequestContent = WebRequestContent(WebRequest)
	await Data.load()

	guild_id:str = Data.get("guild_id")
	if not guild_id:
		return await missingData(cls, WebRequest, msg="missing 'guild_id'")

	if not guild_id.isdigit():
		return await apiWrongData(cls, WebRequest, msg="'guild_id' must be number")


	Guild:discord.Guild = discord.utils.get(PhaazeDiscord.guilds, id=int(guild_id))

	if not Guild:
		return cls.response(
			body=json.dumps(dict(msg="could not find a phaaze known guild", status=400)),
			status=400,
			content_type='application/json'
		)

	res:list = cls.Web.BASE.PhaazeDB.query("""
		SELECT
			(SELECT COUNT(*) FROM discord_level WHERE discord_level.guild_id = %s) AS level_count,
			(SELECT COUNT(*) FROM discord_command WHERE discord_command.guild_id = %s) AS command_count,
			(SELECT COUNT(*) FROM discord_quote WHERE discord_quote.guild_id = %s) AS quote_count,
			(SELECT COUNT(*) FROM discord_twitch_alert WHERE discord_twitch_alert.discord_guild_id = %s) AS twitch_alert_count""",
		(guild_id, guild_id, guild_id, guild_id)
	)
	stats_info:dict = res[0]

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
		role_count = len(Guild.roles),
		command_count = stats_info.get("command_count", 0),
		quote_count = stats_info.get("quote_count", 0),
		twitch_alert_count = stats_info.get("twitch_alert_count", 0),
		level_count = stats_info.get("level_count", 0)
	)

	return cls.response(
		body=json.dumps(dict(result=result, status=200)),
		status=200,
		content_type='application/json'
	)
