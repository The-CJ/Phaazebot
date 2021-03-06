from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.main_web import PhaazebotWeb

from aiohttp.web import Response
from Utils.Classes.htmlformatter import HTMLFormatter
from Utils.Classes.extendedrequest import ExtendedRequest
from Utils.Classes.authwebuser import AuthWebUser
from Platforms.Web.index import PhaazeWebIndex
from Platforms.Web.utils import getNavbar, authWebUser

@PhaazeWebIndex.get("/account")
async def accountMain(cls:"PhaazebotWeb", WebRequest:ExtendedRequest) -> Response:
	"""
	Default url: /account
	"""
	WebUser:AuthWebUser = await authWebUser(cls, WebRequest)
	if not WebUser.found: return await cls.Tree.Account.accountlogin.accountLogin(cls, WebRequest)

	AccountPage:HTMLFormatter = HTMLFormatter("Platforms/Web/Content/Html/Account/main.html")

	site:str = cls.HTMLRoot.replace(
		replace_empty=True,

		title="Phaaze | Account",
		header=getNavbar(),
		main=AccountPage
	)

	return cls.response(
		body=site,
		status=200,
		content_type='text/html'
	)
