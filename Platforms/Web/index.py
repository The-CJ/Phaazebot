from typing import TYPE_CHECKING, Callable
if TYPE_CHECKING:
	from .main_web import PhaazebotWeb

import re
import json
from aiohttp.web import Response, middleware, HTTPException

class WebIndex(object):
	""" Contains all functions for the web to call """
	def __init__(self, Web:"PhaazebotWeb"):
		self.Web:"PhaazebotWeb" = Web
		self.response:Callable = self.sendResponse
		self.FormatHTMLRegex:re.Pattern = re.compile(r"\|>>>\((.+?)\)<<<\|")

	def sendResponse(self, **kwargs):
		already_set_header:dict = kwargs.get('headers', dict())
		kwargs['headers'] = already_set_header
		kwargs['headers']['server'] =f"PhaazeOS v{self.Web.BASE.version}"

		return Response(**kwargs)

	@middleware
	async def middleware_handler(self, request, handler):
		try:
			response = await handler(request)
			return response

		except HTTPException as HTTPEx:
			return self.response(
				body=json.dumps( dict(msg=HTTPEx.reason, status=HTTPEx.status) ),
				status=HTTPEx.status,
				content_type='application/json'
			)
		except Exception as e:
			self.Web.BASE.Logger.error(str(e))
