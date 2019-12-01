from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex

import json
from aiohttp.web import Response, Request
from Utils.Classes.webrequestcontent import WebRequestContent
from Platforms.Web.Processing.Api.errors import missingData, apiWrongData
from Utils.Classes.undefined import UNDEFINED
from Utils.dbutils import validateDBInput

async def apiAdminUsersEdit(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
		Default url: /api/admin/users/edit
	"""
	Data:WebRequestContent = WebRequestContent(WebRequest)
	await Data.load()

	user_id:str = Data.getStr("user_id", "", must_be_digit=True)
	if not user_id:
		return await missingData(cls, WebRequest, msg="missing or invalid 'user_id'")

	# single actions
	# TODO: s

	changes:dict = dict()
	db_changes:dict = dict()

	# username
	value:str = Data.getStr("username", UNDEFINED)
	if value != UNDEFINED:
		db_changes["username"] = validateDBInput(str, value)
		changes["username"] = value

	# email
	value:str = Data.getStr("email", UNDEFINED)
	if value != UNDEFINED:
		db_changes["email"] = validateDBInput(str, value)
		changes["email"] = value

	# verified
	value:bool = Data.getBool("verified", UNDEFINED)
	if value != UNDEFINED:
		db_changes["verified"] = validateDBInput(bool, value)
		changes["verified"] = value

	if not db_changes:
		return await missingData(cls, WebRequest, msg="No changes, please add at least one")

	cls.Web.BASE.Logger.debug(f"(API) Config User U:{user_id} {str(db_changes)}", require="api:user")
	hits:int = cls.Web.BASE.PhaazeDB.updateQuery(
		table = "user",
		content = db_changes,
		where = "user.id = %s",
		where_values = (user_id,)
	)

	if not hits:
		return await apiWrongData(cls, WebRequest, msg="no users updated, 'user_id' not found")

	return cls.response(
		text=json.dumps( dict(msg="user successfull updated", changes=changes, status=200) ),
		content_type="application/json",
		status=200
	)
