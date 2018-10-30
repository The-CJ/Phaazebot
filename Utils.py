#BASE.modules.Utils

import asyncio, discord, string, random

def random_string(size=10):
	s = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(size))
	return s

#OS controll
async def reload_base(BASE):
	BASE.RELOAD = True
	BASE.modules.Console.INFO("Reloading Base...")

	BASE.load_BASE(BASE)
	BASE.modules.Console.INFO("Base Reloaded")

	BASE.modules._Web_.Base.RequestHandler.BASE = BASE
	BASE.modules.Console.INFO("Refreshed Web-Handler")

	setattr(BASE.vars, "app", BASE.run_async(BASE.discord.application_info(), exc_loop=BASE.Discord_loop) )
	BASE.modules.Console.INFO("Refreshed Discord App Info")

	BASE.run_async(BASE.discord.change_presence(game=discord.Game(type=0, name=f"{BASE.vars.TRIGGER_DISCORD} | v{BASE.version}"), status=discord.Status.online), exc_loop=BASE.Discord_loop)
	BASE.modules.Console.INFO("Refreshed Discord Status")

	BASE.modules._Twitch_.Alerts.Init_Main(BASE)
	BASE.modules.Console.INFO("Reinitialized Twitch Alert")

	BASE.RELOAD = False
	BASE.modules.Console.INFO("BASE Reload Successfull!")

