from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex

import json
from aiohttp.web import Response, Request
from Utils.Classes.webrequestcontent import WebRequestContent
from Utils.Classes.undefined import UNDEFINED
from Utils.Classes.webrole import WebRole
from Platforms.Web.Processing.Api.errors import (
	apiMissingData,
	apiWrongData
)
async def apiAdminRolesDelete(cls:"WebIndex", WebRequest:Request) -> Response:
	Data:WebRequestContent = WebRequestContent(WebRequest)
	await Data.load()

	# get required stuff
	role_id:int = Data.getInt("role_id", UNDEFINED, min_x=1)

	# checks
	if not role_id:
		return await apiMissingData(cls, WebRequest, msg="missing or invalid 'role_id'")

	res:list = cls.Web.BASE.PhaazeDB.selectQuery(
		"SELECT `name`, `can_be_removed` FROM `role` WHERE `role`.`id` = %s",
		(role_id,)
	)

	if not res:
		return await apiWrongData(cls, WebRequest, msg=f"could not find role")

	role:WebRole = WebRole( res.pop(0) )

	if not role["can_be_removed"]:
		return await apiWrongData(cls, WebRequest, msg=f"'{role['name']}' cannot be removed")

	cls.Web.BASE.PhaazeDB.deleteQuery(
		"DELETE FROM `role` WHERE `role`.`id` = %s",
		(role_id,)
	)

	return cls.response(
		text=json.dumps( dict(msg="role successfull deleted", role=role['name'], status=200) ),
		content_type="application/json",
		status=200
	)
