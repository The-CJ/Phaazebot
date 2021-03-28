from typing import TYPE_CHECKING, Any, Optional
if TYPE_CHECKING:
	from Platforms.Web.main_web import PhaazebotWeb

import json
import traceback
from aiohttp.web import Response
from Utils.Classes.authwebuser import AuthWebUser
from Utils.Classes.extendedrequest import ExtendedRequest
from Utils.Classes.webrequestcontent import WebRequestContent
from Utils.Classes.storeclasses import GlobalStorage
from Platforms.Web.index import PhaazeWebIndex
from Platforms.Web.utils import authWebUser

@PhaazeWebIndex.view("/api/admin/evaluate")
async def apiAdminEvaluate(cls:"PhaazebotWeb", WebRequest:ExtendedRequest) -> Response:
	"""
	Default url: /api/admin/evaluate
	"""
	WebAuth:AuthWebUser = await authWebUser(cls, WebRequest)
	if not WebAuth.found:
		return await cls.Tree.Api.errors.apiMissingAuthorisation(WebRequest)
	if not WebAuth.User.checkRoles(["superadmin"]):
		return await cls.Tree.Api.errors.apiNotAllowed(WebRequest, msg="Superadmin rights required")

	Data:WebRequestContent = WebRequestContent(WebRequest)
	await Data.load()

	# get required stuff
	command:str = Data.getStr("command", "")
	coroutine:bool = Data.getBool("coroutine", False)

	# this is for easier access
	locals()["BASE"] = cls.BASE
	locals()["SUPERBASE"] = GlobalStorage

	# return values
	success:bool = False
	result:Optional[str] = None
	trace:Optional[str] = None

	try:
		res:Any = eval(command)
		if coroutine: res = await res

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
