from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from phaazebot import Phaazebot

import asyncio

# module management
def shutdownModule(BASE:"Phaazebot", module_name:str) -> bool:
	"""
	just enter the module name, found in BASE.Active and it will run
	the necessary function to ensure a clean exit if needed.

	As far as i know, there should be no startModule function.
	Since it will be started by the Mainframe coroutine in
	Utils.threads.Mainframe.secureModules
	"""
	if not hasattr(BASE.Active, module_name): raise AttributeError(f"BASE.Active has no attribute '{module_name}'")

	BASE.Logger.info(f"Got shutdown event for module: '{module_name}'")

	if module_name == "discord":
		return shutdownModuleDiscord(BASE)

	elif module_name == "twitch_irc":
		return shutdownModuleTwitchIRC(BASE)

	elif module_name == "osu_irc":
		return shutdownModuleOsuIRC(BASE)

	elif module_name == "web":
		return shutdownModuleWeb(BASE)

	elif module_name == "twitch_events":
		return shutdownModuleTwitchEvents(BASE)

	return False

def shutdownModuleDiscord(BASE:"Phaazebot") -> bool:
	"""
	shutdown the discord module just means, logout from discord
	the discord thread will be done after logout
	"""
	asyncio.ensure_future(BASE.Discord.logout(), loop=BASE.DiscordLoop)
	return True

def shutdownModuleTwitchIRC(BASE:"Phaazebot") -> bool:
	"""
	shutdown the twitch module aka just stop everything
	the twitch thread will be done after stop is done
	"""
	BASE.Twitch.stop()
	return True

def shutdownModuleOsuIRC(BASE:"Phaazebot") -> bool:
	"""
	shutdown the twitch module aka just stop everything
	the twitch thread will be done after stop is done
	"""
	BASE.Osu.stop()
	return True

def shutdownModuleWeb(BASE:"Phaazebot") -> bool:
	"""
	shutdown the web module means, end all current operations
	of send a disconnect event to all clients.
	that should be handled by the functions in on_shutdown
	from Platform.Web.main_web.PhaazebotWeb
	"""
	asyncio.ensure_future(BASE.Web.shutdown(), loop=BASE.WebLoop)
	return True

def shutdownModuleTwitchEvents(BASE:"Phaazebot") -> bool:
	"""
	this is actually just to be sure i guess
	"""
	BASE.TwitchEvents.stop()
	return True
