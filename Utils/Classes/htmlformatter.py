from typing import Any

import re

class HTMLFormatter(object):
	"""
		Loades, contains and manipulates HTML files
		if template == True, the content can only be loaded initially and won't be changed by replace
	"""
	def __str__(self) -> str:
		return self.content

	def __repr__(self) -> str:
		return f"<{self.__class__.__name__} from file: {self.path}>"

	def __init__(self, path:str = None, template:bool=False):
		self.content:str = None
		self.path:str = path
		self.template:bool=template
		self.FormatHTMLRegex:"re.Pattern" = re.compile(r"\|<!--#\((.+?)\)#-->\|")
		if self.path: self.loadHTML(self.path)

	def setRegex(self, new_re:str) -> None:
		self.FormatHTMLRegex = re.compile(new_re)

	def loadHTML(self, path:str) -> None:
		try:
			self.path = path
			self.content = open(self.path, 'r').read()
		except FileNotFoundError:
			raise FileNotFoundError(f"Could not find: {path}")
		except Exception as e:
			raise Exception("HTMLFormatter raised unknown error: "+str(e))

	def replace(self, replace_empty:bool=False, **values:dict) -> str:
		"""
			This function will take all
			|<!--#(kwarg)#-->|   (or other re set by self.setRegex)
			in self.content, and replace kwarg with the right key match from **values
			else empty string if replace_empty is True

			returns formated html
		"""
		temp:str = self.content
		search_results:re.Match = re.finditer(self.FormatHTMLRegex, self.content)
		for hit in search_results:
			replacement:Any = values.get(hit.group(1), None)
			if replacement == None and replace_empty == False: continue

			temp = temp.replace(
				hit.group(0),
				str(replacement if replacement else "")
			)
		if not self.template: self.content = temp
		return temp
