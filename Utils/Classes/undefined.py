class Undefined():
	"""
		This class is never (un)equal, bigger, smaller und else to everything, its nothing
	"""
	def __init__(self): pass

	def __eq__(self, value): # ==
		if type(value) == Undefined: return True
		return False
	def __ne__(self, value): # !=
		if type(value) != Undefined: return True
		return False

	def __ge__(self, value): return False # >=
	def __gt__(self, value): return False # >

	def __le__(self, value): return False # <=
	def __lt__(self, value): return False # <

	def __bool__(self): return False # if