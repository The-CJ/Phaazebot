from typing import TYPE_CHECKING, List
if TYPE_CHECKING:
	from Platforms.Web.main_web import PhaazebotWeb

import json
from aiohttp.web import Response
from Utils.Classes.extendedrequest import ExtendedRequest
from Utils.Classes.webrequestcontent import WebRequestContent
from Utils.Classes.undefined import UNDEFINED
from Utils.Classes.webrole import WebRole
from Platforms.Web.db import getWebRoles

async def apiAdminRolesDelete(cls:"PhaazebotWeb", WebRequest:ExtendedRequest) -> Response:
	Data:WebRequestContent = WebRequestContent(WebRequest)
	await Data.load()

	# get required stuff
	role_id:int = Data.getInt("role_id", UNDEFINED, min_x=1)

	# checks
	if role_id == UNDEFINED:
		return await cls.Tree.Api.errors.apiMissingData(cls, WebRequest, msg="missing or invalid 'role_id'")

	res:List[WebRole] = await getWebRoles(cls, role_id=role_id)

	if not res:
		return await cls.Tree.Api.errors.apiWrongData(cls, WebRequest, msg=f"could not find role")

	RoleToDelete:WebRole = res.pop(0)

	if not RoleToDelete.can_be_removed:
		return await cls.Tree.Api.errors.apiWrongData(cls, WebRequest, msg=f"'{RoleToDelete.name}' cannot be removed")

	cls.BASE.PhaazeDB.deleteQuery(
		"DELETE FROM `web_role` WHERE `web_role`.`id` = %s",
		(RoleToDelete.role_id,)
	)

	return cls.response(
		text=json.dumps(dict(msg="role successful deleted", role=RoleToDelete.name, status=200)),
		content_type="application/json",
		status=200
	)
