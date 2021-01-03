from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.main_web import PhaazebotWeb

import os
import json
import mimetypes
from aiohttp.web import Response
from Platforms.Web.index import PhaazeWebIndex
from Utils.Classes.extendedrequest import ExtendedRequest

CONTENTFOLDER_CSS = "Platforms/Web/Content/Css"
CONTENTFOLDER_JS = "Platforms/Web/Content/Js"
CONTENTFOLDER_IMG = "Platforms/Web/Content/Img"

# content serve functions
@PhaazeWebIndex.get("/css{file:.*}")
async def serveCss(cls:"PhaazebotWeb", WebRequest:ExtendedRequest) -> Response:
	"""
	Default url: /css/*
	"""
	file_location:str = WebRequest.match_info.get("file", None)
	if not file_location: return await noFileDefined(cls)

	# remove all injection things
	file_location = file_location.replace("..","").strip("/")

	# not found in filesystem
	if not os.path.isfile(f"{CONTENTFOLDER_CSS}/{file_location}"):
		return await fileNotFound(cls, file_location)

	try:
		file_content:bytes = open(f"{CONTENTFOLDER_CSS}/{file_location}", "rb").read()
	except FileNotFoundError:
		return await fileNotFound(cls, file_location)

	return cls.response(
		status=200,
		content_type='text/css',
		body=file_content
	)

@PhaazeWebIndex.get("/js{file:.*}")
async def serveJs(cls:"PhaazebotWeb", WebRequest:ExtendedRequest) -> Response:
	"""
	Default url: /js/*
	"""
	file_location:str = WebRequest.match_info.get("file", None)
	if not file_location: return await noFileDefined(cls)

	# remove all injection things
	file_location = file_location.replace("..","").strip("/")

	# not found in filesystem
	if not os.path.isfile(f"{CONTENTFOLDER_JS}/{file_location}"):
		return await fileNotFound(cls, file_location)

	try:
		file_content:bytes = open(f"{CONTENTFOLDER_JS}/{file_location}", "rb").read()

	except FileNotFoundError:
		# should not happen, since we checked before, but who cares
		return await fileNotFound(cls, file_location)

	return cls.response(
		status=200,
		content_type='application/javascript',
		body=file_content
	)

@PhaazeWebIndex.get("/img{file:.*}")
async def serveImg(cls:"PhaazebotWeb", WebRequest:ExtendedRequest) -> Response:
	"""
	Default url: /img/*
	"""
	file_location:str = WebRequest.match_info.get("file", None)
	if not file_location: return await noFileDefined(cls)

	# remove all injection things
	file_location = file_location.replace("..","").strip("/")

	# not found in filesystem
	if not os.path.isfile(f"{CONTENTFOLDER_IMG}/{file_location}"):
		return await fileNotFound(cls, file_location)

	try:
		file_content:bytes = open(f"{CONTENTFOLDER_IMG}/{file_location}", "rb").read()
	except FileNotFoundError:
		return await fileNotFound(cls, file_location)

	return cls.response(
		status=200,
		content_type=mimetypes.guess_type(f"{CONTENTFOLDER_IMG}/{file_location}", strict=True)[0],
		body=file_content
	)

@PhaazeWebIndex.get("/favicon.ico")
async def serveFavicon(cls:"PhaazebotWeb", WebRequest:ExtendedRequest) -> Response:
	"""
	Default url: /favicon.ico
	"""
	WebRequest.match_info["file"] = "favicon.ico"
	return await serveImg(cls, WebRequest)

# error handling
async def noFileDefined(cls:"PhaazebotWeb") -> Response:
	return cls.response(
		status=400,
		content_type='application/json',
		body=json.dumps(dict(error="no_file_defined",status=400))
	)

async def fileNotFound(cls:"PhaazebotWeb", file_name:str) -> Response:
	return cls.response(
		status=404,
		content_type='application/json',
		body=json.dumps(dict(error="file_not_found", status=404, file=file_name))
	)
