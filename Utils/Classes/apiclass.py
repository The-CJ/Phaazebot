from typing import Any

class APIClass(object):
	"""
		Utiliy class for all classes that have a .toJSON()
        to format it into a API save dict
	"""

	def toJSON(self) -> None:
		""" This function must be overwritten by the child class """
		raise AttributeError(f"{self.__class__.__name__} missing a .toJSON()")

	def toString(self, data:Any) -> str:
		"""
			ensures any input to be a string
		"""

		# any boolish false result = empty string
		if not data:
			return ""

		return str(data)

	def toBoolean(self, data:Any) -> bool:
		"""
			ensures any input to be a boolean
		"""

		return bool(data)

	def toInteger(self, data:Any) -> int:
		"""
			ensures any input to be a integer
		"""

		try:
			return int(data)
		except:
			return 0

	def toFloat(self, data:Any) -> int:
		"""
			ensures any input to be a float
		"""

		try:
			return float(data)
		except:
			return 0.0

	def toList(self, data:Any) -> list:
		"""
			tryes to ensures any input to be a api save list
			execpt thats impossible, so we just check if its a list,
			or return a empty one.... whopsi
		"""

		if type(data) is list:
			return data

		return []
