from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex

import json
from aiohttp.web import Response, Request
from Utils.Classes.webrequestcontent import WebRequestContent
from Utils.Classes.webuserinfo import WebUserInfo
from Utils.management import shutdownModule
from Platforms.Web.Processing.Api.errors import apiNotAllowed, apiMissingValidMethod

async def apiAdminModule(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
		Default url: /api/admin/module
	"""

	WebUser:WebUserInfo = await cls.getWebUserInfo(WebRequest)
	if not WebUser.checkRoles(["admin", "superadmin"]): return await apiNotAllowed(cls, WebRequest, msg="Admin rights required")

	Data:WebRequestContent = WebRequestContent(WebRequest)
	await Data.load()

	# get required stuff
	module:str = Data.getStr("module", "x")
	state:bool = Data.getBool("state", False)

	if not hasattr(cls.Web.BASE.Active, module):
		return await apiMissingValidMethod(cls, WebRequest, msg=f"module '{module}' not avariable")

	setattr(cls.Web.BASE.Active, module, state)
	cls.Web.BASE.Logger.warning(f"Module change state: '{module}' now '{state}'")

	# handle state 'False', which means shutdown the module
	if not state:
		shutdownModule(cls.Web.BASE, module)

	return cls.response(
		body=json.dumps(dict(msg=f"state for module: '{module}' is now: {str(state)}", status=200)),
		status=200,
		content_type='application/json'
	)
