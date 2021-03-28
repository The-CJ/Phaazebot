import sys
import re

class CliArgsClass(object):
	"""Contains arguments added by program start """
	def __init__(self):
		self.args:dict = dict()

		ArgRE:"re.Pattern" = re.compile(r'^-(.+?)$')
		KWargRE:"re.Pattern" = re.compile(r'^--(.+?)=(.*)$')

		for arg in sys.argv[1:]:

			KWargRes:"re.Match" = KWargRE.match(arg)
			if KWargRes is not None:
				self.args[KWargRes.group(1)] = KWargRes.group(2)
				continue

			ArgRes:"re.Match" = ArgRE.match(arg)
			if ArgRes is not None:
				self.args[ArgRes.group(1)] = True
				continue

	def get(self, arg:str, alt:str=None) -> str:
		return self.args.get(arg, alt)


CliArgs:CliArgsClass = CliArgsClass()
