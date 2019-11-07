import json
from Utils.Classes.undefined import Undefined

class DBContentClass(object):
	"""
		Ground object for all classes, that get feeded with raw data from the database
		to create usable classes
	"""

	def fromJsonField(self, data:str or bytes or None) -> list:
		if type(data) == Undefined: return list()
		if not data: return list()
		return json.loads(data)

	def fromStringList(self, data:str or bytes or None, seperator:str=",") -> list:
		if type(data) == Undefined: return list()
		if not data: return list()
		return data.split(seperator)
