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
		DBConn:MySQLConnection = self.getConnection()

		Cursor:MySQLCursorDict = DBConn.cursor(dictionary=True)
		Cursor.execute(sql, values)

		if Cursor._have_unread_result(): res:list = Cursor.fetchall()
		else: res:list = []

		DBConn.commit()
		DBConn.close()

		return res

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
			database = self.database
		)
