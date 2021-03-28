from typing import Optional, TYPE_CHECKING
if TYPE_CHECKING:
	from Utils.Classes.authwebuser import AuthWebUser
	from Utils.Classes.authtwitchwebuser import AuthTwitchWebUser
	from Utils.Classes.authdiscordwebuser import AuthDiscordWebUser

from aiohttp.web import Request

class ExtendedRequest(Request):
	"""
	Pretty much the same as a normal aiohttp request
	but it has extra fields on it.
	It's just for IDE purposes and keeping track of added values.
	"""
	def __init__(self, *x, **xx):
		super().__init__(*x, **xx)
		self.AuthWeb:Optional[AuthWebUser] = None
		self.AuthDiscord:Optional[AuthDiscordWebUser] = None
		self.AuthTwitch:Optional[AuthTwitchWebUser] = None
