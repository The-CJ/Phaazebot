from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex
	from Platforms.Discord.main_discord import PhaazebotDiscord

import json
import discord
from aiohttp.web import Response, Request
from Utils.Classes.webrequestcontent import WebRequestContent
from Utils.Classes.discordwebuserinfo import DiscordWebUserInfo
from Platforms.Web.Processing.Api.errors import apiMissingAuthorisation, apiMissingData
from Platforms.Web.Processing.Api.Discord.errors import apiDiscordGuildUnknown, apiDiscordMemberNotFound, apiDiscordMissingPermission
from Utils.Classes.undefined import UNDEFINED

async def apiDiscordTwitchalertsDelete(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
		Default url: /api/discord/twitchalerts/delete
	"""
	Data:WebRequestContent = WebRequestContent(WebRequest)
	await Data.load()

	# get required vars
	guild_id:str = Data.getStr("guild_id", UNDEFINED, must_be_digit=True)
	alert_id:int = Data.getInt("alert_id", UNDEFINED, min_x=1)

	# checks
	if not guild_id:
		return await apiMissingData(cls, WebRequest, msg="missing or invalid 'guild_id'")

	if not alert_id:
		return await apiMissingData(cls, WebRequest, msg="missing or invalid 'alert_id'")

	PhaazeDiscord:"PhaazebotDiscord" = cls.Web.BASE.Discord
	Guild:discord.Guild = discord.utils.get(PhaazeDiscord.guilds, id=int(guild_id))
	if not Guild:
		return await apiDiscordGuildUnknown(cls, WebRequest)

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

	cls.Web.BASE.PhaazeDB.deleteQuery("""
		DELETE FROM `discord_twitch_alert`
		WHERE `discord_twitch_alert`.`discord_guild_id` = %s
			AND `discord_twitch_alert`.`id` = %s""",
		(guild_id, alert_id)
	)

	cls.Web.BASE.Logger.debug(f"(API/Discord) Deleted alert: S:{guild_id} A:{alert_id}", require="discord:alert")

	return cls.response(
		text=json.dumps( dict(msg="alert successfull deleted", alert_id=alert_id, status=200) ),
		content_type="application/json",
		status=200
	)
