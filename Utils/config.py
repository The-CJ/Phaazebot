import re
import json
import traceback
from typing import Any, Dict
from Utils.cli import CliArgs
from Utils.Classes.undefined import UNDEFINED

class ConfigParser(object):
	"""
	This class is suppost to provide a raw accesspoint for configuration data.
	There are multiple ways to load config in this class, from there, all other Sub-Config classes that info from here
	"""
	def __init__(self, file_path:str="config.phzcf", file_type:str="phzcf"):
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
		# loose code for now, maybe i make a own lib or so

		Struc:"re.Pattern" = re.compile(r"^\[(.+)\].*?=(.*)$")

		line:bytes
		for line in content.splitlines():
			# strip
			line = line.strip(b' ').strip(b'\t')
			line:str = line.decode("UTF-8")

			# ignore empty lines
			if not line: continue

			# ignore comments
			if line[0] == '#': continue

			Found:re.Match = re.search(Struc, line)
			if Found:
				var_name:str = Found.group(1)
				var_value:str = Found.group(2).strip(' ')

				var_value:Any = json.loads(var_value)

				self.content[var_name] = var_value

	def loadJSON(self, content:bytes) -> None:
		self.content = json.loads( content )
