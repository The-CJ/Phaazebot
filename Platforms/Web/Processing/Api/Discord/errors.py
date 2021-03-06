from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.main_web import PhaazebotWeb

import json
from aiohttp.web import Response
from Utils.Classes.extendedrequest import ExtendedRequest

async def apiDiscordGuildUnknown(cls:"PhaazebotWeb", WebRequest:ExtendedRequest, **kwargs) -> Response:
	"""
	Optional keywords:
	------------------
	* msg `str` : (Default: None) * [Overwrites default]
	* guild_id `str` *
	* guild_name `str` *

	Default message (*gets altered by optional keywords):
	----------------------------------------------------
	Could not find a phaaze known guild
	"""
	res:dict = dict(status=400, error="discord_guild_unknown")

	guild_id:str = kwargs.get("guild_id", "")
	if guild_id:
		res["guild_id"] = str(guild_id)

	guild_name:str = kwargs.get("guild_name", "")
	if guild_name:
		res["guild_name"] = str(guild_name)

	# build message
	default_msg:str = "Could not find a phaaze known guild"

	if guild_name:
		default_msg += f" with name '{guild_name}'"

	if guild_id:
		default_msg += f" (Guild ID:{guild_id})"

	msg:str = kwargs.get("msg", default_msg)
	res["msg"] = msg

	cls.BASE.Logger.debug(f"(API/Discord) 400: {WebRequest.path} | {msg}", require="api:400")
	return cls.response(
		text=json.dumps(res),
		content_type="application/json",
		status=400
	)

async def apiDiscordMissingPermission(cls:"PhaazebotWeb", WebRequest:ExtendedRequest, **kwargs) -> Response:
	"""
	Optional keywords:
	------------------
	* msg `str` : (Default: None) * [Overwrites default]
	* user_id `str` *
	* user_name `str` *
	* guild_id `str`
	* guild_name `str`

	Default message (*gets altered by optional keywords):
	----------------------------------------------------
	Missing 'administrator' or 'manage_guild' permission
	"""
	res:dict = dict(status=400, error="discord_missing_permission")

	user_id:str = kwargs.get("user_id", "")
	if user_id:
		res["user_id"] = str(user_id)

	user_name:str = kwargs.get("user_name", "")
	if user_name:
		res["user_name"] = str(user_name)

	guild_id:str = kwargs.get("guild_id", "")
	if guild_id:
		res["guild_id"] = str(guild_id)

	guild_name:str = kwargs.get("guild_name", "")
	if guild_name:
		res["guild_name"] = str(guild_name)

	# build message
	default_msg:str = "Missing 'administrator' or 'manage_guild' permission"

	if user_name:
		default_msg += f" for user '{user_name}'"

	if user_id:
		default_msg += f" (User ID:{user_id})"

	msg:str = kwargs.get("msg", default_msg)
	res["msg"] = msg

	cls.BASE.Logger.debug(f"(API/Discord) 400 Missing Permission: {WebRequest.path} | {msg}", require="api:400")
	return cls.response(
		text=json.dumps(res),
		content_type="application/json",
		status=400
	)

async def apiDiscordMemberNotFound(cls:"PhaazebotWeb", WebRequest:ExtendedRequest, **kwargs) -> Response:
	"""
	Optional keywords:
	------------------
	* msg `str` : (Default: None) * [Overwrites default]
	* user_id `str` *
	* user_name `str` *
	* guild_id `str`
	* guild_name `str`

	Default message (*gets altered by optional keywords):
	----------------------------------------------------
	Could not find a valid member
	"""
	res:dict = dict(status=404, error="discord_member_not_found")

	user_id:str = kwargs.get("user_id", "")
	if user_id:
		res["user_id"] = str(user_id)

	user_name:str = kwargs.get("user_name", "")
	if user_name:
		res["user_name"] = str(user_name)

	guild_id:str = kwargs.get("guild_id", "")
	if guild_id:
		res["guild_id"] = str(guild_id)

	guild_name:str = kwargs.get("guild_name", "")
	if guild_name:
		res["guild_name"] = str(guild_name)

	# build message
	default_msg:str = "Could not find a valid member"

	if user_name:
		default_msg += f" with name '{user_name}'"

	if user_id:
		default_msg += f" (User ID: {user_id})"

	msg:str = kwargs.get("msg", default_msg)
	res["msg"] = msg

	cls.BASE.Logger.debug(f"(API/Discord) 400 Member not Found: {WebRequest.path} | {msg}", require="api:404")
	return cls.response(
		text=json.dumps(res),
		content_type="application/json",
		status=404
	)

async def apiDiscordRoleNotFound(cls:"PhaazebotWeb", WebRequest:ExtendedRequest, **kwargs) -> Response:
	"""
	Optional keywords:
	------------------
	* msg `str` : (Default: None) * [Overwrites default]
	* role_id `str` *
	* role_name `str` *
	* guild_id `str`
	* guild_name `str`

	Default message (*gets altered by optional keywords):
	----------------------------------------------------
	Could not find a valid role
	"""
	res:dict = dict(status=404, error="discord_role_not_found")

	role_id:str = kwargs.get("role_id", "")
	if role_id:
		res["role_id"] = str(role_id)

	role_name:str = kwargs.get("role_name", "")
	if role_name:
		res["role_name"] = str(role_name)

	guild_id:str = kwargs.get("guild_id", "")
	if guild_id:
		res["guild_id"] = str(guild_id)

	guild_name:str = kwargs.get("guild_name", "")
	if guild_name:
		res["guild_name"] = str(guild_name)

	# build message
	default_msg:str = "Could not find a valid role"

	if role_name:
		default_msg += f" with name '{role_name}'"

	if role_id:
		default_msg += f" (Role ID:{role_id})"

	msg:str = kwargs.get("msg", default_msg)
	res["msg"] = msg

	cls.BASE.Logger.debug(f"(API/Discord) 400 Role not Found: {WebRequest.path} | {msg}", require="api:404")
	return cls.response(
		text=json.dumps(res),
		content_type="application/json",
		status=404
	)

async def apiDiscordChannelNotFound(cls:"PhaazebotWeb", WebRequest:ExtendedRequest, **kwargs) -> Response:
	"""
	Optional keywords:
	------------------
	* msg `str` : (Default: None) * [Overwrites default]
	* channel_id `str` *
	* channel_name `str` *
	* guild_id `str`
	* guild_name `str`

	Default message (*gets altered by optional keywords):
	----------------------------------------------------
	Could not find a valid channel
	"""
	res:dict = dict(status=404, error="discord_channel_not_found")

	channel_id:str = kwargs.get("channel_id", "")
	if channel_id:
		res["channel_id"] = str(channel_id)

	channel_name:str = kwargs.get("channel_name", "")
	if channel_name:
		res["channel_name"] = str(channel_name)

	guild_id:str = kwargs.get("guild_id", "")
	if guild_id:
		res["guild_id"] = str(guild_id)

	guild_name:str = kwargs.get("guild_name", "")
	if guild_name:
		res["guild_name"] = str(guild_name)

	# build message
	default_msg:str = "Could not find a valid channel"

	if channel_name:
		default_msg += f" with name '{channel_name}'"

	if channel_id:
		default_msg += f" (Channel ID:{channel_id})"

	msg:str = kwargs.get("msg", default_msg)
	res["msg"] = msg

	cls.BASE.Logger.debug(f"(API/Discord) 400 Channel not Found: {WebRequest.path} | {msg}", require="api:404")
	return cls.response(
		text=json.dumps(res),
		content_type="application/json",
		status=404
	)
