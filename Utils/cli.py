import sys
import re
from Utils.Classes.undefined import UNDEFINED

class CliArgs(object):
	"""Contains arguments added by programm start """
	def __init__(self):
		self.args:dict = dict()

		ArgRE:"re.Pattern" = re.compile(r'^-(.+?)$')
		KWargRE:"re.Pattern" = re.compile(r'^--(.+?)=(.*)$')

		for arg in sys.argv[1:]:

			KWargRes:"re.Match" = KWargRE.match(arg)
			if KWargRes != None:
				self.args[KWargRes.group(1)] = KWargRes.group(2)
				continue

			ArgRes:"re.Match" = ArgRE.match(arg)
			if ArgRes != None:
				self.args[ArgRes.group(1)] = True
				continue

	def get(self, arg:str, alt:str=None) -> str:
		return self.args.get(arg, alt)

	def pos(self, i:int) -> str:
		try:
			return sys.argv[i]
		except:
			return UNDEFINED

CliArgs = CliArgs()
