from typing import TYPE_CHECKING, Coroutine
if TYPE_CHECKING:
	from Platforms.Discord.main_discord import PhaazebotDiscord
	from Platforms.Web.main_web import PhaazebotWeb

import json
import asyncio
import discord
from aiohttp.web import Response
from Utils.Classes.discordserversettings import DiscordServerSettings
from Utils.Classes.storagetransformer import StorageTransformer
from Utils.Classes.authdiscordwebuser import AuthDiscordWebUser
from Utils.Classes.webrequestcontent import WebRequestContent
from Utils.Classes.extendedrequest import ExtendedRequest
from Utils.Classes.undefined import UNDEFINED
from Platforms.Discord.logging import loggingOnConfigEdit
from Platforms.Discord.punish import checkPunishmentString
from Platforms.Discord.utils import getDiscordRoleFromString, getDiscordChannelFromString
from Platforms.Discord.db import getDiscordSeverSettings
from Platforms.Web.utils import authDiscordWebUser

async def apiDiscordConfigsEdit(cls:"PhaazebotWeb", WebRequest:ExtendedRequest) -> Response:
	"""
	Default url: /api/discord/configs/edit
	"""
	Data:WebRequestContent = WebRequestContent(WebRequest)
	await Data.load()

	# get required stuff
	Edit:StorageTransformer = StorageTransformer()
	Edit["guild_id"] = Data.getStr("guild_id", "", must_be_digit=True)

	# checks
	if not Edit["guild_id"]:
		return await cls.Tree.Api.errors.apiMissingData(cls, WebRequest, msg="missing or invalid 'guild_id'")

	PhaazeDiscord:"PhaazebotDiscord" = cls.BASE.Discord
	Guild:discord.Guild = discord.utils.get(PhaazeDiscord.guilds, id=int(Edit["guild_id"]))
	if not Guild:
		return await cls.Tree.Api.Discord.errors.apiDiscordGuildUnknown(cls, WebRequest)

	# get user info
	AuthDiscord:AuthDiscordWebUser = await authDiscordWebUser(cls, WebRequest)
	if not AuthDiscord.found:
		return await cls.Tree.Api.errors.apiMissingAuthorisation(cls, WebRequest)

	# get member
	CheckMember:discord.Member = Guild.get_member(int(AuthDiscord.User.user_id))
	if not CheckMember:
		return await cls.Tree.Api.Discord.errors.apiDiscordMemberNotFound(cls, WebRequest, guild_id=Edit["guild_id"], user_id=AuthDiscord.User.user_id)

	# check permissions
	# to edit configs, at least moderator rights are needed, (there can be options that require server only duh)
	if not (CheckMember.guild_permissions.administrator or CheckMember.guild_permissions.manage_guild):
		return await cls.Tree.Api.Discord.errors.apiDiscordMissingPermission(cls, WebRequest, guild_id=Edit["guild_id"], user_id=AuthDiscord.User.user_id)

	Configs:DiscordServerSettings = await getDiscordSeverSettings(PhaazeDiscord, origin=Edit["guild_id"], prevent_new=True)

	if not Configs:
		return await cls.Tree.Api.Discord.errors.apiDiscordGuildUnknown(cls, WebRequest, msg="Could not find configs for this guild")

	# check all update values
	update:dict = dict()

	Edit["autorole_id"] = Data.getStr("autorole_id", UNDEFINED, len_max=128, allow_none=True)
	if Edit["autorole_id"] != UNDEFINED:
		error:bool = False
		if not Edit["autorole_id"]:
			update["autorole_id"] = None
		else:
			Role:discord.Role = getDiscordRoleFromString(PhaazeDiscord, Guild, Edit["autorole_id"])
			if not Role:
				error = True
			elif Role >= Guild.me.top_role:
				return await cls.Tree.Api.errors.apiWrongData(cls, WebRequest, msg=f"The Role `{Role.name}` is to high")
			else:
				update["autorole_id"] = str(Role.id)

		if error:
			return await cls.Tree.Api.errors.apiWrongData(cls, WebRequest, msg=f"{Edit['autorole_id']} could not be resolved as a valid discord role")

	# blacklist_ban_links
	Edit["blacklist_ban_links"] = Data.getBool("blacklist_ban_links", UNDEFINED)
	if Edit["blacklist_ban_links"] != UNDEFINED:
		update["blacklist_ban_links"] = Edit["blacklist_ban_links"]

	# blacklist_punishment
	Edit["blacklist_punishment"] = Data.getStr("blacklist_punishment", UNDEFINED, len_max=32)
	if Edit["blacklist_punishment"] != UNDEFINED:
		Edit["blacklist_punishment"] = checkPunishmentString(Edit["blacklist_punishment"])
		update["blacklist_punishment"] = Edit["blacklist_punishment"]

	# currency_name
	Edit["currency_name"] = Data.getStr("currency_name", UNDEFINED, len_max=256, allow_none=True)
	if Edit["currency_name"] != UNDEFINED:
		if not Edit['currency_name']:
			update["currency_name"] = None
		else:
			update["currency_name"] = Edit["currency_name"]

	# currency_name_multi
	Edit["currency_name_multi"] = Data.getStr("currency_name_multi", UNDEFINED, len_max=256, allow_none=True)
	if Edit["currency_name_multi"] != UNDEFINED:
		if not Edit["currency_name_multi"]:
			update["currency_name_multi"] = None
		else:
			update["currency_name_multi"] = Edit["currency_name_multi"]

	# leave_chan
	Edit["leave_chan"] = Data.getStr("leave_chan", UNDEFINED, len_max=128, allow_none=True)
	if Edit["leave_chan"] != UNDEFINED:
		error:bool = False
		if not Edit["leave_chan"]:
			update["leave_chan"] = None
		else:
			Chan:discord.TextChannel = getDiscordChannelFromString(PhaazeDiscord, Guild, Edit["leave_chan"], required_type="text")
			if not Chan:
				error = True
			else:
				update["leave_chan"] = str(Chan.id)

		if error:
			return await cls.Tree.Api.errors.apiWrongData(cls, WebRequest, msg=f"'{Edit['leave_chan']}' could not be resolved as a valid discord text channel")

	# leave_msg
	Edit["leave_msg"] = Data.getStr("leave_msg", UNDEFINED, len_max=1750, allow_none=True)
	if Edit["leave_msg"] != UNDEFINED:
		if not Edit["leave_msg"]:
			update["leave_msg"] = None
		else:
			update["leave_msg"] = Edit["leave_msg"]

	# level_custom_msg
	Edit["level_custom_msg"] = Data.getStr("level_custom_msg", UNDEFINED, len_max=1750, allow_none=True)
	if Edit["level_custom_msg"] != UNDEFINED:
		if not Edit["level_custom_msg"]:
			update["level_custom_msg"] = None
		else:
			update["level_custom_msg"] = Edit["level_custom_msg"]

	# level_announce_chan
	Edit["level_announce_chan"] = Data.getStr("level_announce_chan", UNDEFINED, len_max=128, allow_none=True)
	if Edit["level_announce_chan"] != UNDEFINED:
		error:bool = False
		if not Edit["level_announce_chan"]:
			update["level_announce_chan"] = None
		else:
			Chan:discord.TextChannel = getDiscordChannelFromString(PhaazeDiscord, Guild, Edit["level_announce_chan"], required_type="text")
			if not Chan:
				error = True
			else:
				update["level_announce_chan"] = str(Chan.id)

		if error:
			return await cls.Tree.Api.errors.apiWrongData(cls, WebRequest, msg=f"'{Edit['level_announce_chan']}' could not be resolved as a valid discord text channel")

		update["level_announce_chan"] = Edit["level_announce_chan"]

	# owner_disable_level
	Edit["owner_disable_level"] = Data.getBool("owner_disable_level", UNDEFINED)
	if Edit["owner_disable_level"] != UNDEFINED:
		if not Guild.owner == CheckMember:
			return await cls.Tree.Api.Discord.errors.apiDiscordMissingPermission(cls, WebRequest, guild_id=Edit["guild_id"], user_id=AuthDiscord.User.user_id, msg="changing 'owner_disable_level' require server owner")
		update["owner_disable_level"] = Edit["owner_disable_level"]

	# owner_disable_normal
	Edit["owner_disable_normal"] = Data.getBool("owner_disable_normal", UNDEFINED)
	if Edit["owner_disable_normal"] != UNDEFINED:
		if not Guild.owner == CheckMember:
			return await cls.Tree.Api.Discord.errors.apiDiscordMissingPermission(cls, WebRequest, guild_id=Edit["guild_id"], user_id=AuthDiscord.User.user_id, msg="changing 'owner_disable_level' require server owner")
		update["owner_disable_normal"] = Edit["owner_disable_normal"]

	# owner_disable_regular
	Edit["owner_disable_regular"] = Data.getBool("owner_disable_regular", UNDEFINED)
	if Edit["owner_disable_regular"] != UNDEFINED:
		if not Guild.owner == CheckMember:
			return await cls.Tree.Api.Discord.errors.apiDiscordMissingPermission(cls, WebRequest, guild_id=Edit["guild_id"], user_id=AuthDiscord.User.user_id, msg="changing 'owner_disable_level' require server owner")
		update["owner_disable_regular"] = Edit["owner_disable_regular"]

	# owner_disable_mod
	Edit["owner_disable_mod"] = Data.getBool("owner_disable_mod", UNDEFINED)
	if Edit["owner_disable_mod"] != UNDEFINED:
		if not Guild.owner == CheckMember:
			return await cls.Tree.Api.Discord.errors.apiDiscordMissingPermission(cls, WebRequest, guild_id=Edit["guild_id"], user_id=AuthDiscord.User.user_id, msg="changing 'owner_disable_level' require server owner")
		update["owner_disable_mod"] = Edit["owner_disable_mod"]

	# track_channel
	Edit["track_channel"] = Data.getStr("track_channel", UNDEFINED, len_max=128, allow_none=True)
	if Edit["track_channel"] != UNDEFINED:
		error:bool = False
		if not Edit["track_channel"]:
			update["track_channel"] = Edit["track_channel"]
		else:
			Chan:discord.TextChannel = getDiscordChannelFromString(PhaazeDiscord, Guild, Edit["track_channel"], required_type="text")
			if not Chan:
				error = True
			else:
				update["track_channel"] = str(Chan.id)

		if error:
			return await cls.Tree.Api.errors.apiWrongData(cls, WebRequest, msg=f"'{Edit['track_channel']}' could not be resolved as a valid discord text channel")

	# track_value
	Edit["track_value"] = Data.getInt("track_value", UNDEFINED, min_x=0)
	if Edit["track_value"] != UNDEFINED:
		update["track_value"] = Edit["track_value"]

	# welcome_chan
	Edit["welcome_chan"] = Data.getStr("welcome_chan", UNDEFINED, len_max=128, allow_none=True)
	if Edit["welcome_chan"] != UNDEFINED:
		error:bool = False
		if not Edit["welcome_chan"]:
			update["welcome_chan"] = None
		else:
			Chan:discord.TextChannel = getDiscordChannelFromString(PhaazeDiscord, Guild, Edit["welcome_chan"], required_type="text")
			if not Chan:
				error = True
			else:
				update["welcome_chan"] = str(Chan.id)

		if error:
			return await cls.Tree.Api.errors.apiWrongData(cls, WebRequest, msg=f"'{Edit['welcome_chan']}' could not be resolved as a valid discord text channel")

	# welcome_msg
	Edit["welcome_msg"] = Data.getStr("welcome_msg", UNDEFINED, len_max=1750, allow_none=True)
	if Edit["welcome_msg"] != UNDEFINED:
		if not Edit["welcome_msg"]:
			update["welcome_msg"] = None
		else:
			update["welcome_msg"] = Edit["welcome_msg"]

	# welcome_msg_priv
	Edit["welcome_msg_priv"] = Data.getStr("welcome_msg_priv", UNDEFINED, len_max=1750, allow_none=True)
	if Edit["welcome_msg_priv"] != UNDEFINED:
		if not Edit["welcome_msg_priv"]:
			update["welcome_msg_priv"] = None
		else:
			update["welcome_msg_priv"] = Edit["welcome_msg_priv"]

	if not update:
		return await cls.Tree.Api.errors.apiMissingData(cls, WebRequest, msg="No changes, please add at least one")

	cls.BASE.PhaazeDB.updateQuery(
		table="discord_setting",
		content=update,
		where="`discord_setting`.`guild_id` = %s",
		where_values=(Edit["guild_id"],)
	)

	# logging
	log_coro:Coroutine = loggingOnConfigEdit(PhaazeDiscord, Configs, Editor=CheckMember, changes=update)
	asyncio.ensure_future(log_coro, loop=cls.BASE.DiscordLoop)

	cls.BASE.Logger.debug(f"(API/Discord) Configs: {Edit['guild_id']=} updated", require="discord:configs")
	return cls.response(
		text=json.dumps(dict(msg="Configs: Updated", changes=update, status=200)),
		content_type="application/json",
		status=200
	)
