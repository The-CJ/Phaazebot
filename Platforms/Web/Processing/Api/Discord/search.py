from typing import TYPE_CHECKING, List, Union
if TYPE_CHECKING:
	from Platforms.Discord.main_discord import PhaazebotDiscord
	from Platforms.Web.main_web import PhaazebotWeb

import json
import discord
from aiohttp.web import Response
from Utils.Classes.webrequestcontent import WebRequestContent
from Utils.Classes.extendedrequest import ExtendedRequest
from Platforms.Web.Processing.Api.errors import apiNotAllowed, apiMissingData
from Platforms.Web.index import PhaazeWebIndex
from Platforms.Discord.utils import (
	getDiscordChannelFromString,
	getDiscordMemberFromString,
	getDiscordGuildFromString,
	getDiscordRoleFromString,
)
from Platforms.Web.Processing.Api.Discord.errors import (
	apiDiscordChannelNotFound,
	apiDiscordMemberNotFound,
	apiDiscordGuildUnknown,
	apiDiscordRoleNotFound,
)

SEARCH_OPTIONS:List[str] = ["guild", "member", "role", "channel"]

@PhaazeWebIndex.view("/api/discord/search")
async def apiDiscordSearch(cls:"PhaazebotWeb", WebRequest:ExtendedRequest) -> Response:
	"""
	Default url: /api/discord/search
	"""
	PhaazeDiscord:"PhaazebotDiscord" = cls.BASE.Discord
	if not PhaazeDiscord: return await apiNotAllowed(cls, WebRequest, msg="Discord module is not active")

	Data:WebRequestContent = WebRequestContent(WebRequest)
	await Data.load()

	search:str = Data.getStr("search", "", len_max=128)
	term:str = Data.getStr("term", "", len_max=512)

	if search not in SEARCH_OPTIONS:
		return await apiMissingData(cls, WebRequest, msg="missing or invalid 'search', allowed: " + ", ".join(SEARCH_OPTIONS))

	if not term:
		return await apiMissingData(cls, WebRequest, msg="invalid or missing 'term'")

	if search == "guild":
		return await searchGuild(cls, WebRequest, Data)

	if search == "member":
		return await searchMember(cls, WebRequest, Data)

	if search == "role":
		return await searchRole(cls, WebRequest, Data)

	if search == "channel":
		return await searchChannel(cls, WebRequest, Data)

async def searchGuild(cls:"PhaazebotWeb", WebRequest:ExtendedRequest, Data:WebRequestContent) -> Response:
	search_term:str = Data.getStr("term", "")

	Guild:discord.Guild = getDiscordGuildFromString(cls.BASE.Discord, search_term, contains=True)
	if not Guild: return await apiDiscordGuildUnknown(cls, WebRequest)

	data:dict = {
		"name": str(Guild.name),
		"id": str(Guild.id),
		"owner_id": str(Guild.owner_id),
		"icon": Guild.icon,
		"banner": Guild.banner
	}

	return cls.response(
		text=json.dumps(
			dict(result=data, status=200)
		),
		content_type="application/json",
		status=200
	)

async def searchMember(cls:"PhaazebotWeb", WebRequest:ExtendedRequest, Data:WebRequestContent) -> Response:
	search_term:str = Data.getStr("term", "")
	guild_id:str = Data.getStr("guild_id", "", must_be_digit=True)

	if not guild_id:
		return await apiMissingData(cls, WebRequest, msg="invalid or missing 'guild_id'")

	Guild:discord.Guild = discord.utils.get(cls.BASE.Discord.guilds, id=int(guild_id))
	if not Guild:
		return await apiDiscordGuildUnknown(cls, WebRequest)

	Member:discord.Member = getDiscordMemberFromString(cls.BASE.Discord, Guild, search_term)
	if not Member: return await apiDiscordMemberNotFound(cls, WebRequest)

	data:dict = {
		"name": str(Member.name),
		"nick": Member.nick,
		"id": str(Member.id),
		"discriminator": Member.discriminator,
		"avatar": Member.avatar
	}

	return cls.response(
		text=json.dumps(
			dict(result=data, status=200)
		),
		content_type="application/json",
		status=200
	)

async def searchRole(cls:"PhaazebotWeb", WebRequest:ExtendedRequest, Data:WebRequestContent) -> Response:
	search_term:str = Data.getStr("term", "")
	guild_id:str = Data.getStr("guild_id", "", must_be_digit=True)

	if not guild_id:
		return await apiMissingData(cls, WebRequest, msg="invalid or missing 'guild_id'")

	Guild:discord.Guild = discord.utils.get(cls.BASE.Discord.guilds, id=int(guild_id))
	if not Guild:
		return await apiDiscordGuildUnknown(cls, WebRequest)

	Role:discord.Role = getDiscordRoleFromString(cls.BASE.Discord, Guild, search_term, contains=True)
	if not Role: return await apiDiscordRoleNotFound(cls, WebRequest)

	data:dict = {
		"name": str(Role.name),
		"id": str(Role.id),
		"color": Role.color.value,
		"managed": Role.managed,
		"position": Role.position
	}

	return cls.response(
		text=json.dumps(
			dict(result=data, status=200)
		),
		content_type="application/json",
		status=200
	)

async def searchChannel(cls:"PhaazebotWeb", WebRequest:ExtendedRequest, Data:WebRequestContent) -> Response:
	search_term:str = Data.getStr("term", "")
	guild_id:str = Data.getStr("guild_id", "", must_be_digit=True)

	if not guild_id:
		return await apiMissingData(cls, WebRequest, msg="invalid or missing 'guild_id'")

	Guild:discord.Guild = discord.utils.get(cls.BASE.Discord.guilds, id=int(guild_id))
	if not Guild:
		return await apiDiscordGuildUnknown(cls, WebRequest)

	Channel:Union[discord.TextChannel, discord.VoiceChannel, discord.CategoryChannel] = getDiscordChannelFromString(cls.BASE.Discord, Guild, search_term, contains=True)
	if not Channel: return await apiDiscordChannelNotFound(cls, WebRequest)

	data:dict = {
		"name": str(Channel.name),
		"id": str(Channel.id),
		"position": Channel.position,
	}

	if type(Channel) is discord.TextChannel:
		data["channel_type"] = "text"

	elif type(Channel) is discord.VoiceChannel:
		data["channel_type"] = "voice"

	elif type(Channel) is discord.CategoryChannel:
		data["channel_type"] = "category"

	else:
		data["channel_type"] = "unknown"

	return cls.response(
		text=json.dumps(
			dict(result=data, status=200)
		),
		content_type="application/json",
		status=200
	)
