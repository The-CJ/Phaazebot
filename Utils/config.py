import json
import traceback
from Utils.cli import CliArgs
from typing import Any
from Utils.Classes.undefined import Undefined

class ConfigParser(object):
	""" used to load programm configs from file """
	def __init__(self, file_path:str="config.json", file_type:str="json"):
		self.content:dict = dict()
		self.file_type:str = file_type
		self.file_path:str = file_path

		if not CliArgs.get("no-args"):
			if self.file_type == "json":
				self.loadJSON()
			else:
				pass

			if self.content == None:
				print("Config > missing configuration")
				print("Phaazebot not started, start without configs, add -no-args")
				exit(2)

	def get(self, *arg) -> Any:
		if not arg:
			return self.content
		else:
			if len(arg) > 1: return self.content.get(arg[0], arg[1])
			else: return self.content.get(arg[0], Undefined())

	def loadJSON(self) -> None:
		try:
			self.content = json.loads( open(self.file_path, "rb").read() )
		except FileNotFoundError:
			print(f"Config > could not find: '{self.file_path}'")
			self.content = None
		except json.decoder.JSONDecodeError:
			print(f"Config > json could not load: '{self.file_path}'")
			self.content = None
		except Exception as e:
			print(f'Config > unknown error: {str(e)}')
			traceback.print_exc()
			self.content = None
