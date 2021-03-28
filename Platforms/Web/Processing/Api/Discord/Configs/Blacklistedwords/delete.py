from typing import TYPE_CHECKING, List
if TYPE_CHECKING:
	from Platforms.Discord.main_discord import PhaazebotDiscord
	from Platforms.Web.main_web import PhaazebotWeb

import json
import discord
from aiohttp.web import Response
from Utils.Classes.discordblacklistedword import DiscordBlacklistedWord
from Utils.Classes.authdiscordwebuser import AuthDiscordWebUser
from Utils.Classes.webrequestcontent import WebRequestContent
from Utils.Classes.extendedrequest import ExtendedRequest
from Utils.Classes.undefined import UNDEFINED
from Platforms.Discord.db import getDiscordServerBlacklistedWords
from Platforms.Web.utils import authDiscordWebUser
from Platforms.Web.Processing.Api.errors import apiMissingAuthorisation, apiMissingData

async def apiDiscordConfigsBlacklistedWordsDelete(cls:"PhaazebotWeb", WebRequest:ExtendedRequest) -> Response:
	"""
	Default url: /api/discord/configs/blacklistedwords/create
	"""
	Data:WebRequestContent = WebRequestContent(WebRequest)
	await Data.load()

	# get required stuff
	guild_id:str = Data.getStr("guild_id", UNDEFINED, must_be_digit=True)
	word_id:str = Data.getStr("word_id", UNDEFINED, must_be_digit=True)

	# checks
	if not guild_id:
		return await apiMissingData(cls, WebRequest, msg="missing or invalid 'guild_id'")

	if not word_id:
		return await apiMissingData(cls, WebRequest, msg="missing or invalid 'word_id'")

	PhaazeDiscord:"PhaazebotDiscord" = cls.BASE.Discord
	Guild:discord.Guild = discord.utils.get(PhaazeDiscord.guilds, id=int(guild_id))
	if not Guild:
		return await cls.Tree.Api.Discord.errors.apiDiscordGuildUnknown(cls, WebRequest)

	# get user info
	AuthDiscord:AuthDiscordWebUser = await authDiscordWebUser(cls, WebRequest)
	if not AuthDiscord.found:
		return await apiMissingAuthorisation(cls, WebRequest)

	# get member
	CheckMember:discord.Member = Guild.get_member(int(AuthDiscord.User.user_id))
	if not CheckMember:
		return await cls.Tree.Api.Discord.errors.apiDiscordMemberNotFound(cls, WebRequest, guild_id=guild_id, user_id=AuthDiscord.User.user_id)

	# check permissions
	if not (CheckMember.guild_permissions.administrator or CheckMember.guild_permissions.manage_guild):
		return await cls.Tree.Api.Discord.errors.apiDiscordMissingPermission(cls, WebRequest, guild_id=guild_id, user_id=AuthDiscord.User.user_id)

	# get assign roles
	res_words:List[DiscordBlacklistedWord] = await getDiscordServerBlacklistedWords(PhaazeDiscord, guild_id=guild_id, word_id=word_id)

	if not res_words:
		return await cls.Tree.Api.Discord.Configs.Blacklistedwords.errors.apiDiscordBlacklistWordNotExists(cls, WebRequest, word_id=word_id)

	WordToDelete:DiscordBlacklistedWord = res_words.pop(0)

	cls.BASE.PhaazeDB.deleteQuery("""
		DELETE FROM `discord_blacklist_blacklistword` WHERE `guild_id` = %s AND `id` = %s""",
		(WordToDelete.guild_id, WordToDelete.word_id)
	)

	cls.BASE.Logger.debug(f"(API/Discord) Wordblacklist: {guild_id=} deleted {word_id=}", require="discord:configs")
	return cls.response(
		text=json.dumps(dict(msg=f"Wordblacklist: Deleted entry", deleted=WordToDelete.word, status=200)),
		content_type="application/json",
		status=200
	)
