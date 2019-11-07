from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex
	from Platforms.Discord.main_discord import PhaazebotDiscord

import json
import discord
from aiohttp.web import Response, Request
from Utils.Classes.webrequestcontent import WebRequestContent
from Platforms.Web.Processing.Api.errors import missingData, apiWrongData
from Platforms.Discord.utils import getDiscordServerLevels
from Utils.Classes.discorduserinfo import DiscordUserInfo
from Platforms.Web.Processing.Api.errors import apiMissingAuthorisation
from Platforms.Web.Processing.Api.Discord.errors import apiDiscordGuildUnknown, apiDiscordMemberNotFound, apiDiscordMissingPermission
from Utils.dbutils import validateDBInput

async def apiDiscordLevelsEdit(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
		Default url: /api/discord/levels/edit
	"""
	Data:WebRequestContent = WebRequestContent(WebRequest)
	await Data.load()

	guild_id:str = Data.getStr("guild_id", "", must_be_digit=True)
	if not guild_id:
		return await missingData(cls, WebRequest, msg="missing or invalid 'guild_id'")

	member_id:str = Data.getStr("member_id", "", must_be_digit=True)
	if not member_id:
		return await missingData(cls, WebRequest, msg="missing or invalid 'member_id'")

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
	# to edit configs, at least moderator rights are needed, (there can be options that require server only duh)
	if not (CheckMember.guild_permissions.administrator or CheckMember.guild_permissions.manage_guild):
		return await apiDiscordMissingPermission(cls, WebRequest, guild_id=guild_id, user_id=DiscordUser.user_id)

	level:list = await getDiscordServerLevels(PhaazeDiscord, guild_id=guild_id, member_id=member_id)

	if not level:
		return await apiDiscordGuildUnknown(cls, WebRequest, msg="Could not find a level for this user")

	# single actions
	# action:str or Undefined = Data.getStr("wordblacklist_action", "")
	# if action:
	# 	return await singleActionWordBlacklist(cls, WebRequest, action, Data, Configs)
	#
	# action:str or Undefined = Data.getStr("linkwhitelist_action", "")
	# if action:
	# 	return await singleActionLinkWhitelist(cls, WebRequest, action, Data, Configs)
	#
	# action:str or Undefined = Data.getStr("exceptionrole_action", "")
	# if action:
	# 	return await singleActionExceptionRole(cls, WebRequest, action, Data, Configs, Guild)

	changes:dict = dict()
	db_changes:dict = dict()

	# get all changed stuff and add changes to list
	# changes is for the user, so return with types, db_changes is with, well... db values
	# e.g.:
	# changes["x"] = true
	# db_changes["x"] = "1"

	# ban_links
	value:int = Data.getInt("exp", None, min_x=0)
	if value != None:
		db_changes["exp"] = validateDBInput(int, value)
		changes["exp"] = value

		if value != 0:
			db_changes["edited"] = validateDBInput(bool, True)
			changes["edited"] = True
		else:
			db_changes["edited"] = validateDBInput(bool, False)
			changes["edited"] = False

	cls.Web.BASE.Logger.debug(f"(API/Discord) Level Update: S:{guild_id} M:{member_id} {str(db_changes)}", require="discord:levels")
	cls.Web.BASE.PhaazeDB.updateQuery(
		table = "discord_level",
		content = db_changes,
		where = "discord_level.guild_id = %s AND discord_level.member_id = %s",
		where_values = (guild_id, member_id)
	)

	return cls.response(
		text=json.dumps( dict(msg="level successfull updated", changes=changes, status=200) ),
		content_type="application/json",
		status=200
	)
