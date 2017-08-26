from colorama import Fore, Back, Style, init
import asyncio, tkinter, datetime
init()

WRITE = True

##INFO
#Color format
#Fore: 		BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET.
#Back: 		BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET.
#Style: 	DIM, NORMAL, BRIGHT, RESET_ALL

Save_print = []
async def Debug_and_status_console(BASE):
	"""Thread save Debug Console"""

	while BASE.active.debug_console:
		if len(Save_print) > 0:
			req = Save_print[0]
			Save_print.remove(Save_print[0])
			try:
				now = datetime.datetime.now()
				time_ = "["+now.strftime("%H:%M:%S")+"]"
				print(time_ + req)
			except: print("[" + Fore.RED + "CRITICAL ERROR" + Style.RESET_ALL + "] " + "Printing in Debug+ Console Failed")

		await asyncio.sleep(0.01)

	print("[INFO] Debug Console has been shutdown")

def WHITE(a, m):
	Save_print.append("[" + a + Style.RESET_ALL + "]  " + m)

def BLACK(a, m):
	Save_print.append("[" + Fore.BLACK + a + Style.RESET_ALL + "]  " + m)

def RED(a, m):
	Save_print.append("[" + Fore.RED + a + Style.RESET_ALL + "] " + m)

def GREEN(a, m):
	Save_print.append("[" + Fore.GREEN + a + Style.RESET_ALL + "] " + m)

def YELLOW(a, m):
	Save_print.append("[" + Fore.YELLOW + a + Style.RESET_ALL + "] " + m)

def BLUE(a, m):
	Save_print.append("[" + Fore.BLUE + Style.BRIGHT + a + Style.RESET_ALL + "] " + m)

def MAGENTA(a, m):
	Save_print.append("[" + Fore.MAGENTA + a + Style.RESET_ALL + "] " + m)

def CYAN(a, m):
	Save_print.append("[" + Fore.CYAN + a + Style.RESET_ALL + "] " + m)
