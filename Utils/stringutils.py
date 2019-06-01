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

def randomString(size:int = 10, pool:list = [1,2,3], extra:str = "") -> str:
	"""
		returns a random generated string by size
		based on the allowd char pool, extra cahrs can be passed by 'extra'
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
	key = ''.join(random.choice(string_pool+extra) for x in range(size))
	return key
