from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex

import json
from aiohttp.web import Response, Request
from Utils.Classes.webrequestcontent import WebRequestContent
from Utils.dbutils import validateDBInput
from Platforms.Web.Processing.Api.errors import (
	apiMissingData,
	apiWrongData
)
async def apiAdminRolesCreate(cls:"WebIndex", WebRequest:Request) -> Response:
	Data:WebRequestContent = WebRequestContent(WebRequest)
	await Data.load()

	# get required stuff
	name:str = Data.getStr("name", "", len_max=64)
	description:str = Data.getStr("description", "", len_max=512)
	can_be_removed:bool = Data.getBool("can_be_removed", True)

	# checks
	if not name:
		return await apiMissingData(cls, WebRequest, msg="missing or invalid 'name'")

	res:list = cls.Web.BASE.PhaazeDB.selectQuery(
		"SELECT COUNT(*) AS `i` FROM `role` WHERE LOWER(`role`.`name`) = %s",
		(name,)
	)

	if res[0]['i'] != 0:
		return await apiWrongData(cls, WebRequest, msg=f"role '{name}' already exists")

	cls.Web.BASE.PhaazeDB.insertQuery(
		table = "role",
		content = dict(
			name = name,
			description = description,
			can_be_removed = validateDBInput(bool, can_be_removed)
		)
	)

	return cls.response(
		text=json.dumps( dict(msg="role successfull created", role=name, status=200) ),
		content_type="application/json",
		status=200
	)
