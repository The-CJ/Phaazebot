from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex
	from Platforms.Discord.main_discord import PhaazebotDiscord

import json
import discord
from aiohttp.web import Response, Request
from Utils.Classes.webrequestcontent import WebRequestContent
from Utils.Classes.discordwebuserinfo import DiscordWebUserInfo
from Platforms.Web.Processing.Api.errors import	apiMissingAuthorisation, apiMissingData, apiWrongData
from Platforms.Web.Processing.Api.Discord.errors import (
	apiDiscordGuildUnknown,
	apiDiscordMemberNotFound,
	apiDiscordMissingPermission
)

async def apiDiscordConfigsBlacklistedWordsCreate(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
		Default url: /api/discord/configs/blacklistedwords/create
	"""
	Data:WebRequestContent = WebRequestContent(WebRequest)
	await Data.load()

	# get required stuff
	guild_id:str = Data.getStr("guild_id", "", must_be_digit=True)
	word:str = Data.getStr("word", "").replace(";;;", "") # ;;; is the sql sepperator

	# checks
	if not guild_id:
		return await apiMissingData(cls, WebRequest, msg="missing or invalid 'guild_id'")

	if not word:
		return await apiMissingData(cls, WebRequest, msg="missing field 'word'")

	PhaazeDiscord:"PhaazebotDiscord" = cls.Web.BASE.Discord
	Guild:discord.Guild = discord.utils.get(PhaazeDiscord.guilds, id=int(guild_id))
	if not Guild:
		return await apiDiscordGuildUnknown(cls, WebRequest)

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

	# check if already exists
	res:list = cls.Web.BASE.PhaazeDB.selectQuery("""
		SELECT COUNT(*) AS `match`
		FROM `discord_blacklist_blacklistword`
		WHERE `discord_blacklist_blacklistword`.`guild_id` = %s
			AND LOWER(`discord_blacklist_blacklistword`.`word`) = LOWER(%s)""",
		( guild_id, word )
	)

	if res[0]["match"]:
			return await apiWrongData(cls, WebRequest, msg=f"'{word}' is already added")

	cls.Web.BASE.PhaazeDB.insertQuery(
		table = "discord_blacklist_blacklistword",
		content = {
			"guild_id": guild_id,
			"word": word
		}
	)

	cls.Web.BASE.Logger.debug(f"(API/Discord) Wordblacklist: {guild_id=} added: {word=}", require="discord:configs")
	return cls.response(
		text=json.dumps( dict(msg="Wordblacklist: Added new entry", entry=word, status=200) ),
		content_type="application/json",
		status=200
	)
