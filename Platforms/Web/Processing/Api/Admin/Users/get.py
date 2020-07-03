from typing import TYPE_CHECKING, List, Dict, Any
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex

import json
from aiohttp.web import Response, Request
from Utils.Classes.webrequestcontent import WebRequestContent
from Utils.Classes.webuserinfo import WebUserInfo
from Platforms.Web.db import getWebUsers, getWebUserAmount
from Platforms.Web.Processing.Api.errors import apiUserNotFound

DEFAULT_LIMIT:int = 50

async def apiAdminUsersGet(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
		Default url: /api/admin/users/get
	"""
	Data:WebRequestContent = WebRequestContent(WebRequest)
	await Data.load()

	# get required stuff
	user_id:str = Data.getStr("user_id", "", must_be_digit=True)
	username:str = Data.getStr("username", "", len_max=64)
	username_contains:str = Data.getStr("username_contains", "", len_max=64)
	email:str = Data.getStr("email", "", len_max=128)
	email_contains:str = Data.getStr("email_contains", "", len_max=128)
	limit:int = Data.getInt("limit", DEFAULT_LIMIT, min_x=1)
	offset:int = Data.getInt("offset", 0, min_x=0)

	# get user
	res_users:List[WebUserInfo] = await getWebUsers(cls, user_id=user_id,
		username=username, username_contains=username_contains,
		email=email, email_contains=email_contains,
		limit=limit, offset=offset
	)

	if not res_users:
		return await apiUserNotFound(cls, WebRequest)

	result:Dict[str, Any] = dict(
		result=[ WebUser.toJSON() for WebUser in res_users ],
		limit=limit,
		offset=offset,
		total=(await getWebUserAmount(cls)),
		status=200
	)

	return cls.response(
		text=json.dumps( result ),
		content_type="application/json",
		status=200
	)
