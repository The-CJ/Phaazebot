from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex
	from Platforms.Discord.main_discord import PhaazebotDiscord

import json
import discord
from aiohttp.web import Response, Request
from Utils.Classes.webrequestcontent import WebRequestContent
from Utils.Classes.discordwebuserinfo import DiscordWebUserInfo
from Utils.Classes.discordblacklistedword import DiscordBlacklistedWord
from Platforms.Discord.db import getDiscordServerBlacklistedWords
from Platforms.Web.Processing.Api.errors import (
	apiMissingAuthorisation,
	apiMissingData
)
from Platforms.Web.Processing.Api.Discord.errors import (
	apiDiscordGuildUnknown,
	apiDiscordMemberNotFound,
	apiDiscordMissingPermission
)

from .errors import apiDiscordBlacklistWordNotExists

async def apiDiscordConfigsBlacklistedWordsDelete(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
		Default url: /api/discord/configs/blacklistedwords/create
	"""
	Data:WebRequestContent = WebRequestContent(WebRequest)
	await Data.load()

	# get required stuff
	guild_id:str = Data.getStr("guild_id", "", must_be_digit=True)
	word_id:str = Data.getStr("word_id", "", must_be_digit=True)
	word:str = Data.getStr("word", "")

	# checks
	if not guild_id:
		return await apiMissingData(cls, WebRequest, msg="missing or invalid 'guild_id'")

	if (not word_id) and (not word):
		return await apiMissingData(cls, WebRequest, msg="missing or invalid 'word' or 'word_id'")

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

	# get assign roles
	res_words:list = await getDiscordServerBlacklistedWords(cls.Web.BASE.Discord, guild_id, word_id=word_id, word=word)

	if not res_words:
		return await apiDiscordBlacklistWordNotExists(cls, WebRequest, word_id=word_id, word=word)

	WordToDelete:DiscordBlacklistedWord = res_words.pop(0)

	cls.Web.BASE.PhaazeDB.deleteQuery("""
		DELETE FROM `discord_blacklist_blacklistword` WHERE `guild_id` = %s AND `id` = %s""",
		(WordToDelete.guild_id, WordToDelete.word_id)
	)

	cls.Web.BASE.Logger.debug(f"(API/Discord) Wordblacklist: {guild_id=} deleted [{word=}, {word_id=}]", require="discord:configs")
	return cls.response(
		text=json.dumps( dict(msg=f"Wordblacklist: Deleted entry", deleted=WordToDelete.word, status=200) ),
		content_type="application/json",
		status=200
	)
