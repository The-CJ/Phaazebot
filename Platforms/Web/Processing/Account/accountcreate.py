from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.main_web import PhaazebotWeb

from aiohttp.web import Response
from Utils.Classes.htmlformatter import HTMLFormatter
from Utils.Classes.extendedrequest import ExtendedRequest
from Utils.Classes.authwebuser import AuthWebUser
from Platforms.Web.index import PhaazeWebIndex
from Platforms.Web.utils import getNavbar, authWebUser
from Platforms.Web.Processing.Account.accountlogin import accountLogin

@PhaazeWebIndex.get("/account/create")
async def accountCreate(cls:"PhaazebotWeb", WebRequest:ExtendedRequest) -> Response:
	"""
	Default url: /account/create
	"""
	# already logged in
	WebUser:AuthWebUser = await authWebUser(cls, WebRequest)
	if WebUser.found: return await accountLogin(cls, WebRequest)

	CreatePage:HTMLFormatter = HTMLFormatter("Platforms/Web/Content/Html/Account/create.html")

	site:str = cls.HTMLRoot.replace(
		replace_empty=True,

		title="Phaaze | Account - Create",
		header=getNavbar(),
		main=CreatePage
	)

	return cls.response(
		body=site,
		status=200,
		content_type='text/html'
	)
