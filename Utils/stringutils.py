import hashlib
import string
import random

def password(passwd:str) -> str:
	passwd = str(passwd)
	password:str = hashlib.sha256(passwd.encode("UTF-8")).hexdigest()
	return password

def randomString(size:int = 10) -> str:
	key = ''.join(random.choice(string.ascii_uppercase + string.ascii_letters + string.digits) for x in range(size))
	return key
