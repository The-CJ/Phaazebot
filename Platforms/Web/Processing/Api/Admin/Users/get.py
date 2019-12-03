from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex

import json
from aiohttp.web import Response, Request
from Platforms.Web.Processing.Api.errors import userNotFound
from Utils.Classes.webrequestcontent import WebRequestContent
from Platforms.Web.utils import searchUser

async def apiAdminUsersGet(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
		Default url: /api/admin/users/get
	"""
	Data:WebRequestContent = WebRequestContent(WebRequest)
	await Data.load()

	user_id:str = Data.getStr("user_id", "", must_be_digit=True)
	where:str = f"`user`.`id` = {user_id}" if user_id else "1=1"

	users:list = await searchUser(cls, where=where)

	if not users:
		return await userNotFound(cls, WebRequest, msg=f"no user found with id: '{user_id}'")

	return_list:list = list()
	for WebUser in users:
		return_list.append(WebUser.toJSON())

	return cls.response(
		text=json.dumps( dict(result=return_list, status=200) ),
		content_type="application/json",
		status=200
	)
