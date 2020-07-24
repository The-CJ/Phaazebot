from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex
	from Platforms.Discord.main_discord import PhaazebotDiscord

import json
import discord
from aiohttp.web import Response, Request
from Utils.Classes.webrequestcontent import WebRequestContent
from Utils.Classes.discordwebuserinfo import DiscordWebUserInfo
from Platforms.Web.Processing.Api.errors import (
	apiMissingData,
	apiMissingAuthorisation
)
from Platforms.Web.Processing.Api.Discord.errors import (
	apiDiscordGuildUnknown,
	apiDiscordMemberNotFound,
	apiDiscordMissingPermission
)
from .errors import apiDiscordUserMedalExists, apiDiscordUserMedalLimit

async def apiDiscordLevelsMedalsCreate(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
		Default url: /api/discord/levels/medals/create
	"""
	Data:WebRequestContent = WebRequestContent(WebRequest)
	await Data.load()

	# get required stuff
	guild_id:str = Data.getStr("guild_id", "", must_be_digit=True)
	member_id:str = Data.getStr("member_id", "", must_be_digit=True)
	name:str = Data.getStr("name", "", len_max=512)

	# checks
	if not guild_id:
		return await apiMissingData(cls, WebRequest, msg="missing or invalid 'guild_id'")

	if not member_id:
		return await apiMissingData(cls, WebRequest, msg="missing or invalid 'member_id'")

	if not name:
		return await apiMissingData(cls, WebRequest, msg="missing or invalid 'name'")

	# get/check discord
	PhaazeDiscord:"PhaazebotDiscord" = cls.Web.BASE.Discord
	Guild:discord.Guild = discord.utils.get(PhaazeDiscord.guilds, id=int(guild_id))
	if not Guild:
		return await apiDiscordGuildUnknown(cls, WebRequest)

	# check limit
	res:list = cls.Web.BASE.PhaazeDB.selectQuery("""
		SELECT
			COUNT(*) AS `all`,
			SUM(
				CASE WHEN LOWER(`discord_user_medal`.`name`) = LOWER(%s)
				THEN 1 ELSE 0 END
			) AS `match`
		FROM `discord_user_medal`
		WHERE `discord_user_medal`.`guild_id` = %s
			AND `discord_user_medal`.`member_id` = %s""",
		( name, guild_id, member_id )
	)

	if res[0]['match']:
		return await apiDiscordUserMedalExists(cls, WebRequest)

	if res[0]['all'] >= cls.Web.BASE.Limit.DISCORD_LEVEL_MEDAL_AMOUNT:
		return await apiDiscordUserMedalLimit(cls, WebRequest)

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

	cls.Web.BASE.PhaazeDB.insertQuery(
		table="discord_user_medal",
		content={
			"guild_id": guild_id,
			"member_id": member_id,
			"name": name
		}
	)

	cls.Web.BASE.Logger.debug(f"(API/Discord) User medal: {guild_id=} {member_id=} added new entry", require="discord:medals")

	return cls.response(
		text=json.dumps( dict(msg="Medal: Added new entry", entry=name, status=200) ),
		content_type="application/json",
		status=200
	)
