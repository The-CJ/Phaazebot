from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from main import Phaazebot

import asyncio

def shutdownModule(BASE:"Phaazebot", module_name:str) -> bool:
	"""
		just enter the module name, found in BASE.Active and it will run
		the nessessery function to ensure a clean exit if needed.

		As far as i know, there should be no startModule function.
		Since it will be startet by the Mainframe corotine in
		Utils.threads.Mainframe.secureModules
	"""
	if not hasattr(BASE.Active, module_name): raise AttributeError(f"BASE.Active has no attribute '{module_name}'")

	if module_name == "discord":
		return shutdownModuleDiscord(BASE)

	return False

def shutdownModuleDiscord(BASE:"Phaazebot") -> bool:
	asyncio.ensure_future(BASE.Discord.logout() , loop=BASE.DiscordLoop)
	return True
