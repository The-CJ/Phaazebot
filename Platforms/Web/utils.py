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
	field_replace:str = "loggedin" if UserInfo else ""
	Button.replace(is_logged_in=field_replace)

	return Button

async def getUserInfo(self:"WebIndex", Request:Request, **kwargs:Any) -> WebUserInfo:
	if hasattr(Request, "UserInfo"):
		self.Web.BASE.Logger.debug(f"(Web) Used stored infos: {str(Request.UserInfo)}", require="web:debug")
		return Request.UserInfo

	UserInfo:WebUserInfo = WebUserInfo(self.Web.BASE, Request, **kwargs)
	await UserInfo.auth()
	Request.UserInfo = UserInfo

	return Request.UserInfo
