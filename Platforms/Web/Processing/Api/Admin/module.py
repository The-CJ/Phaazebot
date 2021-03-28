from typing import TYPE_CHECKING, Dict, Any
if TYPE_CHECKING:
	from Platforms.Web.main_web import PhaazebotWeb

import json
from aiohttp.web import Response
from Utils.Classes.authwebuser import AuthWebUser
from Utils.Classes.extendedrequest import ExtendedRequest
from Utils.Classes.webrequestcontent import WebRequestContent
from Utils.Classes.undefined import UNDEFINED
from Utils.management import shutdownModule
from Platforms.Web.index import PhaazeWebIndex
from Platforms.Web.utils import authWebUser

@PhaazeWebIndex.view("/api/admin/module")
async def apiAdminModule(cls:"PhaazebotWeb", WebRequest:ExtendedRequest) -> Response:
	"""
	Default url: /api/admin/module
	"""
	WebAuth:AuthWebUser = await authWebUser(cls, WebRequest)
	if not WebAuth.found:
		return await cls.Tree.Api.errors.apiMissingAuthorisation(WebRequest)
	if not WebAuth.User.checkRoles(["admin", "superadmin"]):
		return await cls.Tree.Api.errors.apiNotAllowed(WebRequest, msg="Admin rights required")

	Data:WebRequestContent = WebRequestContent(WebRequest)
	await Data.load()

	# get required stuff
	module:str = Data.getStr("module", "x")
	state:bool = Data.getBool("state", UNDEFINED)

	if state == UNDEFINED:
		return await cls.Tree.Api.errors.apiWrongData(cls, WebRequest, msg="missing boolish field 'state'")

	if not hasattr(cls.BASE.Active, module):
		return await cls.Tree.Api.errors.apiMissingValidMethod(cls, WebRequest, msg=f"module '{module}' not available")

	setattr(cls.BASE.Active, module, state)
	cls.BASE.Logger.warning(f"Module change state: '{module}' now '{state}'")

	# handle state 'False', which means shutdown the module
	if not state:
		shutdownModule(cls.BASE, module)

	response:Dict[str, Any] = dict(
		msg=f"state for module: '{module}' is now: {str(state)}",
		changed_module=module,
		new_state=state,
		status=200
	)

	return cls.response(
		body=json.dumps(response),
		status=200,
		content_type='application/json'
	)
