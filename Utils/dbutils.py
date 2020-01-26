from typing import Any

def validateDBInput(wanted_type:type, value:Any, alternative:Any=None, allow_null:bool=False) -> str:
	"""
		Transforms any input into the wanted input for a database.
		Tryes to give back value in a wanted input, if not possible return alternative
		Really usefull for bool operations
		Means:
			validateDBInput( bool, "reee" ) -> "1"
			validateDBInput( int, "58452" ) -> "58452"
			validateDBInput( str, 548452 ) -> "548452"
			validateDBInput( bool, "0" ) -> "0"
			validateDBInput( bool, "false" ) -> "0"

		If allow_null is true and None is passed as `value`, it returns None, since NULL is a valid DB type for all
	"""
	if allow_null and value == None: return None

	if wanted_type == bool:
		if value in ["true", "True", "1", True]:
			return "1"
		elif value in ["false", "False", "0", False]:
			return "0"

		if bool(value): return "1"
		else: return "0"

	if wanted_type == int:
		if type(value) == str:
			if value.isdigit():
				return value
			else:
				try:
					return int(value)
				except:
					return alternative

	return str(value)
