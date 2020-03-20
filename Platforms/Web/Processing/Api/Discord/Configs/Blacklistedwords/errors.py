from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex

import json
from aiohttp.web import Response, Request

async def apiDiscordBlacklistWordExists(cls:"WebIndex", WebRequest:Request, **kwargs:dict) -> Response:
	"""
	Optional keywords:
	------------------
	* msg `str` : (Default: None) * [Overwrites default]
	* word `str` *

	Default message (*gets altered by optional keywords):
	----------------------------------------------------
	Blacklisted word already exists
	"""
	res:dict = dict(status=400, error="discord_assignrole_exists")

	word:str = kwargs.get("word", "")
	if word:
		res["word"] = str(word)

	# build message
	default_msg:str = "Blacklisted word already exists"

	if word:
		default_msg += f" (Word: {word})"

	msg:str = kwargs.get("msg", default_msg)
	res["msg"] = msg

	cls.Web.BASE.Logger.debug(f"(API/Discord) 400 Word exists: {WebRequest.path}", require="api:400")
	return cls.response(
		text=json.dumps( res ),
		content_type="application/json",
		status=400
	)

async def apiDiscordBlacklistWordNotExists(cls:"WebIndex", WebRequest:Request, **kwargs:dict) -> Response:
	"""
	Optional keywords:
	------------------
	* msg `str` : (Default: None) * [Overwrites default]
	* word `str` *
	* word_id `str` *

	Default message (*gets altered by optional keywords):
	----------------------------------------------------
	Blacklisted word does not exists
	"""
	res:dict = dict(status=400, error="discord_blacklistword_not_exists")

	word_id:str = kwargs.get("word_id", "")
	if word_id:
		res["word_id"] = str(word_id)

	word:str = kwargs.get("word", "")
	if word:
		res["word"] = str(word)

	# build message
	default_msg:str = "Blacklisted word does not exists"

	if word:
		default_msg += f" (Word: {word})"

	if word_id:
		default_msg += f" (Word ID: {word_id})"

	msg:str = kwargs.get("msg", default_msg)
	res["msg"] = msg

	cls.Web.BASE.Logger.debug(f"(API/Discord) 400 Word not exists: {WebRequest.path}", require="api:400")
	return cls.response(
		text=json.dumps( res ),
		content_type="application/json",
		status=400
	)
