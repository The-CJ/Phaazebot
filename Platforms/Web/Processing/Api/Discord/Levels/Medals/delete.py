from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex
	from Platforms.Discord.main_discord import PhaazebotDiscord

import json
import discord
from aiohttp.web import Response, Request
from Utils.Classes.webrequestcontent import WebRequestContent
from Platforms.Web.Processing.Api.errors import apiMissingData
from Platforms.Discord.utils import getDiscordUsersMedals
from Utils.Classes.discordwebuserinfo import DiscordWebUserInfo
from Utils.Classes.discordusermedal import DiscordUserMedal
from Platforms.Web.Processing.Api.errors import apiMissingAuthorisation
from Platforms.Web.Processing.Api.Discord.errors import apiDiscordGuildUnknown, apiDiscordMemberNotFound, apiDiscordMissingPermission
from .errors import apiDiscordUserMedalNotExists

async def apiDiscordLevelsMedalsDelete(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
		Default url: /api/discord/levels/medals/delete
	"""
	Data:WebRequestContent = WebRequestContent(WebRequest)
	await Data.load()

	# get required vars
	guild_id:str = Data.getStr("guild_id", "", must_be_digit=True)
	member_id:str = Data.getStr("member_id", "", must_be_digit=True)
	medal_id:str = Data.getStr("medal_id", "", must_be_digit=True)
	name:str = Data.getStr("name", "", len_max=512)

	# checks
	if not guild_id:
		return await apiMissingData(cls, WebRequest, msg="missing or invalid 'guild_id'")

	if not member_id:
		return await apiMissingData(cls, WebRequest, msg="missing or invalid 'member_id'")

	if (not medal_id) and (not name):
		return await apiMissingData(cls, WebRequest, msg="missing or invalid 'medal_id' or 'name'")

	PhaazeDiscord:"PhaazebotDiscord" = cls.Web.BASE.Discord
	Guild:discord.Guild = discord.utils.get(PhaazeDiscord.guilds, id=int(guild_id))
	if not Guild:
		return await apiDiscordGuildUnknown(cls, WebRequest)

	# get medal
	res_medal:list = await getDiscordUsersMedals(cls.Web.BASE.Discord, guild_id, member_id=member_id, medal_id=medal_id, name=name)

	if not res_medal:
		return await apiDiscordUserMedalNotExists(cls, WebRequest, name=name, medal_id=medal_id)

	MedalToDelete:DiscordUserMedal = res_medal.pop(0)

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

	cls.Web.BASE.PhaazeDB.deleteQuery("""
		DELETE FROM `discord_user_medal` WHERE `guild_id` = %s AND `id` = %s""",
		(MedalToDelete.guild_id, MedalToDelete.medal_id)
	)

	cls.Web.BASE.Logger.debug(f"(API/Discord) Medal: {guild_id=} deleted [{medal_id=}, {name=}]", require="discord:medals")
	return cls.response(
		text=json.dumps( dict(msg="Medal: Deleted entry", deleted=MedalToDelete.name, status=200) ),
		content_type="application/json",
		status=200
	)
