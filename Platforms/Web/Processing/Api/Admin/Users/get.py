from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex

import json
from Platforms.Web.Processing.Api.errors import apiNotAllowed, apiMissingAuthorisation
from aiohttp.web import Response, Request
from Utils.Classes.webuserinfo import WebUserInfo
from Platforms.Web.utils import searchUser

async def apiAdminUsersGet(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
		Default url: /api/admin/users/get
	"""

	users:list = await searchUser(cls, where="1=1")

	return_list:list = list()

	for WebUser in users:
		WebUser:WebUserInfo = WebUser

		user:dict = dict(
			username=str( WebUser.username ),
			email=str( WebUser.email ),
			verified=bool( WebUser.verified ),
			roles=list( WebUser.roles ),
			user_id=int( WebUser.user_id ),
			last_login=str( WebUser.last_login ),
			# make a WebUser.toJSON() or so.
		)

		return_list.append(user)

	return cls.response(
		text=json.dumps( dict(result=return_list, status=200) ),
		content_type="application/json",
		status=200
	)
