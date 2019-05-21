from typing import Any

import re

class HTMLFormatter(object):
	""" Loades, contains and manipulates HTML files """
	def __init__(self, path:str = None):
		self.content:str = None
		self.FormatHTMLRegex:re.Pattern = re.compile(r"\|>>>\((.+?)\)<<<\|")
		if path: self.loadHTML(path)

	def setRegex(self, new_re:str) -> None:
		self.FormatHTMLRegex = re.compile(new_re)

	def loadHTML(self, path:str) -> None:
		try:
			self.content = open(path, 'r').read()
		except FileNotFoundError:
			raise FileNotFoundError(f"Could not find: {path}")
		except Exception as e:
			raise Exception("HTMLFormatter raised unknown error: "+str(e))

	def replace(self, replace_empty:bool=False, **values:Any) -> None:
		"""
		This function will take all
		|>>>(kwarg)<<<|   (or other re set by self.setRegex)
		in self.content, and replace kwarg with the right key match from **values
		else empty string if replace_empty is True

		returns formated html
		"""
		search_results:re.Match = re.finditer(self.FormatHTMLRegex, self.content)
		for hit in search_results:
			replacement:Any = values.get(hit.group(1), None)
			if replacement == None and replace_empty == False: continue

			self.content = self.content.replace(
				hit.group(0),
				str(replacement if replacement else "")
			)
