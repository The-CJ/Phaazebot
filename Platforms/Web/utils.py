from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from phaazebot import Phaazebot
	from Platforms.Web.main_web import PhaazebotWeb

from Utils.Classes.authdiscordwebuser import AuthDiscordWebUser
from Utils.Classes.authtwitchwebuser import AuthTwitchWebUser
from Utils.Classes.extendedrequest import ExtendedRequest
from Utils.Classes.htmlformatter import HTMLFormatter
from Utils.Classes.storeclasses import GlobalStorage
from Utils.Classes.authwebuser import AuthWebUser
from Platforms.Discord.api import generateDiscordAuthLink
from Platforms.Twitch.api import generateTwitchAuthLink

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
	get the global login form with all applied formatted links etc...
	"""
	PhaazeMain:"Phaazebot" = GlobalStorage.get("Phaazebot")
	try:
		discord_login_link:str = generateDiscordAuthLink(PhaazeMain)
		twitch_login_link:str = generateTwitchAuthLink(PhaazeMain)
	except Exception as E:
		PhaazeMain.Logger.error(f"getAccountModal - {str(E)}")
		discord_login_link:str = "/discord?error"
		twitch_login_link:str = "/twitch?error"

	AccountModal:HTMLFormatter = HTMLFormatter("Platforms/Web/Content/Html/Modal/account.html")
	AccountModal.replace(
		replace_empty=True,
		discord_login_link=discord_login_link,
		twitch_login_link=twitch_login_link,
	)
	return AccountModal

# web authorizer
async def authWebUser(cls:"PhaazebotWeb", WebRequest:ExtendedRequest, **kwargs) -> AuthWebUser:
	"""
	Tries to get a  (Auth)WebUser associated with a request, takes get, post, and cookie in process

	Optional 'system' keywords:
	---------------------------
	* `force_method` - str
	* `phaaze_session` - str
	* `phaaze_token` - str
	* `phaaze_username` - str
	* `phaaze_password` - str
	"""

	if hasattr(WebRequest, "AuthWeb"):
		if WebRequest.AuthWeb is not None:
			cls.BASE.Logger.debug(f"(Web) Used stored info's: {str(WebRequest.AuthWeb)}", require="web:debug")
			return WebRequest.AuthWeb

	AuthUser:AuthWebUser = AuthWebUser(cls.BASE, WebRequest, **kwargs)
	await AuthUser.auth()
	WebRequest.AuthWeb = AuthUser

	return WebRequest.AuthWeb

async def authDiscordWebUser(cls:"PhaazebotWeb", WebRequest:ExtendedRequest, **kwargs) -> AuthDiscordWebUser:
	"""
	Tries to get a DiscordUser, takes get, post, and cookie in process
	kwargs are given to DiscordWebUser

	DiscordWebUser kwargs:
		force_method
		phaaze_discord_session
	"""

	if hasattr(WebRequest, "AuthDiscord"):
		if WebRequest.AuthDiscord is not None:
			cls.BASE.Logger.debug(f"(Web) Used stored discord info's: {str(WebRequest.AuthDiscord)}", require="web:debug")
			return WebRequest.AuthDiscord

	AuthDiscord:AuthDiscordWebUser = AuthDiscordWebUser(cls.BASE, WebRequest, **kwargs)
	await AuthDiscord.auth()
	WebRequest.AuthDiscord = AuthDiscord

	return WebRequest.AuthDiscord

async def authTwitchWebUser(cls: "PhaazebotWeb", WebRequest:ExtendedRequest, **kwargs) -> AuthTwitchWebUser:
	"""
	Tries to get a DiscordUser, takes get, post, and cookie in process
	kwargs are given to TwitchWebUser

	TwitchWebUser kwargs:
		force_method
		phaaze_twitch_session
	"""

	if hasattr(WebRequest, "AuthTwitch"):
		if WebRequest.AuthTwitch is not None:
			cls.BASE.Logger.debug(f"(Web) Used stored twitch info's: {str(WebRequest.AuthTwitch)}", require="web:debug")
			return WebRequest.AuthTwitch

	AuthTwitch:AuthTwitchWebUser = AuthTwitchWebUser(cls.BASE, WebRequest, **kwargs)
	await AuthTwitch.auth()
	WebRequest.AuthTwitch = AuthTwitch

	return WebRequest.AuthTwitch
