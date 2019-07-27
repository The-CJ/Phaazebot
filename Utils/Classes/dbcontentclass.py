import json

class DBContentClass(object):
	"""
		Ground object for all classes, that get feeded with raw data from the database
		to create usable classes
	"""

	def fromJsonField(self, data:str or bytes or None):
		if not data: return None
		return json.loads(data)
