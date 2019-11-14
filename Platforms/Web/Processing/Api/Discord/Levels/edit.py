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
from Utils.Classes.discordleveluser import DiscordLevelUser
from Platforms.Web.Processing.Api.errors import apiMissingAuthorisation
from Platforms.Web.Processing.Api.Discord.errors import apiDiscordGuildUnknown, apiDiscordMemberNotFound, apiDiscordMissingPermission
from Utils.dbutils import validateDBInput
from Utils.Classes.undefined import UNDEFINED

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

	CurrentLevelUser:DiscordLevelUser = level[0]

	# single actions
	action:str = Data.getStr("medal_action", UNDEFINED)
	if action:
		return await singleActionMedal(cls, WebRequest, action, Data, CurrentLevelUser)

	changes:dict = dict()
	db_changes:dict = dict()

	# get all changed stuff and add changes to list
	# changes is for the user, so return with types, db_changes is with, well... db values
	# e.g.:
	# changes["x"] = true
	# db_changes["x"] = "1"

	# exp
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

	if not db_changes:
		return await missingData(cls, WebRequest, msg="No changes, please add at least one")

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

async def singleActionMedal(cls:"WebIndex", WebRequest:Request, action:str, Data:WebRequestContent, CurrentLevelUser:DiscordLevelUser) -> Response:
	"""
		Default url: /api/discord/levels/edit?medal_action=something
	"""
	guild_id:str = Data.getStr("guild_id", "")
	member_id:str = Data.getStr("member_id", "")

	action = action.lower()
	medal_name:str = Data.getStr("medal_name", "").strip(" ").strip("\n")

	if not guild_id:
		# should never happen
		return await missingData(cls, WebRequest, msg="missing or invalid 'guild_id'")

	if not member_id:
		# should never happen
		return await missingData(cls, WebRequest, msg="missing or invalid 'member_id'")

	if action == "add":
		if medal_name in CurrentLevelUser.medals:
			return await apiWrongData(cls, WebRequest, msg=f"'{medal_name}' is already added")

		cls.Web.BASE.PhaazeDB.insertQuery(
			table = "discord_level_medal",
			content = {
				"guild_id": guild_id,
				"member_id": member_id,
				"name": medal_name
			}
		)

		cls.Web.BASE.Logger.debug(f"(API/Discord) Level Medal Update: S:{guild_id} M:{member_id} - add: {medal_name}", require="discord:level")
		return cls.response(
			text=json.dumps( dict(msg="level medals update successfull updated", add=medal_name, status=200) ),
			content_type="application/json",
			status=200
		)

	elif action == "remove":
		pass

	else:
		return await apiWrongData(cls, WebRequest)
