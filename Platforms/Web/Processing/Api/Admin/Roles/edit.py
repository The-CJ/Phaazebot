from typing import TYPE_CHECKING, List
if TYPE_CHECKING:
	from Platforms.Web.main_web import PhaazebotWeb

import json
from aiohttp.web import Response
from Utils.Classes.extendedrequest import ExtendedRequest
from Utils.Classes.webrequestcontent import WebRequestContent
from Utils.Classes.webrole import WebRole
from Utils.Classes.undefined import UNDEFINED
from Platforms.Web.db import getWebRoles

async def apiAdminRolesEdit(cls:"PhaazebotWeb", WebRequest:ExtendedRequest) -> Response:
	Data:WebRequestContent = WebRequestContent(WebRequest)
	await Data.load()

	# get required stuff
	role_id:int = Data.getInt("role_id", 0, min_x=1)

	# checks
	if not role_id:
		return await cls.Tree.Api.errors.apiMissingData(cls, WebRequest, msg="missing or invalid 'role_id'")

	res:List[WebRole] = await getWebRoles(cls, role_id=role_id)
	if not res:
		return await cls.Tree.Api.errors.apiWrongData(cls, WebRequest, msg=f"could not find role")

	CurrentRole:WebRole = res.pop(0)
	update:dict = dict()

	# name
	value:str = Data.getStr("name", UNDEFINED, len_max=64)
	if value != UNDEFINED:
		# only allow role name change as long the role is removable,
		# because based on name... a rename would be a delete... got it?
		if CurrentRole.can_be_removed:
			update["name"] = value

	# description
	value:str = Data.getStr("description", UNDEFINED, len_max=512)
	if value != UNDEFINED:
		update["description"] = value

	# can_be_removed
	value:bool = Data.getBool("can_be_removed", UNDEFINED)
	if value != UNDEFINED:
		# this value can only be set to 0
		# if the user gives a 1, meaning to make it removable... we just ignore it
		if not value:
			update["can_be_removed"] = value

	if not update:
		return await cls.Tree.Api.errors.apiMissingData(cls, WebRequest, msg="No changes, please add at least one")

	cls.BASE.Logger.debug(f"(API) Role update: R:{role_id} {str(update)}", require="api:admin")
	cls.BASE.PhaazeDB.updateQuery(
		table="role",
		content=update,
		where="`role`.`id` = %s",
		where_values=(role_id,)
	)

	return cls.response(
		text=json.dumps(dict(msg="role successful updated", changes=update, status=200)),
		content_type="application/json",
		status=200
	)
