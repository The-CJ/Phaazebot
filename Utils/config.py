import json
import phzcf
import traceback
from typing import Any, Dict
from Utils.cli import CliArgs
from Utils.Classes.undefined import UNDEFINED

class ConfigParser(object):
	"""
	This class is support to provide a raw access point for configuration data.
	There are multiple ways to load config in this class, from there, all other Sub-Config classes that info from here
	"""
	def __init__(self, file_path:str="Config/config.phzcf", file_type:str="phzcf"):
		self.loaded:bool = False
		self.content:Dict[str, Any] = {}
		self.file_type:str = file_type
		self.file_path:str = file_path

		if not CliArgs.get("no-args"):

			self.load()

			if not self.content:
				print("Config > missing configuration")
				print("Phaazebot not started, to start without configs add '-no-args'")
				exit(2)

	def get(self, arg:str, alt:Any=UNDEFINED) -> Any:
		return self.content.get(arg, alt)

	def load(self, redo:bool=False) -> None:

		if self.loaded and not redo: raise RuntimeWarning("Configs already loaded")

		try:

			file_content:bytes = open(self.file_path, "rb").read()
			if self.file_type == "phzcf":
				self.loadPHZCF(file_content)
			elif self.file_type == "json":
				self.loadJSON(file_content)
			else:
				raise AttributeError("invalid `file_type`")

		except FileNotFoundError:
			print(f"Config > could not find: '{self.file_path}'")
		except json.decoder.JSONDecodeError:
			print(f"Config > json could not load: '{self.file_path}'")
		except Exception as E:
			print(f'Config > unknown error: {str(E)}')
			traceback.print_exc()

	def loadPHZCF(self, content:bytes) -> None:
		self.content = phzcf.load(content)

	def loadJSON(self, content:bytes) -> None:
		self.content = json.loads(content)
