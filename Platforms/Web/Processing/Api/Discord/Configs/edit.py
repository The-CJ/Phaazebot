from typing import TYPE_CHECKING, Coroutine
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex
	from Platforms.Discord.main_discord import PhaazebotDiscord

import json
import asyncio
import discord
from aiohttp.web import Response, Request
from Utils.Classes.discordserversettings import DiscordServerSettings
from Utils.Classes.discordwebuser import DiscordWebUserInfo
from Utils.Classes.webrequestcontent import WebRequestContent
from Utils.Classes.undefined import UNDEFINED
from Utils.dbutils import validateDBInput
from Platforms.Discord.db import getDiscordSeverSettings
from Platforms.Discord.utils import getDiscordRoleFromString, getDiscordChannelFromString
from Platforms.Discord.logging import loggingOnConfigEdit
from Platforms.Discord.punish import checkPunishmentString
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

	value:str = Data.getStr("autorole_id", UNDEFINED, len_max=128)
	if value != UNDEFINED:
		error:bool = False
		if not value:
			value = None
		else:
			Role:discord.Role = getDiscordRoleFromString(PhaazeDiscord, Guild, value)
			if not Role:
				error = True
			elif Role >= Guild.me.top_role:
				return await apiWrongData(cls, WebRequest, msg=f"The Role `{Role.name}` is to high")
			else:
				value = str(Role.id)

		if error:
			return await apiWrongData(cls, WebRequest, msg=f"'{value}' could not be resolved as a valid discord role")

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
		value = checkPunishmentString(value)
		db_update["blacklist_punishment"] = validateDBInput(str, value)
		update["blacklist_punishment"] = value

	# currency_name
	value:str = Data.getStr("currency_name", UNDEFINED, len_max=256)
	if value != UNDEFINED:
		if not value: value = None
		db_update["currency_name"] = validateDBInput(str, value, allow_null=True)
		update["currency_name"] = value

	# currency_name_multi
	value:str = Data.getStr("currency_name_multi", UNDEFINED, len_max=256)
	if value != UNDEFINED:
		if not value: value = None
		db_update["currency_name_multi"] = validateDBInput(str, value, allow_null=True)
		update["currency_name_multi"] = value

	# leave_chan
	value:str = Data.getStr("leave_chan", UNDEFINED, len_max=128)
	if value != UNDEFINED:
		error:bool = False
		if not value:
			value = None
		else:
			Chan:discord.TextChannel = getDiscordChannelFromString(PhaazeDiscord, Guild, value, required_type="text")
			if not Chan:
				error = True
			else:
				value = str(Chan.id)

		if error:
			return await apiWrongData(cls, WebRequest, msg=f"'{value}' could not be resolved as a valid discord text channel")

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
	value:str = Data.getStr("level_announce_chan", UNDEFINED, len_max=128)
	if value != UNDEFINED:
		error:bool = False
		if not value: value = None
		else:
			Chan:discord.TextChannel = getDiscordChannelFromString(PhaazeDiscord, Guild, value, required_type="text")
			if not Chan:
				error = True
			else:
				value = str(Chan.id)

		if error:
			return await apiWrongData(cls, WebRequest, msg=f"'{value}' could not be resolved as a valid discord text channel")

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

	# track_channel
	value:str = Data.getStr("track_channel", UNDEFINED, len_max=128)
	if value != UNDEFINED:
		error:bool = False
		if not value: value = None
		else:
			Chan:discord.TextChannel = getDiscordChannelFromString(PhaazeDiscord, Guild, value, required_type="text")
			if not Chan:
				error = True
			else:
				value = str(Chan.id)

		if error:
			return await apiWrongData(cls, WebRequest, msg=f"'{value}' could not be resolved as a valid discord text channel")

		db_update["track_channel"] = validateDBInput(str, value, allow_null=True)
		update["track_channel"] = value

	# track_value
	value:str = Data.getInt("track_value", UNDEFINED, min_x=0)
	if value != UNDEFINED:
		db_update["track_value"] = validateDBInput(int, value)
		update["track_value"] = value

	# welcome_chan
	value:str = Data.getStr("welcome_chan", UNDEFINED, len_max=128)
	if value != UNDEFINED:
		error:bool = False
		if not value: value = None
		else:
			Chan:discord.TextChannel = getDiscordChannelFromString(PhaazeDiscord, Guild, value, required_type="text")
			if not Chan:
				error = True
			else:
				value = str(Chan.id)

		if error:
			return await apiWrongData(cls, WebRequest, msg=f"'{value}' could not be resolved as a valid discord text channel")

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

	cls.Web.BASE.PhaazeDB.updateQuery(
		table = "discord_setting",
		content = db_update,
		where = "`discord_setting`.`guild_id` = %s",
		where_values = (guild_id,)
	)

	# logging
	log_coro:Coroutine = loggingOnConfigEdit(PhaazeDiscord, Configs, Editor=CheckMember, changes=update)
	asyncio.ensure_future(log_coro, loop=cls.Web.BASE.DiscordLoop)

	cls.Web.BASE.Logger.debug(f"(API/Discord) Configs: {guild_id=} updated", require="discord:configs")
	return cls.response(
		text=json.dumps( dict(msg="Configs: Updated", changes=update, status=200) ),
		content_type="application/json",
		status=200
	)
