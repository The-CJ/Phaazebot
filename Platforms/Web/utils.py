from typing import TYPE_CHECKING, Any
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex

from aiohttp.web import Request
from Utils.Classes.htmlformatter import HTMLFormatter
from Utils.Classes.webuserinfo import WebUserInfo
from Utils.Classes.discordwebuserinfo import DiscordWebUserInfo
from Utils.Classes.storeclasses import GlobalStorage

# templating and stuff
def getNavbar(active:str="") -> HTMLFormatter:
	"""
		get the upper nav bar html,
		with all applied styles based on current location
	"""

	Navbar:HTMLFormatter = HTMLFormatter("Platforms/Web/Content/Html/Navbar/default.html")

	Navbar.replace(
		account_modal=getAccountModal()
	)

	Navbar.setRegex(r"\{selected_(.+?)\}")
	Navbar.replace(replace_empty=True, **{active:"active"})

	return Navbar

def getAccountModal() -> HTMLFormatter:
	"""
		get the global login form with all applied formated links etc...
	"""
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

# web translator
async def getWebUserInfo(cls:"WebIndex", WebRequest:Request, **kwargs:Any) -> WebUserInfo:
	"""
		Tryes to get a WebUser, takes get, post, and cookie in process
		kwargs are given to WebUserInfo

		WebUserInfo kwargs:
			force_method
			phaaze_session
			phaaze_token
			phaaze_username
			phaaze_password
	"""

	if hasattr(WebRequest, "WebUser"):
		cls.Web.BASE.Logger.debug(f"(Web) Used stored infos: {str(WebRequest.WebUser)}", require="web:debug")
		return WebRequest.WebUser

	WebUser:WebUserInfo = WebUserInfo(cls.Web.BASE, WebRequest, **kwargs)
	await WebUser.auth()
	WebRequest.WebUser = WebUser

	return WebRequest.WebUser

async def getDiscordUserInfo(cls:"WebIndex", WebRequest:Request, **kwargs:Any) -> DiscordWebUserInfo:
	"""
		Tryes to get a DiscordUser, takes get, post, and cookie in process
		kwargs are given to DiscordWebUserInfo

		DiscordWebUserInfo kwargs:
			force_method
			phaaze_discord_session
	"""

	if hasattr(WebRequest, "DiscordUser"):
		cls.Web.BASE.Logger.debug(f"(Web) Used stored discord infos: {str(WebRequest.DiscordUser)}", require="web:debug")
		return WebRequest.DiscordUser

	DiscordUser:DiscordWebUserInfo = DiscordWebUserInfo(cls.Web.BASE, WebRequest, **kwargs)
	await DiscordUser.auth()
	WebRequest.DiscordUser = DiscordUser

	return WebRequest.DiscordUser

# db managment
async def getWebUsers(cls:"WebIndex", where:str, values:tuple=None, limit:int=None, offset:int=None) -> list:
	"""
		Search user via custom 'where' statement
		'where' can include LIMIT and OFFSET,
		but not GROUP BY or ORDER
	"""
	statement:str = f"""
		SELECT
			`user`.*,
			GROUP_CONCAT(`role`.`name` SEPARATOR ';;;') AS `roles`
		FROM `user`
		LEFT JOIN `user_has_role`
			ON `user_has_role`.`user_id` = `user`.`id`
		LEFT JOIN `role`
			ON `role`.`id` = `user_has_role`.`role_id`
		WHERE {where}
		GROUP BY `user`.`id`"""

	if limit:
		statement += f" LIMIT {limit}"

	if offset:
		statement += f" OFFSET {offset}"

	res:list = cls.Web.BASE.PhaazeDB.selectQuery(statement, values)

	return_list:list = []
	for user in res:
		WebUser:WebUserInfo = WebUserInfo(cls.Web.BASE, None)
		await WebUser.finishUser(user)
		return_list.append(WebUser)

	return return_list

async def getWebUserAmount(cls:"WebIndex", where:str="1=1", values:tuple=()) -> int:
	""" simply gives a number of all matched user """

	res:list = cls.Web.BASE.PhaazeDB.selectQuery(f"SELECT COUNT(*) AS `I` FROM `user` WHERE {where}", values)

	return res[0]['I']
