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
	Create["name"] = Data.getStr("name", UNDEFINED, len_max=64)
	Create["description"] = Data.getStr("description", UNDEFINED, len_max=512)
	Create["can_be_removed"] = Data.getBool("name", UNDEFINED)

	# checks
	if Create["name"] == UNDEFINED:
		return await cls.Tree.Api.errors.apiMissingData(cls, WebRequest, msg="missing or invalid 'name'")

	res:list = cls.BASE.PhaazeDB.selectQuery(
		"SELECT COUNT(*) AS `i` FROM `web_role` WHERE LOWER(`web_role`.`name`) = %s",
		(Create["name"],)
	)

	if res[0]['i'] != 0:
		return await cls.Tree.Api.errors.apiWrongData(cls, WebRequest, msg=f"role '{Create['name']}' already exists")

	cls.BASE.PhaazeDB.insertQuery(
		table="role",
		content=Create.getAllTransform()
	)

	return cls.response(
		text=json.dumps(dict(msg="role successful created", role=Create["name"], status=200)),
		content_type="application/json",
		status=200
	)
