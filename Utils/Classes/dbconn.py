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

	def query(self, sql:str, values:tuple or list = None, commit:bool = False) -> list:
		"""
			Querys a SQL command.
			If its a writing action, commit MUST be true.
			Else no action is taken.
			Returns a list of dict
		"""
		DBConn:MySQLConnection = connect(
			host = self.host,
			user = self.user,
			passwd = self.passwd,
			database = self.database
		)

		Cursor:MySQLCursorDict = DBConn.cursor(dictionary=True)

		Cursor.execute(sql, values)

		if commit:
			DBConn.commit()

		res:list = Cursor.fetchall()

		DBConn.close()

		return res
