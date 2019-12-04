from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex

import json
from aiohttp.web import Response, Request
from Platforms.Web.Processing.Api.errors import userNotFound
from Utils.Classes.webrequestcontent import WebRequestContent
from Platforms.Web.utils import getWebUsers, getWebUserAmount

DEFAULT_LIMIT:int = 50

async def apiAdminUsersGet(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
		Default url: /api/admin/users/get
	"""
	Data:WebRequestContent = WebRequestContent(WebRequest)
	await Data.load()

	user_id:str = Data.getStr("user_id", "", must_be_digit=True)
	username:str = Data.getStr("username", "")
	email:str = Data.getStr("email", "")

	offset:int = Data.getInt("offset", 0, min_x=0)
	limit:int = Data.getInt("limit", DEFAULT_LIMIT, min_x=1)

	where:str = "1=1"
	values:tuple = ()

	if user_id:
		where = "`user`.`id` = %s"
		values = (user_id,)

	elif email or username:
		where = "`user`.`username` LIKE %s OR `user`.`email` LIKE %s"
		values = (username, email)

	users:list = await getWebUsers(cls, where=where, values=values, limit=limit, offset=offset)

	if not users:
		return await userNotFound(cls, WebRequest, msg=f"no user found")

	result:dict = dict(
		result=[ WebUser.toJSON() for WebUser in users ],
		limit=limit,
		offset=offset,
		total = await getWebUserAmount(cls, where=where, values=values),
		status=200
	)

	return cls.response(
		text=json.dumps( result ),
		content_type="application/json",
		status=200
	)
