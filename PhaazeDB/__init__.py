import requests, json

class Connection():
	def __init__(self, adress="http://127.0.0.1", port="", user=None, password=None):
		self.session = requests.session()
		self.adress = adress
		self.port = str(port) if port == "" else ":" + str(port)
		self.user = user
		self.password = password

	def set_connection(self, adress="http://127.0.0.1", port="", user=None, password=None):
		self.adress = adress
		self.port = str(port) if port == "" else ":" + str(port)
		self.user = user
		self.password = password

	def create(self, name=None):
		if name == None: raise

		call = dict(
			action="create",
			login=self.user,
			password=self.password,
			name=name)

		try: r = self.session.post(self.adress+self.port, json=call)
		except: raise ConnectionError

		res = json.loads(r.text)
		return res

	def drop(self, name=None):
		if name == None: raise

		call = dict(
			action="drop",
			login=self.user,
			password=self.password,
			name=name)

		try: r = self.session.post(self.adress+self.port, json=call)
		except: raise ConnectionError

		res = json.loads(r.text)
		return res

	def insert(self, into=None, content=None):
		if into == None or content == None: raise AttributeError

		if type(content) is not dict(): raise AttributeError

		call = dict(
			action="insert",
			login=self.user,
			password=self.password,
			into=into,
			content=content)

		try: r = self.session.post(self.adress+self.port, json=call)
		except: raise ConnectionError

		res = json.loads(r.text)
		return res

	def delete(self, of=None, where=""):
		if of == None: raise

		call = dict(
			action="delete",
			login=self.user,
			password=self.password,
			of=of,
			where=where)

		try: r = self.session.post(self.adress+self.port, json=call)
		except: raise ConnectionError

		res = json.loads(r.text)
		return res

	def update(self, of=None, where="", content=None):
		if of == None or content == None: raise AttributeError

		if type(content) is not dict(): raise AttributeError

		call = dict(
			action="update",
			login=self.user,
			password=self.password,
			of=of,
			where=where,
			content=content
			)

		try: r = self.session.post(self.adress+self.port, json=call)
		except: raise ConnectionError

		res = json.loads(r.text)
		return res

	def select(self, of=None, where="", fields=[]):
		if of == None: raise AttributeError
		if type(fields) is not list(): AttributeError

		call = dict(
			action="select",
			login=self.user,
			password=self.password,
			of=of,
			where=where,
			fields=fields)

		try: r = self.session.post(self.adress+self.port, json=call)
		except: raise ConnectionError

		res = json.loads(r.text)
		return res

