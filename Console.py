from colorama import Fore, Back, Style, init
from collections import deque
import asyncio, datetime

# Colorama Console INIT
init()

WRITE = True

##INFO
#Color format
#Fore: 		BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET.
#Back: 		BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET.
#Style: 	DIM, NORMAL, BRIGHT, RESET_ALL

SAFE_PRINT = deque([])
async def Debug_and_status_console(BASE):
	"""Thread save Debug Console"""

	while BASE.active.debug_console:
		if len(SAFE_PRINT) > 0:
			req = SAFE_PRINT.popleft()
			try:
				now = datetime.datetime.now()
				time_ = "["+now.strftime("%H:%M:%S")+"]"
				print(time_ + req)
			except: print("[" + Fore.RED + "CRITICAL ERROR" + Style.RESET_ALL + "] " + "Printing in Debug Console+ Failed")

		await asyncio.sleep(0.01)

	print("[INFO] Debug Console has been shutdown")

def WHITE(a, m):
	SAFE_PRINT.append("[" + a + Style.RESET_ALL + "]  " + m)

def BLACK(a, m):
	SAFE_PRINT.append("[" + Fore.BLACK + a + Style.RESET_ALL + "]  " + m)

def RED(a, m):
	SAFE_PRINT.append("[" + Fore.RED + a + Style.RESET_ALL + "] " + m)

def GREEN(a, m):
	SAFE_PRINT.append("[" + Fore.GREEN + a + Style.RESET_ALL + "] " + m)

def YELLOW(a, m):
	SAFE_PRINT.append("[" + Fore.YELLOW + a + Style.RESET_ALL + "] " + m)

def BLUE(a, m):
	SAFE_PRINT.append("[" + Fore.BLUE + Style.BRIGHT + a + Style.RESET_ALL + "] " + m)

def MAGENTA(a, m):
	SAFE_PRINT.append("[" + Fore.MAGENTA + a + Style.RESET_ALL + "] " + m)

def CYAN(a, m):
	SAFE_PRINT.append("[" + Fore.CYAN + a + Style.RESET_ALL + "] " + m)
