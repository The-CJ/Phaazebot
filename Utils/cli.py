import sys, re
from typing import Any
from Utils.Classes.undefined import Undefined


class CliArgs(object):
	"""Contains arguments added by programm start """
	def __init__(self):
		self.args:dict = dict()

		arg_re = re.compile(r'^-(.+?)$')
		kwarg_re = re.compile(r'^--(.+?)=(.*)$')

		for arg in sys.argv[1:]:

			arg_res = arg_re.match(arg)
			if arg_res != None:
				self.args[arg_res.group(1)] = True
				continue

			kwarg_res = kwarg_re.match(arg)
			if kwarg_res != None:
				self.args[kwarg_res.group(1)] = kwarg_res.group(2)
				continue

	def get(self, *arg) -> Any:
		if len(arg) == 0:
			return self.args
		else:
			if len(arg) > 1: return self.args.get(arg[0], arg[1])
			else: return self.args.get(arg[0], Undefined())

CliArgs = CliArgs()
