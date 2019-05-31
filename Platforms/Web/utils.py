from typing import TYPE_CHECKING, Any
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex

from aiohttp.web import Request
from Utils.Classes.htmlformatter import HTMLFormatter
from Utils.Classes.webuserinfo import WebUserInfo

def getNavbar(active:str="", UserInfo:WebUserInfo=None) -> HTMLFormatter:
	Navbar:HTMLFormatter = HTMLFormatter("Platforms/Web/Content/Html/Navbar/default.html")

	Navbar.replace(login_button=getLoginButton(UserInfo=UserInfo))

	Navbar.setRegex(r"\{selected_(.+?)\}")
	Navbar.replace(replace_empty=True, **{active:"active"})

	return Navbar

def getLoginButton(UserInfo:WebUserInfo=None) -> HTMLFormatter:
	Button:HTMLFormatter = HTMLFormatter("Platforms/Web/Content/Html/Button/account.html")

	return Button

async def getUserInfo(self:"WebIndex", WebRequest:Request, **kwargs:Any) -> WebUserInfo:
	if hasattr(WebRequest, "UserInfo"):
		self.Web.BASE.Logger.debug(f"(Web) Used stored infos: {str(WebRequest.UserInfo)}", require="web:debug")
		return WebRequest.UserInfo

	UserInfo:WebUserInfo = WebUserInfo(self.Web.BASE, WebRequest, **kwargs)
	await UserInfo.auth()
	WebRequest.UserInfo = UserInfo

	return WebRequest.UserInfo
