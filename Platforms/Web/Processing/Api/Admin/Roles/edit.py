from typing import TYPE_CHECKING, List
if TYPE_CHECKING:
	from Platforms.Web.main_web import PhaazebotWeb

import json
from aiohttp.web import Response
from Utils.Classes.extendedrequest import ExtendedRequest
from Utils.Classes.webrequestcontent import WebRequestContent
from Utils.Classes.storagetransformer import StorageTransformer
from Utils.Classes.undefined import UNDEFINED
from Utils.Classes.webrole import WebRole
from Platforms.Web.db import getWebRoles

async def apiAdminRolesEdit(cls:"PhaazebotWeb", WebRequest:ExtendedRequest) -> Response:
	Data:WebRequestContent = WebRequestContent(WebRequest)
	await Data.load()

	# get required stuff
	Edit:StorageTransformer = StorageTransformer()
	Edit["role_id"] = Data.getInt("role_id", 0, min_x=1)

	# checks
	if not Edit["role_id"]:
		return await cls.Tree.Api.errors.apiMissingData(cls, WebRequest, msg="missing or invalid 'role_id'")

	res:List[WebRole] = await getWebRoles(cls, role_id=Edit["role_id"])
	if not res:
		return await cls.Tree.Api.errors.apiWrongData(cls, WebRequest, msg=f"could not find role")

	CurrentRole:WebRole = res.pop(0)
	update:dict = dict()

	# name
	Edit["name"] = Data.getStr("name", UNDEFINED, len_max=64)
	if Edit["name"] != UNDEFINED:
		# only allow role name change as long the role is removable,
		# because based on name... a rename would be a delete... got it?
		if CurrentRole.can_be_removed:
			update["name"] = Edit["name"]

	# description
	Edit["description"] = Data.getStr("description", UNDEFINED, len_max=512, allow_none=True)
	if Edit["description"] != UNDEFINED:
		update["description"] = Edit["description"]

	# can_be_removed
	Edit["can_be_removed"] = Data.getBool("can_be_removed", UNDEFINED)
	if Edit["can_be_removed"] != UNDEFINED:
		# this value can only be set to 0
		# if the user gives a 1, meaning to make it removable... we just ignore it
		if not Edit["can_be_removed"]:
			update["can_be_removed"] = Edit["can_be_removed"]

	if not update:
		return await cls.Tree.Api.errors.apiMissingData(cls, WebRequest, msg="No changes, please add at least one")

	cls.BASE.Logger.debug(f"(API) Role update: R:{Edit['role_id']} {str(update)}", require="api:admin")
	cls.BASE.PhaazeDB.updateQuery(
		table="web_role",
		content=update,
		where="`web_role`.`id` = %s",
		where_values=(Edit["role_id"],)
	)

	return cls.response(
		text=json.dumps(dict(msg="role successful updated", changes=update, status=200)),
		content_type="application/json",
		status=200
	)
