import hashlib
import string
import random

def password(passwd:str) -> str:
	"""
		returns any string into a sha256 encoded password hash
	"""
	passwd = str(passwd)
	password:str = hashlib.sha256(passwd.encode("UTF-8")).hexdigest()
	return password

def randomString(size:int = 10, pool:list = [1,2,3], extra:str = "", remove:str=",`'") -> str:
	"""
		returns a random generated string by size
		based on the allowed char pool,
		extra chars can be passed by 'extra', removed via 'remove'
		(remove first, then add extra)

		Pools:
		1 - digits
		2 - uppercase chars
		3 - lowerchase chars
		4 - punctuation
	"""
	string_pool:str = ""
	if 1 in pool: string_pool += string.digits
	if 2 in pool: string_pool += string.ascii_uppercase
	if 3 in pool: string_pool += string.ascii_lowercase
	if 4 in pool: string_pool += string.punctuation

	# remove unwanted
	for char in remove:
		string_pool = string_pool.replace(char, "")

	# add extra
	string_pool += extra

	key = ''.join(random.choice(string_pool) for x in range(size))
	return key

def numberToHugeLetter(number:int) -> str:
	numbers:dict = {
		"0": ":zero:",
		"1": ":one:",
		"2": ":two:",
		"3": ":three:",
		"4": ":four:",
		"5": ":five:",
		"6": ":six:",
		"7": ":seven:",
		"8": ":eight:",
		"9": ":nine:"
	}

	number = str(number)
	return "".join([numbers.get(x, "") for x in number])

def prettifyNumbers(number:int or float, ndigits:int=2, sepperator:str="'") -> str:
	"""
		Turns a number into a dottet format to make it easyer readable,
		or make floats to a fix value
	"""

	if not number: return "0"

	if type(number) == str:
		try:
			if ndigits:
				number = float(number)
			else:
				number = int(number)
		except:
			return number

	if not ndigits:
		return ("{:,}".format( number, ndigits )).replace(",", sepperator)
	else:
		return ("{:,}".format( round(number, ndigits) )).replace(",", sepperator)
