from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex

import json
from aiohttp.web import Response, Request
from Platforms.Web.utils import searchUser

async def apiAdminUsersGet(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
		Default url: /api/admin/users/get
	"""

	users:list = await searchUser(cls, where="1=1")

	return_list:list = list()

	for WebUser in users:
		return_list.append(WebUser.toJSON())

	return cls.response(
		text=json.dumps( dict(result=return_list, status=200) ),
		content_type="application/json",
		status=200
	)
