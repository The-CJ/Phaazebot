from typing import TYPE_CHECKING, List
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex

import json
from aiohttp.web import Response, Request
from Utils.Classes.webrequestcontent import WebRequestContent
from Platforms.Web.db import getWebRoles, getWebRoleAmount
from Utils.Classes.webrole import WebRole
from Utils.Classes.undefined import UNDEFINED

DEFAULT_LIMIT:int = 50

async def apiAdminRolesGet(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
		Default url: /api/admin/roles/get
	"""
	Data:WebRequestContent = WebRequestContent(WebRequest)
	await Data.load()

	# get required stuff
	role_id:int = Data.getInt("role_id", UNDEFINED, min_x=1)
	user_id:int = Data.getInt("user_id", UNDEFINED, min_x=1)
	name:str = Data.getStr("name", None)
	name_contains:str = Data.getStr("name_contains", None)
	can_be_removed:int = Data.getInt("can_be_removed", 0)
	limit:int = Data.getInt("limit", DEFAULT_LIMIT, min_x=1)
	offset:int = Data.getInt("offset", 0, min_x=1)

	res_roles:List[WebRole] = await getWebRoles(cls,
		role_id=role_id, user_id=user_id, can_be_removed=can_be_removed,
		name=name, name_contains=name_contains,
		limit=limit, offset=offset
	)

	result:dict = dict(
		result=[ Role.toJSON() for Role in res_roles ],
		limit=limit,
		offset=offset,
		total=await getWebRoleAmount(cls),
		status=200
	)

	return cls.response(
		text=json.dumps( result ),
		content_type="application/json",
		status=200
	)
