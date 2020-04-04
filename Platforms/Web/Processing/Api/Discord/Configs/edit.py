from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex
	from Platforms.Discord.main_discord import PhaazebotDiscord

import json
import discord
from aiohttp.web import Response, Request
from Utils.Classes.webrequestcontent import WebRequestContent
from Utils.Classes.discordserversettings import DiscordServerSettings
from Utils.Classes.discordwebuserinfo import DiscordWebUserInfo
from Utils.Classes.undefined import UNDEFINED
from Utils.dbutils import validateDBInput
from Platforms.Discord.utils import getDiscordSeverSettings, getDiscordRoleFromString, getDiscordChannelFromString
from Platforms.Discord.blacklist import checkBlacklistPunishmentString
from Platforms.Web.Processing.Api.errors import (
	apiMissingData,
	apiWrongData,
	apiMissingAuthorisation
)
from Platforms.Web.Processing.Api.Discord.errors import (
	apiDiscordGuildUnknown,
	apiDiscordMemberNotFound,
	apiDiscordMissingPermission
)

async def apiDiscordConfigsEdit(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
		Default url: /api/discord/configs/edit
	"""
	Data:WebRequestContent = WebRequestContent(WebRequest)
	await Data.load()

	# get required stuff
	guild_id:str = Data.getStr("guild_id", "", must_be_digit=True)

	# checks
	if not guild_id:
		return await apiMissingData(cls, WebRequest, msg="missing or invalid 'guild_id'")

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

	Configs:DiscordServerSettings = await getDiscordSeverSettings(PhaazeDiscord, origin=guild_id, prevent_new=True)

	if not Configs:
		return await apiDiscordGuildUnknown(cls, WebRequest, msg="Could not find configs for this guild")

	update:dict = dict()
	db_update:dict = dict()

	# get all changed stuff and add changes to list
	# changes is for the user, so return with types, db_changes is with, well... db values
	# e.g.:
	# update["x"] = true
	# db_update["x"] = "1"

	value:str = Data.getStr("autorole_id", UNDEFINED)
	if value != UNDEFINED:
		error:bool = False
		if not value: value = None
		elif value.isdigit():
			Role:discord.Role = getDiscordRoleFromString(PhaazeDiscord, Guild, value)
			if not Role:
				error = True
			elif Role >= Guild.me.top_role:
				return await apiWrongData(cls, WebRequest, msg=f"The Role `{Role.name}` is to high")
			else:
				value = str(Role.id)
		else:
			error = True

		if error:
			return await apiWrongData(cls, WebRequest, msg=f"'{value}' could not be resolved as a valid discord role id")

		db_update["autorole_id"] = validateDBInput(str, value, allow_null=True)
		update["autorole_id"] = value

	# blacklist_ban_links
	value:bool = Data.getBool("blacklist_ban_links", UNDEFINED)
	if value != UNDEFINED:
		db_update["blacklist_ban_links"] = validateDBInput(bool, value)
		update["blacklist_ban_links"] = value

	# blacklist_punishment
	value:str = Data.getStr("blacklist_punishment", UNDEFINED, len_max=32)
	if value != UNDEFINED:
		value = checkBlacklistPunishmentString(value)
		db_update["blacklist_punishment"] = validateDBInput(str, value)
		update["blacklist_punishment"] = value

	# leave_chan
	value:str = Data.getStr("leave_chan", UNDEFINED)
	if value != UNDEFINED:
		error:bool = False
		if not value: value = None
		elif value.isdigit():
			Chan:discord.abc.Messageable = discord.utils.get(Guild.channels, id=int(value))
			if type(Chan) != discord.TextChannel:
				error = True
			else:
				value = str(Chan.id)
		else:
			error = True

		if error:
			return await apiWrongData(cls, WebRequest, msg=f"'{value}' could not be resolved as a valid discord text channel id")

		db_update["leave_chan"] = validateDBInput(str, value, allow_null=True)
		update["leave_chan"] = value

	# leave_msg
	value:str = Data.getStr("leave_msg", UNDEFINED, len_max=1750)
	if value != UNDEFINED:
		if not value: value = None
		db_update["leave_msg"] = validateDBInput(str, value, allow_null=True)
		update["leave_msg"] = value

	# level_custom_msg
	value:str = Data.getStr("level_custom_msg", UNDEFINED, len_max=1750)
	if value != UNDEFINED:
		if not value: value = None
		db_update["level_custom_msg"] = validateDBInput(str, value, allow_null=True)
		update["level_custom_msg"] = value

	# level_announce_chan
	value:str = Data.getStr("level_announce_chan", UNDEFINED)
	if value != UNDEFINED:
		error:bool = False
		if not value: value = None
		elif value.isdigit():
			Chan:discord.abc.Messageable = discord.utils.get(Guild.channels, id=int(value))
			if type(Chan) != discord.TextChannel:
				error = True
			else:
				value = str(Chan.id)
		else:
			error = True

		if error:
			return await apiWrongData(cls, WebRequest, msg=f"'{value}' could not be resolved as a valid discord text channel id")

		db_update["level_announce_chan"] = validateDBInput(str, value, allow_null=True)
		update["level_announce_chan"] = value

	# owner_disable_level
	value:bool = Data.getBool("owner_disable_level", UNDEFINED)
	if value != UNDEFINED:
		if not Guild.owner == CheckMember:
			return await apiDiscordMissingPermission(cls, WebRequest, guild_id=guild_id, user_id=DiscordUser.user_id, msg="changing 'owner_disable_level' require server owner")
		db_update["owner_disable_level"] = validateDBInput(bool, value)
		update["owner_disable_level"] = value

	# owner_disable_normal
	value:bool = Data.getBool("owner_disable_normal", UNDEFINED)
	if value != UNDEFINED:
		if not Guild.owner == CheckMember:
			return await apiDiscordMissingPermission(cls, WebRequest, guild_id=guild_id, user_id=DiscordUser.user_id, msg="changing 'owner_disable_normal' require server owner")
		db_update["owner_disable_normal"] = validateDBInput(bool, value)
		update["owner_disable_normal"] = value

	# owner_disable_regular
	value:bool = Data.getBool("owner_disable_regular", UNDEFINED)
	if value != UNDEFINED:
		if not Guild.owner == CheckMember:
			return await apiDiscordMissingPermission(cls, WebRequest, guild_id=guild_id, user_id=DiscordUser.user_id, msg="changing 'owner_disable_regular' require server owner")
		db_update["owner_disable_regular"] = validateDBInput(bool, value)
		update["owner_disable_regular"] = value

	# owner_disable_mod
	value:bool = Data.getBool("owner_disable_mod", UNDEFINED)
	if value != UNDEFINED:
		if not Guild.owner == CheckMember:
			return await apiDiscordMissingPermission(cls, WebRequest, guild_id=guild_id, user_id=DiscordUser.user_id, msg="changing 'owner_disable_mod' require server owner")
		db_update["owner_disable_mod"] = validateDBInput(bool, value)
		update["owner_disable_mod"] = value

	# welcome_chan
	value:str = Data.getStr("welcome_chan", UNDEFINED)
	if value != UNDEFINED:
		error:bool = False
		if not value: value = None
		elif value.isdigit():
			Chan:discord.abc.Messageable = discord.utils.get(Guild.channels, id=int(value))
			if type(Chan) != discord.TextChannel:
				error = True
			else:
				value = str(Chan.id)
		else:
			error = True

		if error:
			return await apiWrongData(cls, WebRequest, msg=f"'{value}' could not be resolved as a valid discord text channel id")

		db_update["welcome_chan"] = validateDBInput(str, value, allow_null=True)
		update["welcome_chan"] = value

	# welcome_msg
	value:str = Data.getStr("welcome_msg", UNDEFINED, len_max=1750)
	if value != UNDEFINED:
		if not value: value = None
		db_update["welcome_msg"] = validateDBInput(str, value, allow_null=True)
		update["welcome_msg"] = value

	# welcome_msg_priv
	value:str = Data.getStr("welcome_msg_priv", UNDEFINED, len_max=1750)
	if value != UNDEFINED:
		if not value: value = None
		db_update["welcome_msg_priv"] = validateDBInput(str, value, allow_null=True)
		update["welcome_msg_priv"] = value

	if not db_update:
		return await apiMissingData(cls, WebRequest, msg="No changes, please add at least one")

	cls.Web.BASE.Logger.debug(f"(API/Discord) Configs: {guild_id=} updated", require="discord:configs")
	cls.Web.BASE.PhaazeDB.updateQuery(
		table = "discord_setting",
		content = db_update,
		where = "discord_setting.guild_id = %s",
		where_values = (guild_id,)
	)

	return cls.response(
		text=json.dumps( dict(msg="Configs: Updated", update=update, status=200) ),
		content_type="application/json",
		status=200
	)
