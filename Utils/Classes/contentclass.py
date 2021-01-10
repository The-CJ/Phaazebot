from typing import Any, Union, List

import json
from datetime import datetime
from Utils.Classes.undefined import Undefined

class ContentClass(object):
	"""
	Ground object for all classes,
	that get fed with raw data from the database
	or goes out to API responses.

	Or a simple class for type conversion.
	"""

	def toJSON(self) -> None:
		""" This function must be overwritten by the child class """
		raise AttributeError(f"{self.__class__.__name__} missing a .toJSON()")

	@staticmethod
	def asString(data:Any) -> str:
		"""
		ensures any input to be a string
		"""

		# any boolish false result = empty string
		if not data:
			return ""

		return str(data)

	@staticmethod
	def asBoolean(data:Any) -> bool:
		"""
		ensures any input to be a boolean
		"""

		return bool(data)

	@staticmethod
	def asInteger(data:Any) -> int:
		"""
		ensures any input to be a integer
		"""

		try:
			return int(data)
		except:
			return 0

	@staticmethod
	def asFloat(data:Any) -> float:
		"""
		ensures any input to be a float
		"""

		try:
			return float(data)
		except:
			return 0.0

	@staticmethod
	def asDatetime(data:Any, str_format:str="%Y-%m-%d %H:%M:%S") -> datetime:
		"""
		ensures any input to be a datetime object
		"""

		try:
			return datetime.strptime(data, str_format)
		except:
			return datetime.strptime("2000-01-01 00:00:00", "%Y-%m-%d %H:%M:%S")

	@staticmethod
	def fromJsonField(data:Union[str, bytes]) -> Union[dict, list]:
		"""
		converts json-string into a dict (or list)
		giving undefined or bool(data) == False
		will result in a empty dict
		"""
		if type(data) == Undefined: return dict()
		if not data: return dict()
		return json.loads(data)

	@staticmethod
	def fromStringList(data:Union[str, bytes], separator:str= ",") -> List[str]:
		"""
		splits string into a list,
		giving undefined or bool(data) == False
		will result in a empty list
		"""
		if type(data) == Undefined: return list()
		if not data: return list()
		return data.split(separator)
