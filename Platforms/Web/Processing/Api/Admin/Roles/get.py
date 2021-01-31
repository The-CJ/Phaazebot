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

	# custom
	Search["for_user_id"] = Data.getInt("for_user_id", UNDEFINED, min_x=1)
	if Search["for_user_id"] != UNDEFINED:

		res:List[dict] = cls.BASE.PhaazeDB.selectQuery("""
			SELECT `user_has_role`.`role_id` AS `rid`
			FROM `user_has_role`
			WHERE `user_has_role`.`user_id` = %s""",
			(int(Search["for_user_id"]),)
		)

		rid_list:str = ','.join(str(x["rid"]) for x in res)
		if not rid_list: rid_list = "0"

		Search.storage.clear()
		Search["overwrite_where"] = f" AND `role`.`id` IN ({rid_list})"

	res_roles:List[WebRole] = await getWebRoles(cls, **Search.getAllTransform())

	result:dict = dict(
		result=[Role.toJSON() for Role in res_roles],
		limit=Search["limit"],
		offset=Search["offset"],
		total=await getWebRoles(cls, count_mode=True, **Search.getAllTransform()),
		status=200
	)

	return cls.response(
		text=json.dumps(result),
		content_type="application/json",
		status=200
	)
