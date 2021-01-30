from typing import TYPE_CHECKING, List, Dict, Any
if TYPE_CHECKING:
	from Platforms.Web.main_web import PhaazebotWeb

import json
from aiohttp.web import Response
from Utils.Classes.storagetransformer import StorageTransformer
from Utils.Classes.webrequestcontent import WebRequestContent
from Utils.Classes.extendedrequest import ExtendedRequest
from Utils.Classes.webuser import WebUser
from Utils.Classes.undefined import UNDEFINED
from Platforms.Web.db import getWebUsers

DEFAULT_LIMIT:int = 50

async def apiAdminUsersGet(cls:"PhaazebotWeb", WebRequest:ExtendedRequest) -> Response:
	"""
	Default url: /api/admin/users/get
	"""
	Data:WebRequestContent = WebRequestContent(WebRequest)
	await Data.load()

	Search:StorageTransformer = StorageTransformer()

	# get required stuff
	Search["user_id"] = Data.getInt("user_id", UNDEFINED, min_x=1)
	Search["username"] = Data.getStr("username", UNDEFINED, len_max=64)
	Search["username_contains"] = Data.getStr("username_contains", UNDEFINED, len_max=64)
	Search["email"] = Data.getStr("email", UNDEFINED, len_max=128)
	Search["email_contains"] = Data.getStr("email_contains", UNDEFINED, len_max=128)
	Search["limit"] = Data.getInt("limit", DEFAULT_LIMIT, min_x=1)
	Search["offset"] = Data.getInt("offset", 0, min_x=1)

	# get user
	res_users:List[WebUser] = await getWebUsers(cls, **Search.getAllTransform())

	result:Dict[str, Any] = dict(
		result=[Us.toJSON() for Us in res_users],
		limit=Search.getTransform("limit", DEFAULT_LIMIT),
		offset=Search.getTransform("offset", 0),
		total=await getWebUsers(cls, count_mode=True, **Search.getAllTransform()),
		status=200
	)

	return cls.response(
		text=json.dumps(result),
		content_type="application/json",
		status=200
	)
