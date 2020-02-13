from mysql.connector.cursor import MySQLCursorDict
from mysql.connector import MySQLConnection

class DBConn(object):
	"""
		Should handle all incomming requests
		call .setMassRequest(True) to prevent closing connection
		and reuse the last connection

		DEBUG:
		All query function take an optional `debug` kwarg
		it is not returned, but gets filled with various data.
		Just give a dict reference with the call to get the data.

		For example, to get the formated query actully send to the server:
		< d = dict()
		< DBConn.query("SELECT * FROM table WHERE id = %s OR name LIKE = %s", (544, 'CJ'), debug=d)
		< print(d.get("last_statement", ""))
		> SELECT * FROM table WHERE id = 544 OR name LIKE = 'CJ'

	"""
	def __init__(self, host:str="localhost", port:str or int=3306, user:str="root", passwd:str="...", database:str=None):
		self.host:str = str(host)
		self.port:str = str(port)
		self.user:str = str(user)
		self.passwd:str = str(passwd)
		self.database:str = str(database)

		self.mass_request:bool = False
		self.MassRequestConn:MySQLConnection = None

		# if != None, called with last statement as arg, for logging etc.
		self.statement_func:callable = None

	def query(self, sql:str, values:tuple or dict = None, debug:dict={}) -> list:
		"""
			Querys a SQL command. Using a MySQLCursorDict.
			query made via this function get auto commited

			Tryes to return values based on the status the Cursor have after finish.

			Return cases
				Does cursor has unread result?
				If yes, its probly a SELECT query
				> Fetch all and return list of dict
				>> use .selectQuery() to ensure SELECT return

				Does cursor have a lastrowid?
				If yes, its probly a INSERT query
				> Return list with one element, the new row id
				>> use .insertQuery() to ensure INSERT new_row_id

			Each query is in theory a transaction,
			use .getConnection() to get a own connection object.

				Then use connection.cursor to get a cursor,
				then make all requests with cursor.execute()
				If finished and everything worked without error,
				use connection.commit() to actully save all changes
				or connection.rollback() if needed.
		"""
		# setup
		Conn:MySQLConnection = self.getConnection()
		Cursor:MySQLCursorDict = Conn.cursor(dictionary=True)

		# do stuff
		self.executeQuery(Cursor, sql, values, debug)

		# read and quess result
		if Cursor._have_unread_result(): res:list = Cursor.fetchall()
		elif Cursor.lastrowid: res:list = [Cursor.lastrowid]
		else: res:list = []

		# commit and close?
		Conn.commit()
		if not self.mass_request: Conn.close()

		return res

	def selectQuery(self, sql:str, values:tuple or dict = None, debug:dict={}) -> list:
		"""
			Pretty much the same as a normal .query()
			except it ensures a list with sets return

			Returns a list of result sets.
		"""
		# setup
		Conn:MySQLConnection = self.getConnection()
		Cursor:MySQLCursorDict = Conn.cursor(dictionary=True)

		# do stuff
		self.executeQuery(Cursor, sql, values, debug)

		# gather stuff
		res:list = Cursor.fetchall()

		# close?, commit is not necessary in a select
		if not self.mass_request: Conn.close()

		return res

	def deleteQuery(self, sql:str, values:tuple or dict = None, debug:dict={}) -> int:
		"""
			Pretty much the same as a normal .query()
			except it ensures a int return

			Returns the number of affected rows.
		"""
		# setup
		Conn:MySQLConnection = self.getConnection()
		Cursor:MySQLCursorDict = Conn.cursor(dictionary=True)

		# do stuff
		self.executeQuery(Cursor, sql, values, debug)

		# commit and close?
		Conn.commit()
		if not self.mass_request: Conn.close()

		return int(Cursor.rowcount)

	def updateQuery(self, table:str=None, content:dict=None, where:str=None, where_values:tuple=(), debug:dict={}) -> int:
		"""
			dict bases, secured update query,
			all special chars will get replaced by byte safe sql counterpart
			query made via this function get auto commited

			here a quick example:

			table = "test"
			content = {"A": "123", "B":"abc", "C":420}
			where = "A != %s AND C = %s LIMIT 2"
			where_values = ("12345", 419)

			UPDATE `test` SET `A` = '123', `B` = 'abc', `C` = 420 WHERE A != '12345' AND C = 419 LIMIT 2;

			Returns the number of affected rows.
		"""
		if not table or not content or not where: raise AttributeError("'table', 'content' and 'where' must be given")

		# prework
		setter:str = ", ".join([ f"`{key}` = %s" for key in content ])
		statement:str = f"""UPDATE `{table}` SET {setter} WHERE {where}"""
		values:tuple = tuple([content[key] for key in content]) + where_values

		# setup
		Conn:MySQLConnection = self.getConnection()
		Cursor:MySQLCursorDict = Conn.cursor(dictionary=True)

		# do stuff
		self.executeQuery(Cursor, statement, values, debug)

		# commit and close?
		Conn.commit()
		if not self.mass_request: Conn.close()

		return int(Cursor.rowcount)

	def insertQuery(self, table:str=None, content:dict=None, debug:dict={}) -> int:
		"""
			dict bases, secured insert query,
			all special chars will get replaced by byte safe sql counterpart
			query made via this function get auto commited

			here a quick example:

			table = "test"
			content = {"A": "123", "B":"abc", "C":420}

			INSERT INTO `test` (`A`, `B`, `C`) VALUES ('123', 'abc', 420);

			Returns
		"""
		if not table or not content: raise AttributeError("'table', and 'content' must be given")

		# prework
		keys:str = ", ".join(f"`{key}`" for key in content)
		value_holder:str = ", ".join("%s" for key in content)
		values:tuple = tuple(content[key] for key in content)

		statement:str = f"""INSERT INTO `{table}` ({keys}) VALUES ({value_holder})"""

		# setup
		Conn:MySQLConnection = self.getConnection()
		Cursor:MySQLCursorDict = Conn.cursor(dictionary=True)

		# do stuff
		self.executeQuery(Cursor, statement, values, debug)

		# commit and close
		Conn.commit()
		if not self.mass_request: Conn.close()

		return Cursor.lastrowid

	def executeQuery(self, Cursor:MySQLCursorDict, sql:str, values:tuple or dict, debug:dict) -> None:
		"""
			Just wrappes the query in a try catch to get the statement and debug funtions
		"""
		try:
			Cursor.execute(sql, values)
			debug["last_statement"] = Cursor.statement
			if self.statement_func != None:
				self.statement_func(debug["last_statement"])

		except Exception as E:
			debug["last_statement"] = Cursor.statement
			if self.statement_func != None:
				self.statement_func(debug["last_statement"])

			raise E

	def getConnection(self) -> MySQLConnection:
		"""
			Returns a connection, (could be a used one if .mass_request is True)
			that can be used for transactions
			all changes can be undone with .rollback()

			finish a writing transactions with .commit()
		"""

		if self.mass_request:
			if self.MassRequestConn != None:
				return self.MassRequestConn
			else:
				self.MassRequestConn = self.createConnection()
				return self.MassRequestConn

		return self.createConnection()

	def createConnection(self) -> MySQLConnection:
		"""
			same as .getConnection execpt it's always a new connection
			.getConnection could also be a already used one because .mass_request is True
		"""
		Conn:MySQLConnection = MySQLConnection(
			host = self.host,
			port = self.port,
			user = self.user,
			passwd = self.passwd,
			database = self.database,
		)

		# enable full char support
		Conn.set_charset_collation("utf8mb4")

		return Conn

	def setMassRequest(self, state:bool) -> None:
		"""
			Mass requests will hold a connection open, after any other operation in this class.
			It will still be commited but not closed.
			This will increase the speed but making the entire class Threading unsave.
			Its recommended to make a new DBConn() object and enable mass request in this.

			a stored instance of a mass request connection can timeout if left unused.
		"""
		self.mass_request = state
