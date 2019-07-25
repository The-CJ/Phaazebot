from mysql.connector.cursor import MySQLCursorDict
from mysql.connector import connect, MySQLConnection

class DBConn(object):
	"""
		Should handle all incomming requests
	"""
	def __init__(self, host:str="localhost", user:str="root", passwd:str="...", database:str=None):
		self.host:str = host
		self.user:str = user
		self.passwd:str = passwd
		self.database:str = database

	def query(self, sql:str, values:tuple or list = None) -> list:
		"""
			Querys a SQL command.

			Each query is in thery a transaction,
			use self.getConnection()
			to get a own connection object.

			Then use connection.cursor to make all requests,
			if finished and everything worked without error,
			use connection.commit() to actully save all changes
		"""
		# setup
		DBConn:MySQLConnection = self.getConnection()
		Cursor:MySQLCursorDict = DBConn.cursor(dictionary=True)

		# enable full char support, because i want to
		Cursor.execute('SET NAMES utf8mb4')
		Cursor.execute("SET CHARACTER SET utf8mb4")
		Cursor.execute("SET character_set_connection=utf8mb4")

		# do stuff
		Cursor.execute(sql, values)

		# read result
		if Cursor._have_unread_result(): res:list = Cursor.fetchall()
		else: res:list = []

		# commit and close
		DBConn.commit()
		DBConn.close()

		return res

	def updateQuery(self, table:str=None, content:dict=None, where:str=None, where_values:tuple=None, limit:int=None) -> None:
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

	def getConnection(self) -> MySQLConnection:
		"""
			Returns a connection for the db,
			that can be used for transactions
			all changes can be undone by connection.rollback()

			finish a connection with commit() and close()
		"""
		return connect(
			host = self.host,
			user = self.user,
			passwd = self.passwd,
			database = self.database,
		)
