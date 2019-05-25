from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from main import Phaazebot

import ssl
from aiohttp import web
from Utils.cli import CliArgs
from .index import WebIndex

class PhaazebotWeb(web.Application):
	def __init__(self, BASE:"Phaazebot"):
		super().__init__()
		self.BASE:"Phaazebot" = BASE
		self._client_max_size = self.BASE.Limit.WEB_CLIENT_MAX_SIZE
		self.port:int = 9001
		self.SSLContext:ssl.SSLContext = None
		self.Index:WebIndex = None

	def setupSSL(self) -> None:
		if CliArgs.get("http", "test") == "live":
			self.port:int = 443
			self.SSLContext:ssl.SSLContext = ssl.SSLContext()
			self.SSLContext.load_cert_chain('/etc/letsencrypt/live/phaaze.net/fullchain.pem', keyfile='/etc/letsencrypt/live/phaaze.net/privkey.pem')
			self.BASE.Logger.info(f"Configured webserver Port={self.port} (live)")

		elif CliArgs.get("http", "test") == "unsecure":
			self.port:int = 80
			self.BASE.Logger.info(f"Configured webserver Port={self.port} (unsecure)")

		elif CliArgs.get("http", "test") == "error_ssl":
			self.port:int = 443
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

		web.run_app(self, handle_signals=False, port=self.port, ssl_context=self.SSLContext, print=False)