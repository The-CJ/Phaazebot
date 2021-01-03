from typing import Optional
from aiohttp.web import Request

class ExtendedRequest(Request):
	"""
	Pretty much the same as a normal aiohttp request
	but it has extra fields on it.
	It's just for IDE purposes and keeping track of added values.
	"""
	def __init__(self, *x, **xx):
		super().__init__(*x, **xx)
		self.WebUser:Optional = None
		self.DiscordUser:Optional = None
		self.TwitchUser:Optional = None
