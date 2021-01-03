from typing import TYPE_CHECKING, Optional, Callable
if TYPE_CHECKING:
	from phaazebot import Phaazebot

import ssl
import json
import traceback
from aiohttp import web
from Utils.cli import CliArgs
from Utils.Classes.extendedrequest import ExtendedRequest
from Utils.Classes.htmlformatter import HTMLFormatter
from Platforms.Web.index import PhaazeWebIndex

# load in modules in tree down.
# they are liked via decorators
import Platforms.Web.Processing as WebProcessing
__all__ = [WebProcessing]

class PhaazebotWeb(web.Application):
	def __init__(self, BASE:"Phaazebot"):
		super().__init__()
		self.BASE:"Phaazebot" = BASE
		self._client_max_size = self.BASE.Limit.web_client_max_size
		self.port:int = 9001
		self.SSLContext:Optional[ssl.SSLContext] = None
		self.HTMLRoot:HTMLFormatter = HTMLFormatter("Platforms/Web/Content/Html/root.html", template=True)
		self.middlewares.append(self.middlewareHandler)

	def __bool__(self):
		return self.BASE.IsReady.web

	# setup
	def setupRouter(self) -> None:
		self.BASE.Logger.debug(f"Loaded {len(PhaazeWebIndex)} entry point's for webserver")
		self.add_routes(PhaazeWebIndex)

	def setupSSL(self) -> None:
		if CliArgs.get("http", "test") == "live":
			self.port = 443
			self.SSLContext:ssl.SSLContext = ssl.SSLContext()
			ssl_root:str = self.BASE.Vars.ssl_dir.rstrip("/")
			self.SSLContext.load_cert_chain(f"{ssl_root}/fullchain.pem", keyfile=f"{ssl_root}/privkey.pem")
			self.BASE.Logger.info(f"Configured webserver Port={self.port} (live)")

		elif CliArgs.get("http", "test") == "unsecure":
			self.port = 80
			self.BASE.Logger.info(f"Configured webserver Port={self.port} (unsecure)")

		elif CliArgs.get("http", "test") == "error_ssl":
			self.port = 443
			self.BASE.Logger.info(f"Configured webserver Port={self.port} (error_ssl)")

		else:
			self.BASE.Logger.info(f"Configured webserver Port={self.port} (test)")

	# response handling
	def response(self, status:int=200, content_type:str="text/plain", **kwargs) -> web.Response:
		already_set_header:dict = kwargs.get('headers', {})
		kwargs['headers'] = already_set_header
		kwargs['headers']['server'] = f"PhaazeOS v{self.BASE.version}"

		return web.Response(status=status, content_type=content_type, **kwargs)

	@web.middleware # middleware handler, aka logging and error handling
	async def middlewareHandler(self, WebRequest:web.Request, handler:Callable) -> web.Response:
		WebRequest.__class__ = ExtendedRequest # people told me to never do this... well fuck it i do it anyways
		WebRequest:ExtendedRequest
		try:
			if str(handler.__name__) in ["_handle"]:
				raise FileNotFoundError()

			if not self.BASE.Active.web:
				return await WebProcessing.Api.errors.apiNotAllowed(self, WebRequest, msg="Web is disabled and will be shutdown soon")

			if not self.BASE.Active.api and WebRequest.path.startswith("/api"):
				return await WebProcessing.Api.errors.apiNotAllowed(self, WebRequest, msg="API endpoint is not enabled")

			response:web.Response = await handler(self, WebRequest)
			return response

		except web.HTTPException as HTTPEx:
			return self.response(
				body=json.dumps(dict(msg=HTTPEx.reason, status=HTTPEx.status)),
				status=HTTPEx.status,
				content_type='application/json'
			)

		except FileNotFoundError:
			return await WebProcessing.errors.notFound(self, WebRequest)

		except Exception as e:
			tb:str = traceback.format_exc()
			self.BASE.Logger.error(f"(Web) Error in request: {str(e)}\n{tb}")
			error:str = str(e) if CliArgs.get("debug") == "all" else "Unknown error"
			return self.response(
				status=500,
				body=json.dumps(dict(msg=error, status=500)),
				content_type='application/json'
			)

	# runtime
	def start(self) -> None:
		self.setupRouter()
		self.setupSSL()
		self.BASE.Logger.info("Web server ready")

		def void(*_, **__) -> None: pass
		web.run_app(self, handle_signals=False, port=self.port, ssl_context=self.SSLContext, print=void)
