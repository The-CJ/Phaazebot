from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex

import json
from aiohttp.web import Response, Request

async def apiDiscordGuildUnknown(cls:"WebIndex", WebRequest:Request, **kwargs:dict) -> Response:
	"""
		Takes from kwargs:
			msg:str
			guild_id:str
			guild_name:str
	"""
	res:dict = dict(status=400, error="discord_guild_unknown")

	guild_id:str = kwargs.get("guild_id", "")
	if guild_id:
		res["guild_id"] = guild_id

	guild_name:str = kwargs.get("guild_name", "")
	if guild_name:
		res["guild_name"] = guild_name

	# build message
	default_msg:str = "Could not find a phaaze known guild"

	if guild_name:
		default_msg += f" with name '{guild_name}'"

	if guild_id:
		default_msg += f" (Guild ID:{guild_id})"

	msg:str = kwargs.get("msg", default_msg)
	res["msg"] = msg

	cls.Web.BASE.Logger.debug(f"(API/Discord) 400: {WebRequest.path} | {msg}", require="api:400")
	return cls.response(
		text=json.dumps( res ),
		content_type="application/json",
		status=400
	)

async def apiDiscordMissingPermission(cls:"WebIndex", WebRequest:Request, **kwargs:dict) -> Response:
	"""
		Takes from kwargs:
			msg:str
			user_id:str
			user_name:str
			guild_id:str
			guild_name:str
	"""
	res:dict = dict(status=400, error="discord_missing_permission")

	user_id:str = kwargs.get("user_id", "")
	if user_id:
		res["user_id"] = user_id

	user_name:str = kwargs.get("user_name", "")
	if user_name:
		res["user_name"] = user_name

	guild_id:str = kwargs.get("guild_id", "")
	if guild_id:
		res["guild_id"] = guild_id

	guild_name:str = kwargs.get("guild_name", "")
	if guild_name:
		res["guild_name"] = guild_name

	# build message
	default_msg:str = "Missing 'administrator' or 'manage_guild' permission"

	if user_name:
		default_msg += f" for user '{user_name}'"
	if guild_name:
		default_msg += f" on guild '{guild_name}'"

	if user_id:
		default_msg += f" (User ID:{user_id})"
	if guild_id:
		default_msg += f" (Guild ID:{guild_id})"

	msg:str = kwargs.get("msg", default_msg)
	res["msg"] = msg

	cls.Web.BASE.Logger.debug(f"(API/Discord) 400 Missing Permission: {WebRequest.path} | {msg}", require="api:400")
	return cls.response(
		text=json.dumps( res ),
		content_type="application/json",
		status=400
	)

async def apiDiscordMemberNotFound(cls:"WebIndex", WebRequest:Request, **kwargs:dict) -> Response:
	"""
		Takes from kwargs:
			msg:str
			user_id:str
			user_name:str
			guild_id:str
			guild_name:str
	"""
	res:dict = dict(status=404, error="discord_member_not_found")

	user_id:str = kwargs.get("user_id", "")
	if user_id:
		res["user_id"] = user_id

	user_name:str = kwargs.get("user_name", "")
	if user_name:
		res["user_name"] = user_name

	guild_id:str = kwargs.get("guild_id", "")
	if guild_id:
		res["guild_id"] = guild_id

	guild_name:str = kwargs.get("guild_name", "")
	if guild_name:
		res["guild_name"] = guild_name

	# build message
	default_msg:str = "Could not find a valid member"

	if guild_name:
		default_msg += f" on guild '{guild_name}'"
	if user_name:
		default_msg += f" with name '{user_name}'"

	if guild_id:
		default_msg += f" (Guild ID: {guild_id})"
	if user_id:
		default_msg += f" (User ID: {user_id})"

	msg:str = kwargs.get("msg", default_msg)
	res["msg"] = msg

	cls.Web.BASE.Logger.debug(f"(API/Discord) 400 Member not Found: {WebRequest.path} | {msg}", require="api:404")
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
			role_name:str
			guild_id:str
			guild_name:str
	"""
	res:dict = dict(status=404, error="discord_role_not_found")

	role_id:str = kwargs.get("role_id", "")
	if role_id:
		res["role_id"] = role_id

	role_name:str = kwargs.get("role_name", "")
	if role_name:
		res["role_name"] = role_name

	guild_id:str = kwargs.get("guild_id", "")
	if guild_id:
		res["guild_id"] = guild_id

	guild_name:str = kwargs.get("guild_name", "")
	if guild_name:
		res["guild_name"] = guild_name

	# build message
	default_msg:str = "Could not find a valid role"

	if guild_name:
		default_msg += f" on guild '{guild_name}'"
	if role_name:
		default_msg += f" with name '{role_name}'"

	if guild_id:
		default_msg += f" (Guild ID:{guild_id})"
	if role_id:
		default_msg += f" (Role ID:{role_id})"

	msg:str = kwargs.get("msg", default_msg)
	res["msg"] = msg

	cls.Web.BASE.Logger.debug(f"(API/Discord) 400 Role not Found: {WebRequest.path} | {msg}", require="api:404")
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
			channel_name:str
			guild_id:str
			guild_name:str
	"""
	res:dict = dict(status=404, error="discord_channel_not_found")

	channel_id:str = kwargs.get("channel_id", "")
	if channel_id:
		res["channel_id"] = channel_id

	channel_name:str = kwargs.get("channel_name", "")
	if channel_name:
		res["channel_name"] = channel_name

	guild_id:str = kwargs.get("guild_id", "")
	if guild_id:
		res["guild_id"] = guild_id

	guild_name:str = kwargs.get("guild_name", "")
	if guild_name:
		res["guild_name"] = guild_name

	# build message
	default_msg:str = "Could not find a valid channel"

	if guild_name:
		default_msg += f" on guild '{guild_name}'"
	if channel_name:
		default_msg += f" with name '{channel_name}'"

	if guild_id:
		default_msg += f" (Guild ID:{guild_id})"
	if channel_id:
		default_msg += f" (Channel ID:{channel_id})"

	msg:str = kwargs.get("msg", default_msg)
	res["msg"] = msg

	cls.Web.BASE.Logger.debug(f"(API/Discord) 400 Channel not Found: {WebRequest.path} | {msg}", require="api:404")
	return cls.response(
		text=json.dumps( res ),
		content_type="application/json",
		status=404
	)
