from typing import List, Any, Dict, Union
from Utils.Classes.undefined import Undefined, UNDEFINED

class StorageTransformer(object):
	"""
	This class is... well both, a Storage and a Transformer
	and a bit formatter, i guess.

	Simple theory, add a `key`, `value` pair via .get()
	but also give it a `wanted_type`.
	"Simple" types will work best for this, like str and int,
	but other types or classes also work... at least we can try

	NOTE: only using (one dimensional) "simple" types,
	will result in a API/JSON save dict

	Not setting a wanted_type will skip transforming and return raw

	# Example
	X = StorageTransformer()
	X.set("key_1", 123456, wanted_type=str)
	X.set("key_2", UNDEFINED, wanted_type=int)
	X.set("key_3", "OK", wanted_type=bool)

	x.getRaw("key_1") => 123456
	x.getTransform("key_1") => "123456"

	x.getRaw("key_2") => UNDEFINED
	x.getTransform("key_1") => 0

	x.getRaw("key_3") => "OK"
	x.getTransform("key_3") => True

	# protected keys
	since this is also a storage, you can define keys that will:
	* not be transformed
	* not be included

	x.protected_keys.append("key_2")
	x.getAllRaw() => {"key_1":123456, "key_2":UNDEFINED, "key_3":"OK"}
	x.getAllTransform() = {"key_1":"123456", "key_3":True}
	"""

	def __init__(self):
		self.protected_keys:List[str] = []
		self.wanted_types:Dict[str, type] = {}
		self.storage:Dict[str, Any] = {}

	def __repr__(self):
		items:int = len(self.storage)
		return f"<{self.__class__.__name__} {items} entry's>"

	# utils
	def setType(self, key:str, wanted_type:type) -> None:
		"""
		allows setting of types without passing new data, even before setting keys
		"""
		self.wanted_types[key] = wanted_type

	def unsetType(self, key:str) -> None:
		"""
		unset saved type, so key will not get transformed
		"""
		self.wanted_types.pop(key, None)

	def addProtected(self, key:str) -> None:
		"""
		adds a key to be protected
		"""
		if key not in self.protected_keys:
			self.protected_keys.append(key)

	def removeProtected(self, key:str) -> None:
		"""
		removes a  protected key
		"""
		if key in self.protected_keys:
			self.protected_keys.remove(key)

	# set & unset
	def set(self, key:str, value:Any, wanted_type:Union[type, None]=None) -> None:
		"""
		Set a new value, allows to give a `wanted_type` that's
		used later in .transform() and allTransform()
		"""
		if type(key) is not str:
			raise AttributeError(f"`key` must be str, not {type(key)}, because i say so")

		# save value
		self.storage[key] = value

		# remember wanted type, if given
		if wanted_type is not None:
			self.wanted_types[key] = wanted_type

	def unset(self, key:str) -> None:
		"""
		Unsets a key.
		Or better said, it completely deletes them, also the remembered type
		"""
		self.storage.pop(key, None)
		self.wanted_types.pop(key, None)

	# raw getter
	def getRaw(self, key:str, alternative:Any) -> Any:
		"""
		Tries to return the value associated with `key`, or `alternative`.
		basically the same as self.storage.get()
		"""
		return self.storage.get(key, alternative)

	def getAllRaw(self) -> Dict[str, Any]:
		"""
		basically just self.storage
		"""
		return self.storage

	# getter transformed
	def getTransform(self, key:str, alternative:Any, overwrite_type:Union[type, None]=None) -> Any:
		"""
		Tries to return the value associated with `key`, or `alternative`.
		if a `wanted_type` was set, it tries to transform,
		raise's AttributeError if transformation failed.

		Calling this function allows transforming of keys that are protected
		"""
		# filter out protected
		value:Any = self.storage.get(key, alternative)
		wanted_type:type = self.wanted_types.get(key, None)
		if overwrite_type:
			wanted_type = overwrite_type

		# apply type transformation
		if wanted_type is None:
			return value

		try:
			return wanted_type(value)
		except Exception as E:
			raise E.__class__(f"Key `{key}` with a value of type {type(value)} could not be transformed to {wanted_type}")

	def getAllTransform(self, include_protected:bool=False, include_undefined:bool=False) -> Any:
		"""
		Same as .getTransform, but returns all `key`, (transformed)`value` pairs
		NOTE: that values that are type UNDEFINED, will also not be added by default
		"""
		transformed:Dict[str, Any] = {}
		for key in self.storage:
			# don't include protected
			if (not include_protected) and (key in self.protected_keys): continue

			# don't include UNDEFINED, Note that None is not UNDEFINED
			if (not include_undefined) and (type(self.storage[key]) is Undefined): continue

			transformed[key] = self.getTransform(key, UNDEFINED)

		return transformed
