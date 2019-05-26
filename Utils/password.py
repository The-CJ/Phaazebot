import hashlib

def password(passwd:str) -> str:
	passwd = str(passwd)
	password:str = hashlib.sha256(passwd.encode("UTF-8")).hexdigest()
	return password
