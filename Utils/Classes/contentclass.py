from typing import Any, Union, List, Optional

import json
from datetime import datetime
from decimal import Decimal
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
	def asString(data:Any, allow_null:bool = False) -> Optional[str]:
		"""
		ensures any input to be a string
		"""

		if allow_null and (data is None or type(data) is Undefined):
			return None

		# any boolish false result = empty string
		if not data:
			return ""

		return str(data)

	@staticmethod
	def asBoolean(data:Any, allow_null:bool = False) -> Optional[bool]:
		"""
		ensures any input to be a boolean
		"""

		if allow_null and (data is None or type(data) is Undefined):
			return None

		return bool(data)

	@staticmethod
	def asInteger(data:Any, allow_null:bool = False) -> Optional[int]:
		"""
		ensures any input to be a integer
		"""

		if allow_null and (data is None or type(data) is Undefined):
			return None

		try:
			return int(data)
		except:
			return 0

	@staticmethod
	def asFloat(data:Any, allow_null:bool = False) -> Optional[float]:
		"""
		ensures any input to be a float
		"""

		if allow_null and (data is None or type(data) is Undefined):
			return None

		try:
			return float(data)
		except:
			return 0.0

	@staticmethod
	def asDatetime(data:Any, str_format:str = "%Y-%m-%d %H:%M:%S", allow_null:bool = False) -> Optional[datetime]:
		"""
		ensures any input to be a datetime object
		"""

		if allow_null and (data is None or type(data) is Undefined):
			return None

		if type(data) is datetime: return data

		try:
			return datetime.strptime(data, str_format)
		except:
			return datetime.strptime("2000-01-01 00:00:00", "%Y-%m-%d %H:%M:%S")

	@staticmethod
	def asList(data:Any, allow_null:bool = False) -> Optional[list]:
		"""
		tries to ensures any input to be a api save list
		except that's impossible, so we just check if its a list,
		or return a empty one.... whopsi
		"""

		if allow_null and (data is None or type(data) is Undefined):
			return None

		if type(data) is list:
			return data

		return []

	@classmethod
	def asDecimal(cls, data:Any, allow_null:bool = False) -> Optional[Decimal]:
		"""
		ensures any input to be a float
		"""

		if allow_null and (data is None or type(data) is Undefined):
			return None

		try:
			return Decimal(data)
		except:
			return Decimal(0)

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
	def fromStringList(data:Union[str, bytes], separator:str = ",") -> List[str]:
		"""
		splits string into a list,
		giving undefined or bool(data) == False
		will result in a empty list
		"""
		if type(data) == Undefined: return list()
		if not data: return list()
		return data.split(separator)
