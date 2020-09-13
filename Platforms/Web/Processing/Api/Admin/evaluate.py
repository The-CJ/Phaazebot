from typing import TYPE_CHECKING, Any
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex

import json
import traceback
from aiohttp.web import Response, Request
from Utils.Classes.webrequestcontent import WebRequestContent
from Utils.Classes.webuserinfo import WebUserInfo
from Utils.Classes.storeclasses import GlobalStorage
from Platforms.Web.Processing.Api.errors import apiNotAllowed

async def apiAdminEvaluate(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
	Default url: /api/admin/evaluate
	"""
	WebUser:WebUserInfo = await cls.getWebUserInfo(WebRequest)
	if not WebUser.checkRoles(["superadmin"]): return await apiNotAllowed(cls, WebRequest, msg="Superadmin rights required")

	Data:WebRequestContent = WebRequestContent(WebRequest)
	await Data.load()

	# get required stuff
	command:str = Data.getStr("command", "")
	corotine:bool = Data.getBool("corotine", False)

	# this is for easyer access
	locals()["BASE"] = cls.Web.BASE
	locals()["SUPERBASE"] = GlobalStorage

	# return values
	success:bool = False
	result:str = None
	trace:str = None

	try:
		res:Any = eval(command)
		if corotine: res = await res

		result = str(res)
		trace = None
		success = True

	except Exception as Fail:
		result = str(Fail)
		trace = traceback.format_exc()
		success = False

	return cls.response(
		body=json.dumps(dict(result=result, traceback=trace, success=success, status="200")),
		status=200,
		content_type='application/json'
	)
