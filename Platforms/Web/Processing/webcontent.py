from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex

import json, mimetypes
from aiohttp.web import Request, Response

CONTENTFOLDER_CSS = "Platforms/Web/Content/Css"
CONTENTFOLDER_JS = "Platforms/Web/Content/Js"
CONTENTFOLDER_IMG = "Platforms/Web/Content/Img"

# content serve functions
async def serveCss(self:"WebIndex", Request:Request) -> Response:
	file_location:str = Request.match_info.get("file", None)
	if not file_location: return noFileDefined(self)

	file_location = file_location.replace("..","").strip("/")

	try:
		file_content:bytes = open(f"{CONTENTFOLDER_CSS}/{file_location}", "rb").read()
	except FileNotFoundError:
		return await fileNotFound(self, file_location)

	return self.response(
		status=200,
		content_type='text/css',
		body=file_content
	)

async def serveJs(self:"WebIndex", Request:Request) -> Response:
	file_location:str = Request.match_info.get("file", None)
	if not file_location: return noFileDefined(self)

	file_location = file_location.replace("..","").strip("/")

	try:
		file_content:bytes = open(f"{CONTENTFOLDER_JS}/{file_location}", "rb").read()
	except FileNotFoundError:
		return await fileNotFound(self, file_location)

	return self.response(
		status=200,
		content_type='application/json',
		body=file_content
	)

async def serveImg(self:"WebIndex", Request:Request) -> Response:
	file_location:str = Request.match_info.get("file", None)
	if not file_location: return noFileDefined(self)

	file_location = file_location.replace("..","").strip("/")

	try:
		file_content:bytes = open(f"{CONTENTFOLDER_IMG}/{file_location}", "rb").read()
	except FileNotFoundError:
		return await fileNotFound(self, file_location)

	return self.response(
		status=200,
		content_type=mimetypes.guess_type(f"{CONTENTFOLDER_IMG}/{file_location}", strict=True)[0],
		body=file_content
	)

# error handling
async def noFileDefined(cls:"WebIndex") -> Response:
	return cls.response(
		status=400,
		content_type='application/json',
		text=json.dumps( dict( error="no_file_defined",status=400 ) )
	)

async def fileNotFound(cls:"WebIndex", file_name:str) -> Response:
	return cls.response(
		status=404,
		content_type='application/json',
		text=json.dumps( dict( error="file_not_found", status=404, file=file_name ) )
	)
