from typing import TYPE_CHECKING, Any
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex

from aiohttp.web import Request
from Utils.Classes.htmlformatter import HTMLFormatter
from Utils.Classes.webuserinfo import WebUserInfo
from Utils.Classes.discorduserinfo import DiscordUserInfo
from Utils.Classes.storeclasses import GlobalStorage

def getNavbar(active:str="") -> HTMLFormatter:
	Navbar:HTMLFormatter = HTMLFormatter("Platforms/Web/Content/Html/Navbar/default.html")

	Navbar.replace(
		account_modal=getAccountModal()
	)

	Navbar.setRegex(r"\{selected_(.+?)\}")
	Navbar.replace(replace_empty=True, **{active:"active"})

	return Navbar

def getAccountModal() -> HTMLFormatter:
	try:
		discord_login_link:str = GlobalStorage.get("Phaazebot").Vars.DISCORD_LOGIN_LINK
	except:
		discord_login_link:str = "/discord?error"

	AccountModal:HTMLFormatter = HTMLFormatter("Platforms/Web/Content/Html/Modal/account.html")
	AccountModal.replace(
		replace_empty=True,
		discord_login_link=discord_login_link
	)
	return AccountModal

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

async def searchUser(cls:"WebIndex", where:str, values:tuple = None) -> list:
	"""
		Search user via custom 'where' statement
	"""
	statement:str = f"""
		SELECT
			`user`.*,
			GROUP_CONCAT(`role`.`name` SEPARATOR ';;;')
		FROM `user`
		LEFT JOIN `user_has_role`
			ON `user_has_role`.`user_id` = `user`.`id`
		LEFT JOIN `role`
			ON `role`.`id` = `user_has_role`.`role_id`
		WHERE {where}
		GROUP BY `user`.`id`"""

	res:list = cls.Web.BASE.PhaazeDB.query(statement, values)

	return_list:list = []
	for user in res:
		WebUser:WebUserInfo = WebUserInfo(cls.Web.BASE, None)
		await WebUser.finishUser(user)
		return_list.append(WebUser)

	return return_list
