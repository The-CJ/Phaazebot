from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex
	from Platforms.Discord.main_discord import PhaazebotDiscord

import json
import discord
from aiohttp.web import Response, Request
from Utils.Classes.webrequestcontent import WebRequestContent
from Platforms.Web.Processing.Api.errors import missingData, apiWrongData
from Platforms.Discord.utils import getDiscordSeverSettings
from Utils.Classes.discordserversettings import DiscordServerSettings
from Utils.Classes.discorduserinfo import DiscordUserInfo
from Platforms.Web.Processing.Api.errors import apiMissingAuthorisation
from Platforms.Web.Processing.Api.Discord.errors import apiDiscordGuildUnknown, apiDiscordMemberNotFound, apiDiscordMissingPermission, apiDiscordRoleNotFound
from Utils.Classes.undefined import Undefined
from Platforms.Discord.blacklist import checkBlacklistPunishmentString
from Utils.dbutils import validateDBInput

async def apiDiscordConfigsEdit(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
		Default url: /api/discord/configs/edit
	"""
	Data:WebRequestContent = WebRequestContent(WebRequest)
	await Data.load()

	guild_id:str = Data.get("guild_id")
	if not guild_id:
		return await missingData(cls, WebRequest, msg="missing 'guild_id'")

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

	Configs:DiscordServerSettings = await getDiscordSeverSettings(PhaazeDiscord, origin=guild_id, prevent_new=True)

	if not Configs:
		return await apiDiscordGuildUnknown(cls, WebRequest, msg="Could not find configs for this guild")

	# single actions
	action:str or Undefined = Data.get("wordblacklist_action")
	if action:
		return await singleActionWordBlacklist(cls, WebRequest, action, Data, Configs)

	action:str or Undefined = Data.get("linkwhitelist_action")
	if action:
		return await singleActionLinkWhitelist(cls, WebRequest, action, Data, Configs)

	action:str or Undefined = Data.get("exceptionrole_action")
	if action:
		return await singleActionExceptionRole(cls, WebRequest, action, Data, Configs, Guild)

	changes:dict = dict()
	db_changes:dict = dict()

	# get all changed stuff and add changes to list
	# changes is for the user, so return with types, db_changes is with, well... db values
	# e.g.:
	# changes["x"] = true
	# db_changes["x"] = "1"

	# ban_links
	value:str or Undefined = Data.get("ban_links")
	if type(value) is not Undefined:
		db_changes["ban_links"] = validateDBInput(bool, value)
		changes["ban_links"] = True if db_changes["ban_links"] == "1" else False

	# blacklist_punishment
	value:str or Undefined = Data.get("blacklist_punishment")
	if type(value) is not Undefined:
		value = checkBlacklistPunishmentString(value)
		db_changes["blacklist_punishment"] = validateDBInput(str, value)
		changes["blacklist_punishment"] = db_changes["blacklist_punishment"]

	# leave_chan
	value:str or Undefined = Data.get("leave_chan")
	if type(value) is not Undefined:
		error:bool = False
		if value == "": pass
		elif value.isdigit():
			Chan:discord.abc.Messageable = discord.utils.get(Guild.channels, id=int(value))
			if type(Chan) != discord.TextChannel:
				error = True
			else:
				value = Chan.id
		else:
			error = True

		if error:
			return await apiWrongData(cls, WebRequest, msg=f"'{value}' could not be resolved as a valid discord text channel id")

		db_changes["leave_chan"] = validateDBInput(str, value)
		changes["leave_chan"] = db_changes["leave_chan"]

	# leave_msg
	value:str or Undefined = Data.get("leave_msg")
	if type(value) is not Undefined:
		db_changes["leave_msg"] = validateDBInput(str, value)
		changes["leave_msg"] = db_changes["leave_msg"]

	# owner_disable_normal
	value:str or Undefined = Data.get("owner_disable_normal")
	if type(value) is not Undefined:
		db_changes["owner_disable_normal"] = validateDBInput(bool, value)
		changes["owner_disable_normal"] = True if db_changes["owner_disable_normal"] == "1" else False

	# owner_disable_regular
	value:str or Undefined = Data.get("owner_disable_regular")
	if type(value) is not Undefined:
		db_changes["owner_disable_regular"] = validateDBInput(bool, value)
		changes["owner_disable_regular"] = True if db_changes["owner_disable_regular"] == "1" else False

	# owner_disable_mod
	value:str or Undefined = Data.get("owner_disable_mod")
	if type(value) is not Undefined:
		db_changes["owner_disable_mod"] = validateDBInput(bool, value)
		changes["owner_disable_mod"] = True if db_changes["owner_disable_mod"] == "1" else False

	# welcome_chan
	value:str or Undefined = Data.get("welcome_chan")
	if type(value) is not Undefined:
		error:bool = False
		if value == "": pass
		elif value.isdigit():
			Chan:discord.abc.Messageable = discord.utils.get(Guild.channels, id=int(value))
			if type(Chan) != discord.TextChannel:
				error = True
			else:
				value = Chan.id
		else:
			error = True

		if error:
			return await apiWrongData(cls, WebRequest, msg=f"'{value}' could not be resolved as a valid discord text channel id")

		db_changes["welcome_chan"] = validateDBInput(str, value)
		changes["welcome_chan"] = db_changes["welcome_chan"]

	# welcome_msg
	value:str or Undefined = Data.get("welcome_msg")
	if type(value) is not Undefined:
		db_changes["welcome_msg"] = validateDBInput(str, value)
		changes["welcome_msg"] = db_changes["welcome_msg"]

	# welcome_msg_priv
	value:str or Undefined = Data.get("welcome_msg_priv")
	if type(value) is not Undefined:
		db_changes["welcome_msg_priv"] = validateDBInput(str, value)
		changes["welcome_msg_priv"] = db_changes["welcome_msg_priv"]

	if not db_changes:
		return await missingData(cls, WebRequest, msg="No changes, please add at least one")

	cls.Web.BASE.Logger.debug(f"(API/Discord) Config Update: S:{guild_id} {str(db_changes)}", require="discord:configs")
	cls.Web.BASE.PhaazeDB.updateQuery(
		table = "discord_setting",
		content = db_changes,
		where = "discord_setting.guild_id = %s",
		where_values = (guild_id,)
	)

	return cls.response(
		text=json.dumps( dict(msg="configs successfull updated", changes=changes, status=200) ),
		content_type="application/json",
		status=200
	)

async def singleActionWordBlacklist(cls:"WebIndex", WebRequest:Request, action:str, Data:WebRequestContent, Configs:DiscordServerSettings) -> Response:
	"""
		Default url: /api/discord/configs/edit?wordblacklist_action=something
	"""
	guild_id:str = Data.get("guild_id")
	action = action.lower()
	action_word:str = Data.get("wordblacklist_word", "").strip(" ").strip("\n")

	if not guild_id:
		# should never happen
		return await missingData(cls, WebRequest, msg="missing field 'guild_id'")

	if not action_word:
		return await missingData(cls, WebRequest, msg="missing field 'blacklist_word'")

	if action == "add":
		Configs.blacklist_words.append(action_word.lower())
		cls.Web.BASE.PhaazeDB.updateQuery(
			table = "discord_setting",
			content = {"blacklist_words": json.dumps(Configs.blacklist_words) },
			where = "discord_setting.guild_id = %s",
			where_values = (guild_id,)
		)

		cls.Web.BASE.Logger.debug(f"(API/Discord) Word Blacklist Update: S:{guild_id} - add: {action_word}", require="discord:configs")
		return cls.response(
			text=json.dumps( dict(msg="word blacklist successfull updated", add=action_word, status=200) ),
			content_type="application/json",
			status=200
		)

	elif action == "remove":
		for word in Configs.blacklist_words:
			if action_word == word.lower():
				Configs.blacklist_words.remove(word)

				cls.Web.BASE.PhaazeDB.updateQuery(
					table = "discord_setting",
					content = {"blacklist_words": json.dumps(Configs.blacklist_words) },
					where = "discord_setting.guild_id = %s",
					where_values = (guild_id,)
				)

				cls.Web.BASE.Logger.debug(f"(API/Discord) Word Blacklist Update: S:{guild_id} - rem: {action_word}", require="discord:configs")
				return cls.response(
					text=json.dumps( dict(msg="word blacklist successfull updated", remove=action_word, status=200) ),
					content_type="application/json",
					status=200
				)

		return await apiWrongData(cls, WebRequest, msg=f"can't remove '{action_word}', it's currently not in the word blacklist")


	else:
		return await apiWrongData(cls, WebRequest)

async def singleActionLinkWhitelist(cls:"WebIndex", WebRequest:Request, action:str, Data:WebRequestContent, Configs:DiscordServerSettings) -> Response:
	"""
		Default url: /api/discord/configs/edit?linkwhitelist_action=something
	"""
	guild_id:str = Data.get("guild_id")
	action = action.lower()
	action_link:str = Data.get("linkwhitelist_link", "").strip(" ").strip("\n")

	if not guild_id:
		# should never happen
		return await missingData(cls, WebRequest, msg="missing field 'guild_id'")

	if not action_link:
		return await missingData(cls, WebRequest, msg="missing field 'linkwhitelist_link'")

	if action == "add":
		Configs.ban_links_whitelist.append(action_link.lower())
		cls.Web.BASE.PhaazeDB.updateQuery(
			table = "discord_setting",
			content = {"ban_links_whitelist": json.dumps(Configs.ban_links_whitelist) },
			where = "discord_setting.guild_id = %s",
			where_values = (guild_id,)
		)

		cls.Web.BASE.Logger.debug(f"(API/Discord) Link Whitelist Update: S:{guild_id} - add: {action_link}", require="discord:configs")
		return cls.response(
			text=json.dumps( dict(msg="link whitelist successfull updated", add=action_link, status=200) ),
			content_type="application/json",
			status=200
		)

	elif action == "remove":
		for link in Configs.ban_links_whitelist:
			if action_link == link.lower():
				Configs.ban_links_whitelist.remove(link)

				cls.Web.BASE.PhaazeDB.updateQuery(
					table = "discord_setting",
					content = {"ban_links_whitelist": json.dumps(Configs.ban_links_whitelist) },
					where = "discord_setting.guild_id = %s",
					where_values = (guild_id,)
				)

				cls.Web.BASE.Logger.debug(f"(API/Discord) Link Whitelist Update: S:{guild_id} - rem: {action_link}", require="discord:configs")
				return cls.response(
					text=json.dumps( dict(msg="link whitelist successfull updated", remove=action_link, status=200) ),
					content_type="application/json",
					status=200
				)

		return await apiWrongData(cls, WebRequest, msg=f"can't remove '{action_link}', it's currently not in the link whitelist")


	else:
		return await apiWrongData(cls, WebRequest)

async def singleActionExceptionRole(cls:"WebIndex", WebRequest:Request, action:str, Data:WebRequestContent, Configs:DiscordServerSettings, CurrentGuild:discord.Guild) -> Response:
	"""
		Default url: /api/discord/configs/edit?exceptionrole_action=something
	"""
	guild_id:str = Data.get("guild_id")
	action = action.lower()
	role_id:str = Data.get("exceptionrole_id", "").strip(" ").strip("\n")

	if not guild_id:
		# should never happen
		return await missingData(cls, WebRequest, msg="missing field 'guild_id'")

	if not role_id:
		return await missingData(cls, WebRequest, msg="missing or invalid field 'role_id'")

	if not role_id.isdigit():
		return await apiWrongData(cls, WebRequest, msg="'role_id' must be digit")

	ActionRole:discord.Role = CurrentGuild.get_role(int(role_id))
	if not ActionRole:
		return await apiDiscordRoleNotFound(cls, WebRequest, role_id=role_id, guild_id=CurrentGuild.id)

	if action == "add":
		if str(ActionRole.id) in Configs.ban_links_role:
			return await apiWrongData(cls, WebRequest, msg=f"'{ActionRole.name}' is already added")

		Configs.ban_links_role.append(role_id)
		cls.Web.BASE.PhaazeDB.updateQuery(
			table = "discord_setting",
			content = {"ban_links_role": json.dumps(Configs.ban_links_role) },
			where = "discord_setting.guild_id = %s",
			where_values = (guild_id,)
		)

		cls.Web.BASE.Logger.debug(f"(API/Discord) Exception role list Update: S:{guild_id} - add: {role_id}", require="discord:configs")
		return cls.response(
			text=json.dumps( dict(msg="exception role list successfull updated", add=role_id, status=200) ),
			content_type="application/json",
			status=200
		)

	elif action == "remove":
		for role in Configs.ban_links_role:
			if role_id == role:
				Configs.ban_links_role.remove(role)

				cls.Web.BASE.PhaazeDB.updateQuery(
					table = "discord_setting",
					content = {"ban_links_role": json.dumps(Configs.ban_links_role) },
					where = "discord_setting.guild_id = %s",
					where_values = (guild_id,)
				)

				cls.Web.BASE.Logger.debug(f"(API/Discord) Exception role list Update: S:{guild_id} - rem: {role_id}", require="discord:configs")
				return cls.response(
					text=json.dumps( dict(msg="exception role list successfull updated", remove=role_id, status=200) ),
					content_type="application/json",
					status=200
				)

		return await apiWrongData(cls, WebRequest, msg=f"can't remove '{role_id}' is currently not added")


	else:
		return await apiWrongData(cls, WebRequest)
