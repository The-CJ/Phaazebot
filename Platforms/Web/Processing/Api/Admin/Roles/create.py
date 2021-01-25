from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.main_web import PhaazebotWeb

import json
from aiohttp.web import Response
from Utils.Classes.undefined import UNDEFINED
from Utils.Classes.extendedrequest import ExtendedRequest
from Utils.Classes.webrequestcontent import WebRequestContent
from Utils.Classes.storagetransformer import StorageTransformer

async def apiAdminRolesCreate(cls:"PhaazebotWeb", WebRequest:ExtendedRequest) -> Response:
	Data:WebRequestContent = WebRequestContent(WebRequest)
	await Data.load()

	# get required stuff
	Create:StorageTransformer = StorageTransformer()
	Create.set("name", Data.getStr("name", UNDEFINED, len_max=64), wanted_type=str)
	Create.set("description", Data.getStr("description", UNDEFINED, len_max=512), wanted_type=str)
	Create.set("can_be_removed", Data.getBool("name", UNDEFINED), wanted_type=bool)

	# checks
	name:str = Create.getTransform("name", UNDEFINED)
	if name == UNDEFINED:
		return await cls.Tree.Api.errors.apiMissingData(cls, WebRequest, msg="missing or invalid 'name'")

	res:list = cls.BASE.PhaazeDB.selectQuery(
		"SELECT COUNT(*) AS `i` FROM `role` WHERE LOWER(`role`.`name`) = %s",
		(Create.getTransform("name", UNDEFINED),)
	)

	if res[0]['i'] != 0:
		return await cls.Tree.Api.errors.apiWrongData(cls, WebRequest, msg=f"role '{name}' already exists")

	cls.BASE.PhaazeDB.insertQuery(
		table="role",
		content=Create.getAllTransform()
	)

	return cls.response(
		text=json.dumps(dict(msg="role successful created", role=name, status=200)),
		content_type="application/json",
		status=200
	)
