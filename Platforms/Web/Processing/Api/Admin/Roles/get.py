from typing import TYPE_CHECKING, List
if TYPE_CHECKING:
	from Platforms.Web.main_web import PhaazebotWeb

import json
from aiohttp.web import Response, Request
from Utils.Classes.storagetransformer import StorageTransformer
from Utils.Classes.webrequestcontent import WebRequestContent
from Utils.Classes.webrole import WebRole
from Utils.Classes.undefined import UNDEFINED
from Platforms.Web.db import getWebRoles

DEFAULT_LIMIT:int = 50

async def apiAdminRolesGet(cls:"PhaazebotWeb", WebRequest:Request) -> Response:
	"""
	Default url: /api/admin/roles/get
	"""
	Data:WebRequestContent = WebRequestContent(WebRequest)
	await Data.load()

	Search:StorageTransformer = StorageTransformer()

	# get required stuff
	Search["role_id"] = Data.getInt("role_id", UNDEFINED, min_x=1)
	Search["name"] = Data.getStr("name", UNDEFINED)
	Search["name_contains"] = Data.getStr("name_contains", UNDEFINED)
	Search["can_be_removed"] = Data.getInt("can_be_removed", UNDEFINED)
	Search["limit"] = Data.getInt("limit", DEFAULT_LIMIT, min_x=1)
	Search["offset"] = Data.getInt("offset", 0, min_x=1)

	print(Search.getAllTransform())

	res_roles:List[WebRole] = await getWebRoles(cls, **Search.getAllTransform())

	result:dict = dict(
		result=[Role.toJSON() for Role in res_roles],
		limit=Search.getTransform("limit", DEFAULT_LIMIT),
		offset=Search.getTransform("offset", 0),
		total=await getWebRoles(cls, count_mode=True, **Search.getAllTransform()),
		status=200
	)

	return cls.response(
		text=json.dumps(result),
		content_type="application/json",
		status=200
	)
