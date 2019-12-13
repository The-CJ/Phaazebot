from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex

import json
from aiohttp.web import Response, Request

async def apiDiscordGuildUnknown(cls:"WebIndex", WebRequest:Request, **kwargs:dict) -> Response:
	"""
		Takes from kwargs:
			msg:str
	"""
	default_msg:str = "could not find a phaaze known guild"
	msg:str = kwargs.get("msg", default_msg)

	cls.Web.BASE.Logger.debug(f"(API/Discord) 400: {WebRequest.path}", require="api:400")
	return cls.response(
		text=json.dumps( dict(status=400, msg=msg, error="discord_guild_unknown") ),
		content_type="application/json",
		status=400
	)

async def apiDiscordMissingPermission(cls:"WebIndex", WebRequest:Request, **kwargs:dict) -> Response:
	"""
		Takes from kwargs:
			msg:str
			user_id:str
			guild_id:str
	"""
	res:dict = dict(status=400, error="discord_missing_permission")

	default_msg:str = "missing 'administrator' or 'manage_guild' permission"
	msg:str = kwargs.get("msg", default_msg)
	res["msg"] = msg

	user_id:str = kwargs.get("user_id", "")
	if user_id:
		res["user_id"] = user_id

	guild_id:str = kwargs.get("guild_id", "")
	if guild_id:
		res["guild_id"] = guild_id

	cls.Web.BASE.Logger.debug(f"(API/Discord) 400 Missing Permission: {WebRequest.path}", require="api:400")
	return cls.response(
		text=json.dumps( res ),
		content_type="application/json",
		status=400
	)

# not found
async def apiDiscordMemberNotFound(cls:"WebIndex", WebRequest:Request, **kwargs:dict) -> Response:
	"""
		Takes from kwargs:
			msg:str
			user_id:str
			guild_id:str
	"""
	res:dict = dict(status=404, error="discord_member_not_found")

	default_msg:str = "could not find a valid member on this guild"
	msg:str = kwargs.get("msg", default_msg)
	res["msg"] = msg

	user_id:str = kwargs.get("user_id", "")
	if user_id:
		res["user_id"] = user_id

	guild_id:str = kwargs.get("guild_id", "")
	if guild_id:
		res["guild_id"] = guild_id

	cls.Web.BASE.Logger.debug(f"(API/Discord) 400 Member not Found: {WebRequest.path}", require="api:404")
	return cls.response(
		text=json.dumps( res ),
		content_type="application/json",
		status=404
	)

async def apiDiscordRoleNotFound(cls:"WebIndex", WebRequest:Request, **kwargs:dict) -> Response:
	"""
		Takes from kwargs:
			msg:str
			role_id:str
			guild_id:str
	"""
	res:dict = dict(status=404, error="discord_role_not_found")

	default_msg:str = "could not find a valid role on this guild"
	msg:str = kwargs.get("msg", default_msg)
	res["msg"] = msg

	role_id:str = kwargs.get("role_id", "")
	if role_id:
		res["role_id"] = role_id

	guild_id:str = kwargs.get("guild_id", "")
	if guild_id:
		res["guild_id"] = guild_id

	cls.Web.BASE.Logger.debug(f"(API/Discord) 400 Role not Found: {WebRequest.path}", require="api:404")
	return cls.response(
		text=json.dumps( res ),
		content_type="application/json",
		status=404
	)

async def apiDiscordChannelNotFound(cls:"WebIndex", WebRequest:Request, **kwargs:dict) -> Response:
	"""
		Takes from kwargs:
			msg:str
			channel_id:str
			guild_id:str
	"""
	res:dict = dict(status=404, error="discord_channel_not_found")

	default_msg:str = "could not find a valid channel on this guild"
	msg:str = kwargs.get("msg", default_msg)
	res["msg"] = msg

	channel_id:str = kwargs.get("channel_id", "")
	if channel_id:
		res["channel_id"] = channel_id

	guild_id:str = kwargs.get("guild_id", "")
	if guild_id:
		res["guild_id"] = guild_id

	cls.Web.BASE.Logger.debug(f"(API/Discord) 400 Channel not Found: {WebRequest.path}", require="api:404")
	return cls.response(
		text=json.dumps( res ),
		content_type="application/json",
		status=404
	)

# not/already exists
async def apiDiscordCommandExists(cls:"WebIndex", WebRequest:Request, **kwargs:dict) -> Response:
	"""
		Takes from kwargs:
			msg:str
			command:str
	"""
	res:dict = dict(status=400, error="discord_command_exists")

	default_msg:str = "This command trigger already exists"
	msg:str = kwargs.get("msg", default_msg)
	res["msg"] = msg

	command:str = kwargs.get("command", "")
	if command:
		res["command"] = command

	cls.Web.BASE.Logger.debug(f"(API/Discord) 400 Command exits: {WebRequest.path}", require="api:400")
	return cls.response(
		text=json.dumps( res ),
		content_type="application/json",
		status=400
	)

async def apiDiscordCommandNotExists(cls:"WebIndex", WebRequest:Request, **kwargs:dict) -> Response:
	"""
		Takes from kwargs:
			msg:str
			command:str
	"""
	res:dict = dict(status=400, error="discord_command_not_exists")

	default_msg:str = "No command has been found"
	msg:str = kwargs.get("msg", default_msg)
	res["msg"] = msg

	command:str = kwargs.get("command", "")
	if command:
		res["command"] = command

	cls.Web.BASE.Logger.debug(f"(API/Discord) 400 Command not found: {WebRequest.path}", require="api:400")
	return cls.response(
		text=json.dumps( res ),
		content_type="application/json",
		status=400
	)

async def apiDiscordQuotesNotExists(cls:"WebIndex", WebRequest:Request, **kwargs:dict) -> Response:
	"""
		Takes from kwargs:
			msg:str
			quote_id:str
	"""
	res:dict = dict(status=400, error="discord_quote_not_exists")

	default_msg:str = "No quote has been found"
	msg:str = kwargs.get("msg", default_msg)
	res["msg"] = msg

	quote_id:str = kwargs.get("quote_id", "")
	if quote_id:
		res["quote_id"] = quote_id

	cls.Web.BASE.Logger.debug(f"(API/Discord) 400 Command not found: {WebRequest.path}", require="api:400")
	return cls.response(
		text=json.dumps( res ),
		content_type="application/json",
		status=400
	)

async def apiDiscordAssignRoleExists(cls:"WebIndex", WebRequest:Request, **kwargs:dict) -> Response:
	"""
		Takes from kwargs:
			msg:str
			role_id:str
			trigger:str
	"""
	res:dict = dict(status=400, error="discord_assignrole_exists")

	default_msg:str = "Assignrole already exists"
	msg:str = kwargs.get("msg", default_msg)
	res["msg"] = msg

	role_id:str = kwargs.get("role_id", "")
	if role_id:
		res["role_id"] = role_id

	trigger:str = kwargs.get("trigger", "")
	if trigger:
		res["trigger"] = trigger

	cls.Web.BASE.Logger.debug(f"(API/Discord) 400 Assignrole exists: {WebRequest.path}", require="api:400")
	return cls.response(
		text=json.dumps( res ),
		content_type="application/json",
		status=400
	)

# limits
async def apiDiscordCommandLimit(cls:"WebIndex", WebRequest:Request, **kwargs:dict) -> Response:
	"""
		Takes from kwargs:
			msg:str
			limit:str
	"""
	res:dict = dict(status=400, error="discord_command_limit")

	default_msg:str = "You have hit the limit of commands for this server"
	msg:str = kwargs.get("msg", default_msg)
	res["msg"] = msg

	limit:str = kwargs.get("limit", cls.Web.BASE.Limit.DISCORD_COMMANDS_AMOUNT)
	if limit:
		res["limit"] = limit

	cls.Web.BASE.Logger.debug(f"(API/Discord) 400 Too many commands: {WebRequest.path}", require="api:400")
	return cls.response(
		text=json.dumps( res ),
		content_type="application/json",
		status=400
	)

async def apiDiscordLevelMedalLimit(cls:"WebIndex", WebRequest:Request, **kwargs:dict) -> Response:
	"""
		Takes from kwargs:
			msg:str
			limit:str
	"""
	res:dict = dict(status=400, error="discord_medal_limit")

	default_msg:str = "You have hit the limit of medals for this member"
	msg:str = kwargs.get("msg", default_msg)
	res["msg"] = msg

	limit:str = kwargs.get("limit", cls.Web.BASE.Limit.DISCORD_LEVEL_MEDAL_AMOUNT)
	if limit:
		res["limit"] = limit

	cls.Web.BASE.Logger.debug(f"(API/Discord) 400 Too many medals: {WebRequest.path}", require="api:400")
	return cls.response(
		text=json.dumps( res ),
		content_type="application/json",
		status=400
	)

async def apiDiscordQuoteLimit(cls:"WebIndex", WebRequest:Request, **kwargs:dict) -> Response:
	"""
		Takes from kwargs:
			msg:str
			limit:str
	"""
	res:dict = dict(status=400, error="discord_quote_limit")

	default_msg:str = "You have hit the limit of quotes for this guild"
	msg:str = kwargs.get("msg", default_msg)
	res["msg"] = msg

	limit:str = kwargs.get("limit", cls.Web.BASE.Limit.DISCORD_QUOTES_AMOUNT)
	if limit:
		res["limit"] = limit

	cls.Web.BASE.Logger.debug(f"(API/Discord) 400 Too many quotes: {WebRequest.path}", require="api:400")
	return cls.response(
		text=json.dumps( res ),
		content_type="application/json",
		status=400
	)

async def apiDiscordAssignRoleLimit(cls:"WebIndex", WebRequest:Request, **kwargs:dict) -> Response:
	"""
		Takes from kwargs:
			msg:str
			limit:str
	"""
	res:dict = dict(status=400, error="discord_quote_limit")

	default_msg:str = "You have hit the limit of assign roles for this guild"
	msg:str = kwargs.get("msg", default_msg)
	res["msg"] = msg

	limit:str = kwargs.get("limit", cls.Web.BASE.Limit.DISCORD_ASSIGNROLE_AMOUNT)
	if limit:
		res["limit"] = limit

	cls.Web.BASE.Logger.debug(f"(API/Discord) 400 Too many assign roles: {WebRequest.path}", require="api:400")
	return cls.response(
		text=json.dumps( res ),
		content_type="application/json",
		status=400
	)
