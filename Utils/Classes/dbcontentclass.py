import json
from Utils.Classes.undefined import Undefined

class DBContentClass(object):
	"""
		Ground object for all classes, that get feeded with raw data from the database
		to create usable classes
	"""

	def fromJsonField(self, data:str or bytes) -> dict or list:
		"""
			converts json-string into a dict (or list)
			giving undefined or bool(data) == False
			will result in a empty dict
		"""
		if type(data) == Undefined: return dict()
		if not data: return dict()
		return json.loads(data)

	def fromStringList(self, data:str or bytes, seperator:str=",") -> list:
		"""
			splits string into a list,
			giving undefined or bool(data) == False
			will result in a empty list
		"""
		if type(data) == Undefined: return list()
		if not data: return list()
		return data.split(seperator)
