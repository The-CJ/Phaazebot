from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex

import json
from aiohttp.web import Response, Request
from Utils.Classes.webrequestcontent import WebRequestContent
from Utils.Classes.webrole import WebRole
from Utils.Classes.undefined import UNDEFINED
from Utils.dbutils import validateDBInput
from Platforms.Web.Processing.Api.errors import (
	apiMissingData,
	apiWrongData
)
async def apiAdminRolesEdit(cls:"WebIndex", WebRequest:Request) -> Response:
	Data:WebRequestContent = WebRequestContent(WebRequest)
	await Data.load()

	# get required stuff
	role_id:int = Data.getInt("role_id", UNDEFINED, min_x=1)

	# checks
	if not role_id:
		return await apiMissingData(cls, WebRequest, msg="missing or invalid 'role_id'")

	res:list = cls.Web.BASE.PhaazeDB.selectQuery(
		"SELECT * FROM `role` WHERE `role`.`id` = %s",
		(role_id,)
	)

	if not res:
		return await apiWrongData(cls, WebRequest, msg=f"could not find role")

	CurrentRole:WebRole = WebRole( res.pop(0) )

	db_changes:dict = dict()
	changes:dict = dict()

	# name
	value:str = Data.getStr("name", UNDEFINED, len_max=64)
	if value != UNDEFINED:
		# only allow role name change as long the role is removable,
		# because based on name... a rename whould be a delete... got it?
		if CurrentRole.can_be_removed:
			db_changes["name"] = validateDBInput(str, value)
			changes["name"] = value

	# description
	value:str = Data.getStr("description", UNDEFINED, len_max=512)
	if value != UNDEFINED:
		db_changes["description"] = validateDBInput(str, value)
		changes["description"] = value

	# can_be_removed
	value:bool = Data.getBool("can_be_removed", UNDEFINED)
	if value != UNDEFINED:
		# this value can only be set to 0
		# if the user gives a 1, meaning to make it removeable... we just ignore it
		if not value:
			db_changes["can_be_removed"] = validateDBInput(bool, value)
			changes["can_be_removed"] = value

	if not db_changes:
		return await apiMissingData(cls, WebRequest, msg="No changes, please add at least one")

	cls.Web.BASE.Logger.debug(f"(API) Role update: R:{role_id} {str(db_changes)}", require="api:admin")
	cls.Web.BASE.PhaazeDB.updateQuery(
		table = "role",
		content = db_changes,
		where = "role.id = %s",
		where_values = (role_id,)
	)

	return cls.response(
		text=json.dumps( dict(msg="role successfull updated", changes=changes, status=200) ),
		content_type="application/json",
		status=200
	)
