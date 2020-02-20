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
from Platforms.Discord.utils import getDiscordSeverSettings
from Platforms.Discord.blacklist import checkBlacklistPunishmentString
from Platforms.Web.Processing.Api.errors import (
	apiMissingData,
	apiWrongData,
	apiMissingAuthorisation
)
from Platforms.Web.Processing.Api.Discord.errors import (
	apiDiscordGuildUnknown,
	apiDiscordMemberNotFound,
	apiDiscordMissingPermission,
	apiDiscordRoleNotFound,
	apiDiscordChannelNotFound
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

	# single actions
	action:str = Data.getStr("wordblacklist_action", UNDEFINED)
	if action:
		return await singleActionWordBlacklist(cls, WebRequest, action, Data, Configs)

	action:str = Data.getStr("linkwhitelist_action", UNDEFINED)
	if action:
		return await singleActionLinkWhitelist(cls, WebRequest, action, Data, Configs)

	action:str = Data.getStr("exceptionrole_action", UNDEFINED)
	if action:
		return await singleActionExceptionRole(cls, WebRequest, action, Data, Configs, Guild)

	action:str = Data.getStr("disabled_levelchan_action", UNDEFINED)
	if action:
		return await singleActionDisableLevelChannel(cls, WebRequest, action, Data, Configs, Guild)

	action:str = Data.getStr("disabled_quotechan_action", UNDEFINED)
	if action:
		return await singleActionDisableQuoteChannel(cls, WebRequest, action, Data, Configs, Guild)

	action:str = Data.getStr("disabled_normalchan_action", UNDEFINED)
	if action:
		return await singleActionDisableNormalChannel(cls, WebRequest, action, Data, Configs, Guild)

	action:str = Data.getStr("disabled_regularchan_action", UNDEFINED)
	if action:
		return await singleActionDisableRegularChannel(cls, WebRequest, action, Data, Configs, Guild)

	action:str = Data.getStr("enabled_gamechan_action", UNDEFINED)
	if action:
		return await singleActionEnableGameChannel(cls, WebRequest, action, Data, Configs, Guild)

	action:str = Data.getStr("enabled_nsfwchan_action", UNDEFINED)
	if action:
		return await singleActionEnableNSFWChannel(cls, WebRequest, action, Data, Configs, Guild)

	update:dict = dict()
	db_update:dict = dict()

	# get all changed stuff and add changes to list
	# changes is for the user, so return with types, db_changes is with, well... db values
	# e.g.:
	# update["x"] = true
	# db_update["x"] = "1"

	# blacklist_ban_links
	value:bool = Data.getBool("blacklist_ban_links", UNDEFINED)
	if value != UNDEFINED:
		db_update["blacklist_ban_links"] = validateDBInput(bool, value)
		update["blacklist_ban_links"] = value

	# blacklist_punishment
	value:str = Data.getStr("blacklist_punishment", UNDEFINED)
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
	value:str = Data.getStr("leave_msg", UNDEFINED)
	if value != UNDEFINED:
		if not value: value = None
		db_update["leave_msg"] = validateDBInput(str, value, allow_null=True)
		update["leave_msg"] = value

	# level_custom_msg
	value:str = Data.getStr("level_custom_msg", UNDEFINED)
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
	value:str = Data.getStr("welcome_msg", UNDEFINED)
	if value != UNDEFINED:
		if not value: value = None
		db_update["welcome_msg"] = validateDBInput(str, value, allow_null=True)
		update["welcome_msg"] = value

	# welcome_msg_priv
	value:str = Data.getStr("welcome_msg_priv", UNDEFINED)
	if value != UNDEFINED:
		if not value: value = None
		db_update["welcome_msg_priv"] = validateDBInput(str, value, allow_null=True)
		update["welcome_msg_priv"] = value

	if not db_update:
		return await apiMissingData(cls, WebRequest, msg="No changes, please add at least one")

	cls.Web.BASE.Logger.debug(f"(API/Discord) Config Update: S:{guild_id} {str(db_update)}", require="discord:configs")
	cls.Web.BASE.PhaazeDB.updateQuery(
		table = "discord_setting",
		content = db_update,
		where = "discord_setting.guild_id = %s",
		where_values = (guild_id,)
	)

	return cls.response(
		text=json.dumps( dict(msg="configs successfull updated", update=update, status=200) ),
		content_type="application/json",
		status=200
	)

async def singleActionWordBlacklist(cls:"WebIndex", WebRequest:Request, action:str, Data:WebRequestContent, Configs:DiscordServerSettings) -> Response:
	"""
		Default url: /api/discord/configs/edit?wordblacklist_action=something
	"""
	guild_id:str = Data.getStr("guild_id", "")
	action = action.lower()
	action_word:str = Data.getStr("wordblacklist_word", "").replace(";;;", "") # ;;; is the sql sepperator

	if not guild_id:
		# should never happen
		return await apiMissingData(cls, WebRequest, msg="missing field 'guild_id'")

	if not action_word:
		return await apiMissingData(cls, WebRequest, msg="missing field 'wordblacklist_word'")

	if action == "add":
		cls.Web.BASE.PhaazeDB.insertQuery(
			table = "discord_blacklist_blacklistword",
			content = {
				"guild_id": guild_id,
				"word": action_word
			}
		)

		cls.Web.BASE.Logger.debug(f"(API/Discord) Word Blacklist Update: S:{guild_id} - add: {action_word}", require="discord:configs")
		return cls.response(
			text=json.dumps( dict(msg="word blacklist successfull updated", add=action_word, status=200) ),
			content_type="application/json",
			status=200
		)

	elif action == "remove":
		if action_word not in Configs.blacklist_blacklistwords:
			return await apiWrongData(cls, WebRequest, msg=f"can't remove '{action_word}', it's currently not in the word blacklist")

		cls.Web.BASE.PhaazeDB.deleteQuery("""
			DELETE FROM `discord_blacklist_blacklistword` WHERE `guild_id` = %s AND `word` = %s""",
			(guild_id, action_word)
		)

		cls.Web.BASE.Logger.debug(f"(API/Discord) Word Blacklist Update: S:{guild_id} - rem: {action_word}", require="discord:configs")
		return cls.response(
			text=json.dumps( dict(msg="word blacklist successfull updated", remove=action_word, status=200) ),
			content_type="application/json",
			status=200
		)

	else:
		return await apiWrongData(cls, WebRequest)

async def singleActionLinkWhitelist(cls:"WebIndex", WebRequest:Request, action:str, Data:WebRequestContent, Configs:DiscordServerSettings) -> Response:
	"""
		Default url: /api/discord/configs/edit?linkwhitelist_action=something
	"""
	guild_id:str = Data.getStr("guild_id", "")
	action = action.lower()
	action_link:str = Data.getStr("linkwhitelist_link", "").replace(";;;", "") # ;;; is the sql sepperator

	if not guild_id:
		# should never happen
		return await apiMissingData(cls, WebRequest, msg="missing field 'guild_id'")

	if not action_link:
		return await apiMissingData(cls, WebRequest, msg="missing field 'linkwhitelist_link'")

	if action == "add":
		cls.Web.BASE.PhaazeDB.insertQuery(
			table = "discord_blacklist_whitelistlink",
			content = {
				"link": action_link,
				"guild_id": guild_id
			}
		)

		cls.Web.BASE.Logger.debug(f"(API/Discord) Link Whitelist Update: S:{guild_id} - add: {action_link}", require="discord:configs")
		return cls.response(
			text=json.dumps( dict(msg="link whitelist successfull updated", add=action_link, status=200) ),
			content_type="application/json",
			status=200
		)

	elif action == "remove":
		if action_link not in Configs.blacklist_whitelistlinks:
			return await apiWrongData(cls, WebRequest, msg=f"can't remove '{action_link}', it's currently not in the link whitelist")

		cls.Web.BASE.PhaazeDB.deleteQuery("""
			DELETE FROM `discord_blacklist_whitelistlink` WHERE `guild_id` = %s AND `link` = %s""",
			(guild_id, action_link)
		)

		cls.Web.BASE.Logger.debug(f"(API/Discord) Link Whitelist Update: S:{guild_id} - rem: {action_link}", require="discord:configs")
		return cls.response(
			text=json.dumps( dict(msg="link whitelist successfull updated", remove=action_link, status=200) ),
			content_type="application/json",
			status=200
		)

	else:
		return await apiWrongData(cls, WebRequest)

async def singleActionExceptionRole(cls:"WebIndex", WebRequest:Request, action:str, Data:WebRequestContent, Configs:DiscordServerSettings, CurrentGuild:discord.Guild) -> Response:
	"""
		Default url: /api/discord/configs/edit?exceptionrole_action=something
	"""
	guild_id:str = Data.getStr("guild_id", "")
	action = action.lower()
	role_id:str = Data.getStr("exceptionrole_id", "", must_be_digit=True)

	if not guild_id:
		# should never happen
		return await apiMissingData(cls, WebRequest, msg="missing field 'guild_id'")

	if not role_id:
		return await apiMissingData(cls, WebRequest, msg="missing or invalid field 'exceptionrole_id'")

	ActionRole:discord.Role = CurrentGuild.get_role(int(role_id))
	if not ActionRole and action == "add":
		return await apiDiscordRoleNotFound(cls, WebRequest, guild_id=CurrentGuild.id, guild_name=CurrentGuild.name, role_id=role_id)

	if action == "add":
		if str(ActionRole.id) in Configs.blacklist_whitelistroles:
			return await apiWrongData(cls, WebRequest, msg=f"'{ActionRole.name}' is already added")

		cls.Web.BASE.PhaazeDB.insertQuery(
			table = "discord_blacklist_whitelistrole",
			content = {
				"guild_id": guild_id,
				"role_id": role_id
			}
		)

		cls.Web.BASE.Logger.debug(f"(API/Discord) Exception role list Update: S:{guild_id} - add: {role_id}", require="discord:configs")
		return cls.response(
			text=json.dumps( dict(msg="exception role list successfull updated", add=role_id, status=200) ),
			content_type="application/json",
			status=200
		)

	elif action == "remove":
		if role_id not in Configs.blacklist_whitelistroles:
			return await apiWrongData(cls, WebRequest, msg=f"can't remove '{role_id}', is currently not added")

		cls.Web.BASE.PhaazeDB.deleteQuery("""
			DELETE FROM `discord_blacklist_whitelistrole` WHERE `guild_id` = %s AND `role_id` = %s""",
			(guild_id, role_id)
		)

		cls.Web.BASE.Logger.debug(f"(API/Discord) Exception role list Update: S:{guild_id} - rem: {role_id}", require="discord:configs")
		return cls.response(
			text=json.dumps( dict(msg="exception role list successfull updated", remove=role_id, status=200) ),
			content_type="application/json",
			status=200
		)

	else:
		return await apiWrongData(cls, WebRequest)

async def singleActionDisableLevelChannel(cls:"WebIndex", WebRequest:Request, action:str, Data:WebRequestContent, Configs:DiscordServerSettings, CurrentGuild:discord.Guild) -> Response:
	"""
		Default url: /api/discord/configs/edit?disabled_levelchan_action=something
	"""
	guild_id:str = Data.getStr("guild_id", "")
	action = action.lower()
	channel_id:str = Data.getStr("disabled_levelchan_id", "", must_be_digit=True)

	if not guild_id:
		# should never happen
		return await apiMissingData(cls, WebRequest, msg="missing field 'guild_id'")

	if not channel_id:
		return await apiMissingData(cls, WebRequest, msg="missing or invalid field 'disable_chan_level_id'")

	ActionChannel:discord.TextChannel = CurrentGuild.get_channel(int(channel_id))
	if not ActionChannel and action == "add":
		return await apiDiscordChannelNotFound(cls, WebRequest, guild_name=CurrentGuild.name, guild_id=CurrentGuild.id, channel_id=channel_id)

	if action == "add":
		if str(ActionChannel.id) in Configs.disabled_levelchannels:
			return await apiWrongData(cls, WebRequest, msg=f"'{ActionChannel.name}' is already added")

		cls.Web.BASE.PhaazeDB.insertQuery(
			table = "discord_disabled_levelchannel",
			content = {
				"guild_id": guild_id,
				"channel_id": channel_id
			}
		)

		cls.Web.BASE.Logger.debug(f"(API/Discord) Disabled level channel list Update: S:{guild_id} - add: {channel_id}", require="discord:configs")
		return cls.response(
			text=json.dumps( dict(msg="disabled level channel list successfull updated", add=channel_id, status=200) ),
			content_type="application/json",
			status=200
		)

	elif action == "remove":
		if channel_id not in Configs.disabled_levelchannels:
			return await apiWrongData(cls, WebRequest, msg=f"can't remove '{channel_id}', is currently not added")

		cls.Web.BASE.PhaazeDB.deleteQuery("""
			DELETE FROM `discord_disabled_levelchannel` WHERE `guild_id` = %s AND `channel_id` = %s""",
			(guild_id, channel_id)
		)

		cls.Web.BASE.Logger.debug(f"(API/Discord) Disabled level channel list Update: S:{guild_id} - rem: {channel_id}", require="discord:configs")
		return cls.response(
			text=json.dumps( dict(msg="disabled level channel list successfull updated", remove=channel_id, status=200) ),
			content_type="application/json",
			status=200
		)

	else:
		return await apiWrongData(cls, WebRequest)

async def singleActionDisableQuoteChannel(cls:"WebIndex", WebRequest:Request, action:str, Data:WebRequestContent, Configs:DiscordServerSettings, CurrentGuild:discord.Guild) -> Response:
	"""
		Default url: /api/discord/configs/edit?disabled_quotechan_action=something
	"""
	guild_id:str = Data.getStr("guild_id", "")
	action = action.lower()
	channel_id:str = Data.getStr("disabled_quotechan_id", "", must_be_digit=True)

	if not guild_id:
		# should never happen
		return await apiMissingData(cls, WebRequest, msg="missing field 'guild_id'")

	if not channel_id:
		return await apiMissingData(cls, WebRequest, msg="missing or invalid field 'disabled_quotechan_id'")

	ActionChannel:discord.TextChannel = CurrentGuild.get_channel(int(channel_id))
	if not ActionChannel and action == "add":
		return await apiDiscordChannelNotFound(cls, WebRequest, guild_name=CurrentGuild.name, guild_id=CurrentGuild.id, channel_id=channel_id)

	if action == "add":
		if str(ActionChannel.id) in Configs.disabled_quotechannels:
			return await apiWrongData(cls, WebRequest, msg=f"'{ActionChannel.name}' is already added")

		cls.Web.BASE.PhaazeDB.insertQuery(
			table = "discord_disabled_quotechannel",
			content = {
				"guild_id": guild_id,
				"channel_id": channel_id
			}
		)

		cls.Web.BASE.Logger.debug(f"(API/Discord) Disabled quote channel list Update: S:{guild_id} - add: {channel_id}", require="discord:configs")
		return cls.response(
			text=json.dumps( dict(msg="disabled quote channel list successfull updated", add=channel_id, status=200) ),
			content_type="application/json",
			status=200
		)

	elif action == "remove":
		if channel_id not in Configs.disabled_quotechannels:
			return await apiWrongData(cls, WebRequest, msg=f"can't remove '{channel_id}', is currently not added")

		cls.Web.BASE.PhaazeDB.deleteQuery("""
			DELETE FROM `discord_disabled_quotechannel` WHERE `guild_id` = %s AND `channel_id` = %s""",
			(guild_id, channel_id)
		)

		cls.Web.BASE.Logger.debug(f"(API/Discord) Disabled quote channel list Update: S:{guild_id} - rem: {channel_id}", require="discord:configs")
		return cls.response(
			text=json.dumps( dict(msg="disabled quote channel list successfull updated", remove=channel_id, status=200) ),
			content_type="application/json",
			status=200
		)

	else:
		return await apiWrongData(cls, WebRequest)

async def singleActionDisableNormalChannel(cls:"WebIndex", WebRequest:Request, action:str, Data:WebRequestContent, Configs:DiscordServerSettings, CurrentGuild:discord.Guild) -> Response:
	"""
		Default url: /api/discord/configs/edit?disabled_normalchan_action=something
	"""
	guild_id:str = Data.getStr("guild_id", "")
	action = action.lower()
	channel_id:str = Data.getStr("disabled_normalchan_id", "", must_be_digit=True)

	if not guild_id:
		# should never happen
		return await apiMissingData(cls, WebRequest, msg="missing field 'guild_id'")

	if not channel_id:
		return await apiMissingData(cls, WebRequest, msg="missing or invalid field 'disabled_normalchan_id'")

	ActionChannel:discord.TextChannel = CurrentGuild.get_channel(int(channel_id))
	if not ActionChannel and action == "add":
		return await apiDiscordChannelNotFound(cls, WebRequest, guild_name=CurrentGuild.name, guild_id=CurrentGuild.id, channel_id=channel_id)

	if action == "add":
		if str(ActionChannel.id) in Configs.disabled_normalchannels:
			return await apiWrongData(cls, WebRequest, msg=f"'{ActionChannel.name}' is already added")

		cls.Web.BASE.PhaazeDB.insertQuery(
			table = "discord_disabled_normalchannel",
			content = {
				"guild_id": guild_id,
				"channel_id": channel_id
			}
		)

		cls.Web.BASE.Logger.debug(f"(API/Discord) Disabled normal channel list Update: S:{guild_id} - add: {channel_id}", require="discord:configs")
		return cls.response(
			text=json.dumps( dict(msg="disabled normal channel list successfull updated", add=channel_id, status=200) ),
			content_type="application/json",
			status=200
		)

	elif action == "remove":
		if channel_id not in Configs.disabled_normalchannels:
			return await apiWrongData(cls, WebRequest, msg=f"can't remove '{channel_id}', is currently not added")

		cls.Web.BASE.PhaazeDB.deleteQuery("""
			DELETE FROM `discord_disabled_normalchannel` WHERE `guild_id` = %s AND `channel_id` = %s""",
			(guild_id, channel_id)
		)

		cls.Web.BASE.Logger.debug(f"(API/Discord) Disabled normal channel list Update: S:{guild_id} - rem: {channel_id}", require="discord:configs")
		return cls.response(
			text=json.dumps( dict(msg="disabled normal channel list successfull updated", remove=channel_id, status=200) ),
			content_type="application/json",
			status=200
		)

	else:
		return await apiWrongData(cls, WebRequest)

async def singleActionDisableRegularChannel(cls:"WebIndex", WebRequest:Request, action:str, Data:WebRequestContent, Configs:DiscordServerSettings, CurrentGuild:discord.Guild) -> Response:
	"""
		Default url: /api/discord/configs/edit?disabled_regularchan_action=something
	"""
	guild_id:str = Data.getStr("guild_id", "")
	action = action.lower()
	channel_id:str = Data.getStr("disabled_regularchan_id", "", must_be_digit=True)

	if not guild_id:
		# should never happen
		return await apiMissingData(cls, WebRequest, msg="missing field 'guild_id'")

	if not channel_id:
		return await apiMissingData(cls, WebRequest, msg="missing or invalid field 'disabled_regularchan_id'")

	ActionChannel:discord.TextChannel = CurrentGuild.get_channel(int(channel_id))
	if not ActionChannel and action == "add":
		return await apiDiscordChannelNotFound(cls, WebRequest, guild_name=CurrentGuild.name, guild_id=CurrentGuild.id, channel_id=channel_id)

	if action == "add":
		if str(ActionChannel.id) in Configs.disabled_regularchannels:
			return await apiWrongData(cls, WebRequest, msg=f"'{ActionChannel.name}' is already added")

		cls.Web.BASE.PhaazeDB.insertQuery(
			table = "discord_disabled_regularchannel",
			content = {
				"guild_id": guild_id,
				"channel_id": channel_id,
			}
		)

		cls.Web.BASE.Logger.debug(f"(API/Discord) Disabled normal channel list Update: S:{guild_id} - add: {channel_id}", require="discord:configs")
		return cls.response(
			text=json.dumps( dict(msg="disabled normal channel list successfull updated", add=channel_id, status=200) ),
			content_type="application/json",
			status=200
		)

	elif action == "remove":
		if channel_id not in Configs.disabled_regularchannels:
			return await apiWrongData(cls, WebRequest, msg=f"can't remove '{channel_id}', is currently not added")

		cls.Web.BASE.PhaazeDB.deleteQuery("""
			DELETE FROM `discord_disabled_regularchannel` WHERE `guild_id` = %s AND `channel_id` = %s""",
			(guild_id, channel_id)
		)

		cls.Web.BASE.Logger.debug(f"(API/Discord) Disabled normal channel list Update: S:{guild_id} - rem: {channel_id}", require="discord:configs")
		return cls.response(
			text=json.dumps( dict(msg="disabled normal channel list successfull updated", remove=channel_id, status=200) ),
			content_type="application/json",
			status=200
		)

	else:
		return await apiWrongData(cls, WebRequest)

async def singleActionEnableGameChannel(cls:"WebIndex", WebRequest:Request, action:str, Data:WebRequestContent, Configs:DiscordServerSettings, CurrentGuild:discord.Guild) -> Response:
	"""
		Default url: /api/discord/configs/edit?enabled_gamechan_action=something
	"""
	guild_id:str = Data.getStr("guild_id", "")
	action = action.lower()
	channel_id:str = Data.getStr("enabled_gamechan_id", "", must_be_digit=True)

	if not guild_id:
		# should never happen
		return await apiMissingData(cls, WebRequest, msg="missing field 'guild_id'")

	if not channel_id:
		return await apiMissingData(cls, WebRequest, msg="missing or invalid field 'enabled_gamechan_id'")

	ActionChannel:discord.TextChannel = CurrentGuild.get_channel(int(channel_id))
	if not ActionChannel and action == "add":
		return await apiDiscordChannelNotFound(cls, WebRequest, guild_name=CurrentGuild.name, guild_id=CurrentGuild.id, channel_id=channel_id)

	if action == "add":
		if str(ActionChannel.id) in Configs.enabled_gamechannels:
			return await apiWrongData(cls, WebRequest, msg=f"'{ActionChannel.name}' is already added")

		cls.Web.BASE.PhaazeDB.insertQuery(
			table = "discord_enabled_gamechannel",
			content = {
				"guild_id": guild_id,
				"channel_id": channel_id
			}
		)

		cls.Web.BASE.Logger.debug(f"(API/Discord) Enabled game channel list Update: S:{guild_id} - add: {channel_id}", require="discord:configs")
		return cls.response(
			text=json.dumps( dict(msg="enabled game channel list successfull updated", add=channel_id, status=200) ),
			content_type="application/json",
			status=200
		)

	elif action == "remove":
		if channel_id not in Configs.enabled_gamechannels:
			return await apiWrongData(cls, WebRequest, msg=f"can't remove '{channel_id}', is currently not added")

		cls.Web.BASE.PhaazeDB.deleteQuery("""
			DELETE FROM `discord_enabled_gamechannel` WHERE `guild_id` = %s AND `channel_id` = %s""",
			(guild_id, channel_id)
		)

		cls.Web.BASE.Logger.debug(f"(API/Discord) Enabled game channel list Update: S:{guild_id} - rem: {channel_id}", require="discord:configs")
		return cls.response(
			text=json.dumps( dict(msg="enabled game channel list successfull updated", remove=channel_id, status=200) ),
			content_type="application/json",
			status=200
		)

	else:
		return await apiWrongData(cls, WebRequest)

async def singleActionEnableNSFWChannel(cls:"WebIndex", WebRequest:Request, action:str, Data:WebRequestContent, Configs:DiscordServerSettings, CurrentGuild:discord.Guild) -> Response:
	"""
		Default url: /api/discord/configs/edit?enabled_nsfwchan_action=something
	"""
	guild_id:str = Data.getStr("guild_id", "")
	action = action.lower()
	channel_id:str = Data.getStr("enabled_nsfwchan_id", "", must_be_digit=True)

	if not guild_id:
		# should never happen
		return await apiMissingData(cls, WebRequest, msg="missing field 'guild_id'")

	if not channel_id:
		return await apiMissingData(cls, WebRequest, msg="missing or invalid field 'enabled_nsfwchan_id'")

	ActionChannel:discord.TextChannel = CurrentGuild.get_channel(int(channel_id))
	if not ActionChannel and action == "add":
		return await apiDiscordChannelNotFound(cls, WebRequest, guild_name=CurrentGuild.name, guild_id=CurrentGuild.id, channel_id=channel_id)

	if action == "add":
		if str(ActionChannel.id) in Configs.enabled_nsfwchannels:
			return await apiWrongData(cls, WebRequest, msg=f"'{ActionChannel.name}' is already added")

		cls.Web.BASE.PhaazeDB.insertQuery(
			table = "discord_enabled_nsfwchannel",
			content = {
				"guild_id": guild_id,
				"channel_id": channel_id,
			}
		)

		cls.Web.BASE.Logger.debug(f"(API/Discord) Enabled nsfw channel list Update: S:{guild_id} - add: {channel_id}", require="discord:configs")
		return cls.response(
			text=json.dumps( dict(msg="enabled nsfw channel list successfull updated", add=channel_id, status=200) ),
			content_type="application/json",
			status=200
		)

	elif action == "remove":
		if channel_id not in Configs.enabled_nsfwchannels:
			return await apiWrongData(cls, WebRequest, msg=f"can't remove '{channel_id}', is currently not added")

		cls.Web.BASE.PhaazeDB.deleteQuery("""
			DELETE FROM `discord_enabled_nsfwchannel` WHERE `guild_id` = %s AND `channel_id` = %s""",
			(guild_id, channel_id)
		)

		cls.Web.BASE.Logger.debug(f"(API/Discord) Enabled nsfw channel list Update: S:{guild_id} - rem: {channel_id}", require="discord:configs")
		return cls.response(
			text=json.dumps( dict(msg="enabled nsfw channel list successfull updated", remove=channel_id, status=200) ),
			content_type="application/json",
			status=200
		)

	else:
		return await apiWrongData(cls, WebRequest)
