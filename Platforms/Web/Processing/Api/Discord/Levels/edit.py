from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex
	from Platforms.Discord.main_discord import PhaazebotDiscord

import json
import discord
from aiohttp.web import Response, Request
from Utils.Classes.webrequestcontent import WebRequestContent
from Platforms.Discord.utils import getDiscordServerUsers
from Utils.dbutils import validateDBInput
from Utils.Classes.discordwebuserinfo import DiscordWebUserInfo
from Utils.Classes.discorduserstats import DiscordUserStats
from Utils.Classes.undefined import UNDEFINED
from Platforms.Web.Processing.Api.errors import (
	apiMissingAuthorisation,
	apiMissingData,
	apiWrongData
)
from Platforms.Web.Processing.Api.Discord.errors import (
	apiDiscordGuildUnknown,
	apiDiscordMemberNotFound,
	apiDiscordMissingPermission
)
from .errors import apiDiscordLevelMedalLimit

async def apiDiscordLevelsEdit(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
		Default url: /api/discord/levels/edit
	"""
	Data:WebRequestContent = WebRequestContent(WebRequest)
	await Data.load()

	# get required stuff
	guild_id:str = Data.getStr("guild_id", "", must_be_digit=True)
	member_id:str = Data.getStr("member_id", "", must_be_digit=True)

	# checks
	if not guild_id:
		return await apiMissingData(cls, WebRequest, msg="missing or invalid 'guild_id'")

	if not member_id:
		return await apiMissingData(cls, WebRequest, msg="missing or invalid 'member_id'")

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
	# to edit configs, at least moderator rights are needed, (there can be options that require server only duh)
	if not (CheckMember.guild_permissions.administrator or CheckMember.guild_permissions.manage_guild):
		return await apiDiscordMissingPermission(cls, WebRequest, guild_id=guild_id, user_id=DiscordUser.user_id)

	# get level user
	res_level:list = await getDiscordServerUsers(PhaazeDiscord, guild_id=guild_id, member_id=member_id)
	if not res_level:
		return await apiDiscordGuildUnknown(cls, WebRequest, msg="Could not find a level for this user")
	CurrentLevelUser:DiscordUserStats = res_level.pop(0)

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

	# currency
	value:int = Data.getInt("currency", UNDEFINED, min_x=0)
	if value != UNDEFINED:
		db_changes["currency"] = validateDBInput(int, value)
		changes["currency"] = value

	# exp
	value:int = Data.getInt("exp", UNDEFINED, min_x=0)
	if value != UNDEFINED:
		db_changes["exp"] = validateDBInput(int, value)
		changes["exp"] = value

		if value != 0:
			db_changes["edited"] = validateDBInput(bool, True)
			changes["edited"] = True
		else:
			db_changes["edited"] = validateDBInput(bool, False)
			changes["edited"] = False

	# on_server
	value:bool = Data.getBool("on_server", UNDEFINED)
	if value != UNDEFINED:
		if not Guild.owner == CheckMember:
			return await apiDiscordMissingPermission(cls, WebRequest, guild_id=guild_id, user_id=DiscordUser.user_id, msg="changing 'on_server' require server owner")

		db_changes["on_server"] = validateDBInput(bool, value)
		changes["on_server"] = value

	if not db_changes:
		return await apiMissingData(cls, WebRequest, msg="No changes, please add at least one")

	cls.Web.BASE.Logger.debug(f"(API/Discord) Level Update: S:{guild_id} M:{member_id} {str(db_changes)}", require="discord:levels")
	cls.Web.BASE.PhaazeDB.updateQuery(
		table = "discord_user",
		content = db_changes,
		where = "discord_user.guild_id = %s AND discord_user.member_id = %s",
		where_values = (guild_id, member_id)
	)

	return cls.response(
		text=json.dumps( dict(msg="level successfull updated", changes=changes, status=200) ),
		content_type="application/json",
		status=200
	)

async def singleActionMedal(cls:"WebIndex", WebRequest:Request, action:str, Data:WebRequestContent, CurrentLevelUser:DiscordUserStats) -> Response:
	"""
		Default url: /api/discord/levels/edit?medal_action=something
	"""
	guild_id:str = Data.getStr("guild_id", "")
	member_id:str = Data.getStr("member_id", "")

	action = action.lower()
	medal_name:str = Data.getStr("medal_name", "").strip(" ").strip("\n")

	if not guild_id:
		# should never happen
		return await apiMissingData(cls, WebRequest, msg="missing or invalid 'guild_id'")

	if not member_id:
		# should never happen
		return await apiMissingData(cls, WebRequest, msg="missing or invalid 'member_id'")

	if not medal_name:
		return await apiMissingData(cls, WebRequest, msg="missing 'medal_name'")

	if action == "add":
		if medal_name in CurrentLevelUser.medals:
			return await apiWrongData(cls, WebRequest, msg=f"'{medal_name}' is already added")

		if len(CurrentLevelUser.medals) >= cls.Web.BASE.Limit.DISCORD_LEVEL_MEDAL_AMOUNT:
			return await apiDiscordLevelMedalLimit(cls, WebRequest)

		cls.Web.BASE.PhaazeDB.insertQuery(
			table = "discord_user_medal",
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
		if medal_name not in CurrentLevelUser.medals:
			return await apiWrongData(cls, WebRequest, msg=f"can't remove '{medal_name}', is currently not added")

		cls.Web.BASE.PhaazeDB.deleteQuery("""
			DELETE FROM `discord_user_medal`
			WHERE `guild_id` = %s
				AND `member_id` = %s
				AND `name` = %s""",
			(guild_id, member_id, medal_name)
		)

		cls.Web.BASE.Logger.debug(f"(API/Discord) Level Medal Update: S:{guild_id} M:{member_id} - rem: {medal_name}", require="discord:level")
		return cls.response(
			text=json.dumps( dict(msg="level medals update successfull updated", rem=medal_name, status=200) ),
			content_type="application/json",
			status=200
		)

	else:
		return await apiWrongData(cls, WebRequest)
