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
