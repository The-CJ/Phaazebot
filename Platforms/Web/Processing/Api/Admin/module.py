from typing import TYPE_CHECKING, Dict, Any
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex

import json
from aiohttp.web import Response, Request
from Utils.Classes.webrequestcontent import WebRequestContent
from Utils.Classes.authwebuser import AuthWebUser
from Utils.Classes.undefined import UNDEFINED
from Utils.management import shutdownModule
from Platforms.Web.Processing.Api.errors import apiNotAllowed, apiMissingValidMethod, apiWrongData

async def apiAdminModule(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
	Default url: /api/admin/module
	"""

	WebUser:AuthWebUser = await cls.getWebUserInfo(WebRequest)
	if not WebUser.checkRoles(["admin", "superadmin"]): return await apiNotAllowed(cls, WebRequest, msg="Admin rights required")

	Data:WebRequestContent = WebRequestContent(WebRequest)
	await Data.load()

	# get required stuff
	module:str = Data.getStr("module", "x")
	state:bool = Data.getBool("state", UNDEFINED)

	if state == UNDEFINED:
		return await apiWrongData(cls, WebRequest, msg="missing boolish field 'state'")

	if not hasattr(cls.Web.BASE.Active, module):
		return await apiMissingValidMethod(cls, apiWrongData, msg=f"module '{module}' not avariable")

	setattr(cls.Web.BASE.Active, module, state)
	cls.Web.BASE.Logger.warning(f"Module change state: '{module}' now '{state}'")

	# handle state 'False', which means shutdown the module
	if not state:
		shutdownModule(cls.Web.BASE, module)

	response:Dict[str, Any] = dict(
		msg = f"state for module: '{module}' is now: {str(state)}",
		changed_module = module,
		new_state = state,
		status = 200
	)

	return cls.response(
		body=json.dumps( response ),
		status=200,
		content_type='application/json'
	)
