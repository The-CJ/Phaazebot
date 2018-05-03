#BASE.moduls.Utils

import asyncio, discord

def list_XOR(list_1, list_2):
	list_1 = [hash(o) for o in list_1]
	list_2 = [hash(o) for o in list_2]

	check_list = list_1 + list_2
	diffr_list = []

	for obj in check_list:
		if (hash(obj) in list_1 or hash(obj) in list_2) and not (hash(obj) in list_1 and hash(obj) in list_2):
			diffr_list.append(obj)

	return diffr_list

def get_osu_status_symbol(state):
	#4 = loved, 3 = qualified, 2 = approved, 1 = ranked, 0 = pending, -1 = WIP, -2 = graveyard
	if state == "-2":
		return ":cross:"
	elif state == "-1":
		return ":tools:"
	elif state == "0":
		return ":clock1:"
	elif state == "1":
		return ":large_blue_diamond:"
	elif state == "2":
		return ":fire:"
	elif state == "3":
		return ":sweat_drops:"
	elif state == "4":
		return ":heart:"
	else: return ":question:"

#OS controll
async def reload_base(BASE):
	BASE.RELOAD = True
	BASE.moduls.Console.BLUE("SYSTEM INFO","Reloading Base...")

	BASE.load_BASE(BASE)
	BASE.moduls.Console.BLUE("SYSTEM INFO","Base Reloaded")

	BASE.moduls._Web_.Base.RequestHandler.BASE = BASE
	BASE.moduls.Console.BLUE("SYSTEM INFO","Refreshed Web-Handler")

	setattr(BASE.vars, "app", BASE.run_async(BASE.discord.application_info(), exc_loop=BASE.Discord_loop) )
	BASE.moduls.Console.BLUE("SYSTEM INFO","Refreshed Discord App Info")

	BASE.run_async(BASE.discord.change_presence(game=discord.Game(type=0, name=BASE.version_nr), status=discord.Status.online), exc_loop=BASE.Discord_loop)
	BASE.moduls.Console.BLUE("SYSTEM INFO","Refreshed Discord Status")

	BASE.moduls._Twitch_.Alerts.Init_Main(BASE)
	BASE.moduls.Console.BLUE("SYSTEM INFO","Reinitialized Twitch Alert")

	BASE.RELOAD = False
	BASE.moduls.Console.BLUE("SYSTEM INFO","BASE Reload Successfull!")

