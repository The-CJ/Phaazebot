from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
	from main import Phaazebot

import ssl
from aiohttp import web
from Utils.cli import CliArgs
from Platforms.Web.index import WebIndex

class PhaazebotWeb(web.Application):
	def __init__(self, BASE:"Phaazebot"):
		super().__init__()
		self.BASE:"Phaazebot" = BASE
		self._client_max_size = self.BASE.Limit.web_client_max_size
		self.port:int = 9001
		self.SSLContext:Optional[ssl.SSLContext] = None
		self.Index:Optional[WebIndex] = None

	def __bool__(self):
		return self.BASE.IsReady.web

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

	def setupRouter(self) -> None:
		self.Index:WebIndex = WebIndex(self)
		self.Index.addRoutes()

	def start(self) -> None:
		self.setupRouter()
		self.setupSSL()
		self.BASE.Logger.info("Web server ready")

		def void(*_, **__) -> None: pass
		web.run_app(self, handle_signals=False, port=self.port, ssl_context=self.SSLContext, print=void)
