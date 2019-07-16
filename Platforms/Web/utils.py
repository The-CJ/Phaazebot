from typing import TYPE_CHECKING, Any
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex

from aiohttp.web import Request
from Utils.Classes.htmlformatter import HTMLFormatter
from Utils.Classes.webuserinfo import WebUserInfo
from Utils.Classes.discorduserinfo import DiscordUserInfo

def getNavbar(active:str="", UserInfo:WebUserInfo=None) -> HTMLFormatter:
	Navbar:HTMLFormatter = HTMLFormatter("Platforms/Web/Content/Html/Navbar/default.html")

	Navbar.replace(login_button=getLoginButton(UserInfo=UserInfo))

	Navbar.setRegex(r"\{selected_(.+?)\}")
	Navbar.replace(replace_empty=True, **{active:"active"})

	return Navbar

def getLoginButton(UserInfo:WebUserInfo=None) -> HTMLFormatter:
	Button:HTMLFormatter = HTMLFormatter("Platforms/Web/Content/Html/Button/account.html")

	return Button

async def getUserInfo(cls:"WebIndex", WebRequest:Request, **kwargs:Any) -> WebUserInfo:
	if hasattr(WebRequest, "UserInfo"):
		cls.Web.BASE.Logger.debug(f"(Web) Used stored infos: {str(WebRequest.UserInfo)}", require="web:debug")
		return WebRequest.UserInfo

	UserInfo:WebUserInfo = WebUserInfo(cls.Web.BASE, WebRequest, **kwargs)
	await UserInfo.auth()
	WebRequest.UserInfo = UserInfo

	return WebRequest.UserInfo

async def getDiscordUserInfo(cls:"WebIndex", WebRequest:Request, **kwargs:Any) -> DiscordUserInfo:
	if hasattr(WebRequest, "DiscordUser"):
		cls.Web.BASE.Logger.debug(f"(Web) Used stored discord infos: {str(WebRequest.DiscordUser)}", require="web:debug")
		return WebRequest.DiscordUser

	DiscordUser:DiscordUserInfo = DiscordUserInfo(cls.Web.BASE, WebRequest, **kwargs)
	await DiscordUser.auth()
	WebRequest.DiscordUser = DiscordUser

	return WebRequest.DiscordUser

async def searchUser(cls:"WebIndex", where:str) -> list:
	"""
		Search user via custom 'where' statement (store is 'user')
		All results get packed into a WebUserInfo object
	"""
	search:dict = dict(
		of="user",
		store="user",
		where=where,
		join=dict(
			of="role",
			store="role",
			where="role['id'] in user['role']",
			fields=["name", "id"]
		)
	)
	res:dict = cls.Web.BASE.PhaazeDB.select(**search)

	return_list:list = []
	for user in res.get("data", []):
		WebUser:WebUserInfo = WebUserInfo(cls.Web.BASE, None)
		await WebUser.finishUser(user)
		return_list.append(WebUser)

	return return_list
