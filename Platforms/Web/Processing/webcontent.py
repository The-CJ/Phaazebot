from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex

import json, mimetypes
from aiohttp.web import Request, Response

CONTENTFOLDER_CSS = "Platforms/Web/Content/Css"
CONTENTFOLDER_JS = "Platforms/Web/Content/Js"
CONTENTFOLDER_IMG = "Platforms/Web/Content/Img"

# content serve functions
async def serveCss(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
		Default url: /css/*
	"""
	file_location:str = WebRequest.match_info.get("file", None)
	if not file_location: return noFileDefined(cls)

	file_location = file_location.replace("..","").strip("/")

	try:
		file_content:bytes = open(f"{CONTENTFOLDER_CSS}/{file_location}", "rb").read()
	except FileNotFoundError:
		return await fileNotFound(cls, file_location)

	return cls.response(
		status=200,
		content_type='text/css',
		body=file_content
	)

async def serveJs(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
		Default url: /js/*
	"""
	file_location:str = WebRequest.match_info.get("file", None)
	if not file_location: return noFileDefined(cls)

	file_location = file_location.replace("..","").strip("/")

	try:
		file_content:bytes = open(f"{CONTENTFOLDER_JS}/{file_location}", "rb").read()
	except FileNotFoundError:
		return await fileNotFound(cls, file_location)

	return cls.response(
		status=200,
		content_type='application/javascript',
		body=file_content
	)

async def serveImg(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
		Default url: /img/*
	"""
	file_location:str = WebRequest.match_info.get("file", None)
	if not file_location: return noFileDefined(cls)

	file_location = file_location.replace("..","").strip("/")

	try:
		file_content:bytes = open(f"{CONTENTFOLDER_IMG}/{file_location}", "rb").read()
	except FileNotFoundError:
		return await fileNotFound(cls, file_location)

	return cls.response(
		status=200,
		content_type=mimetypes.guess_type(f"{CONTENTFOLDER_IMG}/{file_location}", strict=True)[0],
		body=file_content
	)

async def serveFavicon(cls:"WebIndex", WebRequest:Request) -> Response:
	WebRequest.match_info["file"] = "favicon.ico"
	return await cls.serveImg(WebRequest)

# error handling
async def noFileDefined(cls:"WebIndex") -> Response:
	return cls.response(
		status=400,
		content_type='application/json',
		body=json.dumps( dict( error="no_file_defined",status=400 ) )
	)

async def fileNotFound(cls:"WebIndex", file_name:str) -> Response:
	return cls.response(
		status=404,
		content_type='application/json',
		body=json.dumps( dict( error="file_not_found", status=404, file=file_name ) )
	)
