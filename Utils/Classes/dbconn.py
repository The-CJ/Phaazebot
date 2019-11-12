from mysql.connector.cursor import MySQLCursorDict
from mysql.connector import connect, MySQLConnection
from mysql.connector.pooling import MySQLConnectionPool, PooledMySQLConnection

class DBConn(object):
	"""
		Should handle all incomming requests
	"""
	def __init__(self, host:str="localhost", port:str or int=3306, user:str="root", passwd:str="...", database:str=None):
		self.pool:MySQLConnectionPool = None
		self.CurrentConn:PooledMySQLConnection = None

		self.host:str = str(host)
		self.port:str = str(port)
		self.user:str = str(user)
		self.passwd:str = str(passwd)
		self.database:str = str(database)

	def query(self, sql:str, values:tuple or list = None) -> list:
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
				>> use .insertQuery() to ensure new row id

			Each query is in theory a transaction,
			use .getConnection() to get a own connection object.

				Then use connection.cursor to get a cursor,
				then make all requests with cursor.execute.
				If finished and everything worked without error,
				use connection.commit() to actully save all changes
				or connection.rollback() if needed.
		"""
		# setup
		Conn:PooledMySQLConnection = self.getConnection()
		Cursor:MySQLCursorDict = Conn.cursor(dictionary=True)

		# do stuff
		Cursor.execute(sql, values)

		# read and quess result
		if Cursor._have_unread_result(): res:list = Cursor.fetchall()
		elif Cursor.lastrowid: res:list = [Cursor.lastrowid]
		else: res:list = []

		# commit and close
		Conn.commit()
		Conn.close()

		return res

	def updateQuery(self, table:str=None, content:dict=None, where:str=None, where_values:tuple=None) -> None:
		"""
			dict bases, secured update query, all special chars will get replaced by byte safe sql counterpart
			here a quick example:

			table = "test"
			content = {"A": "123", "B":"abc", "C":420}
			where = "A != %s AND C = %s LIMIT 2"
			where_values = ("12345", 419)

			UPDATE `test` SET `A` = '123', `B` = 'abc', `C` = 420 WHERE A != '12345' AND C = 419 LIMIT 2;

			+ gets auto commited
		"""
		if not table or not content or not where: raise AttributeError("'table', 'content' and 'where' must be given")

		# prework
		setter:str = ", ".join([ f"`{key}` = %s" for key in content ])
		statement:str = f"""UPDATE `{table}` SET {setter} WHERE {where}"""
		values:tuple = tuple([content[key] for key in content]) + where_values

		# setup
		DBConn:MySQLConnection = self.getConnection()
		Cursor:MySQLCursorDict = DBConn.cursor(dictionary=True)

		# enable full char support, because i want to
		Cursor.execute('SET NAMES utf8mb4')
		Cursor.execute("SET CHARACTER SET utf8mb4")
		Cursor.execute("SET character_set_connection=utf8mb4")

		# do stuff
		Cursor.execute(statement, values)

		# commit and close
		DBConn.commit()
		DBConn.close()

		return

	def insertQuery(self, table:str=None, content:dict=None) -> None:
		"""
			dict bases, secured insert query, all special chars will get replaced by byte safe sql counterpart
			here a quick example:

			table = "test"
			content = {"A": "123", "B":"abc", "C":420}

			INSERT INTO `test` (`A`, `B`, `C`) VALUES ('123', 'abc', 420);

			+ gets auto commited
		"""
		if not table or not content: raise AttributeError("'table', and 'content' must be given")

		# prework
		keys:str = ", ".join(f"`{key}`" for key in content)
		value_holder:str = ", ".join("%s" for key in content)
		values:tuple = tuple(content[key] for key in content)

		statement:str = f"""INSERT INTO `{table}` ({keys}) VALUES ({value_holder})"""

		# setup
		DBConn:MySQLConnection = self.getConnection()
		Cursor:MySQLCursorDict = DBConn.cursor(dictionary=True)

		# enable full char support, because i want to
		Cursor.execute('SET NAMES utf8mb4')
		Cursor.execute("SET CHARACTER SET utf8mb4")
		Cursor.execute("SET character_set_connection=utf8mb4")

		# do stuff
		Cursor.execute(statement, values)

		# commit and close
		DBConn.commit()
		DBConn.close()

		return

	def getConnection(self, new:bool=False) -> PooledMySQLConnection:
		"""
			Returns a connection from the pool, (creates pool if none present)
			that can be used for transactions
			all changes can be undone with .rollback()

			finish a writing transactions with .commit()
		"""

		# reuse current connection
		if self.CurrentConn != None and not new:
			return self.CurrentConn

		# make pool
		if self.pool == None:
			self.generatePool()

		# inital pool is empty, restock
		if self.pool._cnx_queue.empty():
			self.pool.add_connection()

		# enable full char support
		self.CurrentConn = self.pool.get_connection()
		self.CurrentConn.set_charset_collation('utf8mb4')
		return self.CurrentConn

	def generatePool(self) -> None:
		self.pool = MySQLConnectionPool(
			pool_size = 3,
			host = self.host,
			port = self.port,
			user = self.user,
			passwd = self.passwd,
			database = self.database,
		)
