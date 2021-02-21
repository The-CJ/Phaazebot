from typing import TYPE_CHECKING, List, Dict, Any
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
from Utils.Classes.discordcommand import DiscordCommand
from Utils.Classes.undefined import UNDEFINED
from Platforms.Web.utils import authDiscordWebUser
from Platforms.Discord.db import getDiscordServerCommands
from Platforms.Web.Processing.Api.errors import apiMissingData, apiMissingAuthorisation
from Platforms.Web.Processing.Api.Discord.errors import apiDiscordGuildUnknown

DEFAULT_LIMIT:int = 50
MAX_LIMIT:int = 100

async def apiDiscordCommandsGet(cls:"PhaazebotWeb", WebRequest:ExtendedRequest) -> Response:
	"""
	Default url: /api/discord/commands/get
	"""
	Data:WebRequestContent = WebRequestContent(WebRequest)
	await Data.load()

	# get required vars
	Search:StorageTransformer = StorageTransformer()
	Search["guild_id"] = Data.getStr("guild_id", UNDEFINED, must_be_digit=True)
	Search["command_id"] = Data.getStr("command_id", UNDEFINED, must_be_digit=True)
	Search["trigger"] = Data.getStr("trigger", UNDEFINED)
	Search["show_hidden"] = Data.getBool("show_hidden", False)
	Search["limit"] = Data.getInt("limit", DEFAULT_LIMIT, min_x=1, max_x=MAX_LIMIT)
	Search["offset"] = Data.getInt("offset", 0, min_x=0)

	# checks
	if not Search["guild_id"]:
		return await apiMissingData(cls, WebRequest, msg="missing or invalid 'guild_id'")

	PhaazeDiscord:"PhaazebotDiscord" = cls.BASE.Discord
	Guild:discord.Guild = discord.utils.get(PhaazeDiscord.guilds, id=int(Search["guild_id"]))
	if not Guild:
		return await apiDiscordGuildUnknown(cls, WebRequest)

	if Search["show_hidden"]:
		# user requested to get full information about commands, requires authorisation

		AuthDiscord:AuthDiscordWebUser = await authDiscordWebUser(cls, WebRequest)
		if not AuthDiscord.found:
			return await apiMissingAuthorisation(cls, WebRequest)

		# get member
		CheckMember:discord.Member = Guild.get_member(int(AuthDiscord.User.user_id))
		if not CheckMember:
			return await cls.Tree.Api.Discord.errors.apiDiscordMemberNotFound(cls, WebRequest, guild_id=Search["guild_id"], user_id=AuthDiscord.User.user_id)

		# check permissions
		if not (CheckMember.guild_permissions.administrator or CheckMember.guild_permissions.manage_guild):
			return await cls.Tree.Api.Discord.errors.apiDiscordMissingPermission(
				cls,
				WebRequest,
				guild_id=Search["guild_id"],
				user_id=AuthDiscord.User.user_id,
				msg="'administrator' or 'manage_guild' permission required to show commands with hidden properties"
			)

	res_commands:List[DiscordCommand] = await getDiscordServerCommands(PhaazeDiscord, **Search.getAllTransform())

	result:Dict[str, Any] = dict(
		result=[Command.toJSON(show_hidden=Search["show_hidden"]) for Command in res_commands],
		limit=Search["limit"],
		offset=Search["offset"],
		total=await getDiscordServerCommands(PhaazeDiscord, count_mode=True, **Search.getAllTransform()),
		status=200
	)

	return cls.response(
		text=json.dumps(result),
		content_type="application/json",
		status=200
	)
