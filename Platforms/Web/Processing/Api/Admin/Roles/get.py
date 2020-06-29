from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex

import json
from aiohttp.web import Response, Request
from Utils.Classes.webrequestcontent import WebRequestContent
from Utils.Classes.webrole import WebRole
from Utils.Classes.undefined import UNDEFINED

async def apiAdminRolesGet(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
		Default url: /api/admin/roles/get
	"""
	Data:WebRequestContent = WebRequestContent(WebRequest)
	await Data.load()

	# get required stuff
	role_id:int = Data.getInt("role_id", UNDEFINED, min_x=1)
	user_id:int = Data.getInt("user_id", UNDEFINED, min_x=1)

	sql:str = """SELECT * FROM `role` WHERE 1=1"""
	values:tuple = ()

	# only show roles of a specific user
	# join with user_has_role to only get roles a given user (user_id) has [if provided]
	if user_id:
		sql = """
			SELECT `role`.*
			FROM `user_has_role`
			LEFT JOIN `role` ON `role`.`id` = `user_has_role`.`role_id`
			WHERE `user_has_role`.`user_id` = %s"""
		values += (user_id,)

	# only show one?
	if role_id:
		sql += " AND `role`.`id` = %s"
		values += (role_id,)

	res:list = cls.Web.BASE.PhaazeDB.selectQuery(sql, values)
	res = [WebRole(r) for r in res]

	return_list:list = list()

	for Role in res:
		return_list.append( Role.toJSON() )

	return cls.response(
		text=json.dumps( dict(result=return_list, status=200) ),
		content_type="application/json",
		status=200
	)
