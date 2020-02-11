import logging
import os
import sys
import inspect
from Utils.cli import CliArgs
try: from cysystemd.journal import JournaldLogHandler
except ImportError:	pass

class PhaazeLoggerFormatter(logging.Formatter):
	""" custom logging colors """
	default_color:str = "\033[00m"
	colors:dict = dict(
		DEBUG = "\033[90m",
		INFO = "\033[36m",
		WARNING = "\033[93m",
		ERROR = "\033[33m",
		CRITICAL = "\033[31m",
	)

	def formatMessage(self, Record:logging.LogRecord) -> None:
		lvl:str = Record.levelname
		wanted_color:str = self.colors.get(lvl, self.default_color)
		Record.levelname = f"{wanted_color}{lvl}{self.default_color}"
		return self._style.format(Record)

class PhaazeLogger(object):
	""" Logger for project, sends to systemd or console """
	def __init__(self):
		self.Log:logging.Logger = logging.getLogger("Phaazebot")
		self.Log.setLevel(logging.DEBUG)
		self.Formatter:PhaazeLoggerFormatter = PhaazeLoggerFormatter("[%(levelname)s]: %(message)s")
		self.active_debugs:list = [a.lower() for a in CliArgs.get("debug", "").split(",")]

		self.logging_type:str = CliArgs.get("logging" , "console")

		if self.logging_type in ["systemd", "cysystemd"] and "cysystemd" in sys.modules:
			# TODO: rework this
			JH = JournaldLogHandler()
			JH.setFormatter(self.Formatter)
			self.Log.addHandler(JH)

		elif self.logging_type == "console":
			PhaazeStreamHandler:logging.StreamHandler = logging.StreamHandler()
			PhaazeStreamHandler.setFormatter(self.Formatter)
			self.Log.addHandler(PhaazeStreamHandler)

		else:
			pass

	def info(self, msg:str) -> None:
		self.Log.info(msg)

	def warning(self, msg:str) -> None:
		self.Log.warning(msg)

	def error(self, msg:str) -> None:
		self.Log.error(msg)

	def critical(self, msg:str) -> None:
		self.Log.critical(msg)

	def debug(self, msg:str, require:str="all") -> None:
		show:bool = False
		if require == "": show = True
		
		for ad in self.active_debugs:
			if ad == "all": show = True; break
			if require == ad: show = True; break
			if require.split(":")[0] == ad: show = True; break

		if show:
			# Caller tracks back the command that called this function,
			# i only take the line, and the file in which it happen
			Caller:inspect.Traceback = inspect.getframeinfo(inspect.stack()[1][0])
			location:str = Caller.filename.replace(os.getcwd(), "")

			self.Log.debug(f"{location}:{Caller.lineno} | {msg}")

	def printSQL(self, statement:str) -> None:
		"""
			pretty prints a sql statement
			(i like using tabs, so that should remove them before printing,
			so you dont have to watch disorderd stairs)
		"""
		# just remove leading whitespaces and put back together
		statement = '\n'.join([ l.lstrip("\t") for l in statement.splitlines() ])
		self.debug(f"{'+'*10}\n{statement}\n{'-'*10}", require="")
