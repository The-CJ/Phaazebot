from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Discord.main_discord import PhaazebotDiscord
	from Platforms.Web.main_web import PhaazebotWeb

import json
import discord
from aiohttp.web import Response
from Utils.Classes.storagetransformer import StorageTransformer
from Utils.Classes.authdiscordwebuser import AuthDiscordWebUser
from Utils.Classes.webrequestcontent import WebRequestContent
from Utils.Classes.extendedrequest import ExtendedRequest
from Utils.Classes.undefined import UNDEFINED
from Platforms.Web.utils import authDiscordWebUser
from Platforms.Discord.utils import getDiscordChannelFromString

async def apiDiscordConfigsGameEnabledChannelsCreate(cls:"PhaazebotWeb", WebRequest:ExtendedRequest) -> Response:
	"""
	Default url: /api/discord/configs/gameenabledchannels/create
	"""
	Data:WebRequestContent = WebRequestContent(WebRequest)
	await Data.load()

	# get required stuff
	Create:StorageTransformer = StorageTransformer()
	Create["guild_id"] = Data.getStr("guild_id", UNDEFINED, must_be_digit=True)
	Create["channel_id"] = Data.getStr("channel_id", UNDEFINED, must_be_digit=True)

	# checks
	if not Create["guild_id"]:
		return await cls.Tree.Api.errors.apiMissingData(cls, WebRequest, msg="missing or invalid 'guild_id'")

	if not Create["channel_id"]:
		return await cls.Tree.Api.errors.apiMissingData(cls, WebRequest, msg="missing or invalid 'channel_id'")

	PhaazeDiscord:"PhaazebotDiscord" = cls.BASE.Discord
	Guild:discord.Guild = discord.utils.get(PhaazeDiscord.guilds, id=int(Create["guild_id"]))
	if not Guild:
		return await cls.Tree.Api.Discord.errors.apiDiscordGuildUnknown(cls, WebRequest)

	# get user info
	AuthDiscord:AuthDiscordWebUser = await authDiscordWebUser(cls, WebRequest)
	if not AuthDiscord.found:
		return await cls.Tree.Api.errors.apiMissingAuthorisation(cls, WebRequest)

	# get member
	CheckMember:discord.Member = Guild.get_member(int(AuthDiscord.User.user_id))
	if not CheckMember:
		return await cls.Tree.Api.Discord.errors.apiDiscordMemberNotFound(cls, WebRequest, guild_id=Create["guild_id"], user_id=AuthDiscord.User.user_id)

	# check permissions
	if not (CheckMember.guild_permissions.administrator or CheckMember.guild_permissions.manage_guild):
		return await cls.Tree.Api.Discord.errors.apiDiscordMissingPermission(cls, WebRequest, guild_id=Create["guild_id"], user_id=AuthDiscord.User.user_id)

	ActionChannel:discord.TextChannel = getDiscordChannelFromString(PhaazeDiscord, Guild, Create["channel_id"], required_type="text")
	if not ActionChannel:
		return await cls.Tree.Api.Discord.errors.apiDiscordChannelNotFound(cls, WebRequest, channel_id=Create["channel_id"])

	# check if already exists
	res:list = cls.BASE.PhaazeDB.selectQuery("""
		SELECT COUNT(*) AS `match`
		FROM `discord_enabled_gamechannel`
		WHERE `discord_enabled_gamechannel`.`guild_id` = %s
			AND `discord_enabled_gamechannel`.`channel_id` = %s""",
		(Create["guild_id"], Create["channel_id"])
	)

	if res[0]["match"]:
		return await cls.Tree.Api.Discord.Configs.Gameenabledchannels.errors.apiDiscordConfigsGameEnabledChannelExists(cls, WebRequest, channel_id=Create["channel_id"], channel_name=ActionChannel.name)

	cls.BASE.PhaazeDB.insertQuery(
		table="discord_enabled_gamechannel",
		content={
			"guild_id": Create["guild_id"],
			"channel_id": Create["channel_id"]
		}
	)

	cls.BASE.Logger.debug(f"(API/Discord) Game enabled channel: {Create['guild_id']=} added: {Create['channel_id']=}", require="discord:configs")
	return cls.response(
		text=json.dumps(dict(msg="Game enabled channel: Added new entry", entry=Create["channel_id"], status=200)),
		content_type="application/json",
		status=200
	)
