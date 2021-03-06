from typing import Any, Iterator

import re

class HTMLFormatter(object):
	"""
	Loads, contains and manipulates HTML files
	if template == True, the content can only be loaded initially and won't be changed by replace
	"""
	def __str__(self) -> str:
		return self.content

	def __repr__(self) -> str:
		return f"<{self.__class__.__name__} from file: {self.path}>"

	def __init__(self, path:str = None, template:bool = False, decoding:str = "UTF-8"):
		self.content:str = ""
		self.path:str = path
		self.template:bool = template
		self.decoding:str = decoding
		self.FormatHTMLRegex:"re.Pattern" = re.compile(r"\|<!--#\((.+?)\)#-->\|")
		if self.path: self.loadHTML(self.path)

	def setRegex(self, new_re:str) -> None:
		self.FormatHTMLRegex = re.compile(new_re)

	def loadHTML(self, path:str) -> None:
		try:
			self.path = path
			self.content = open(self.path, 'rb').read().decode(self.decoding)
		except FileNotFoundError:
			raise FileNotFoundError(f"Could not find: {path}")
		except Exception as e:
			raise Exception("HTMLFormatter raised unknown error: "+str(e))

	def replace(self, replace_empty:bool=False, **values) -> str:
		"""
			This function will take all
			|<!--#(kwarg)#-->| (or other re set by self.setRegex)
			in self.content, and replace kwarg with the right key match from **values
			else empty string if replace_empty is True

			returns formatted html
		"""
		temp:str = self.content
		search_results:Iterator[re.Match] = re.finditer(self.FormatHTMLRegex, self.content)
		for Hit in search_results:
			replacement:Any = values.get(Hit.group(1), None)
			if replacement is None and not replace_empty: continue

			temp = temp.replace(
				Hit.group(0),
				str(replacement if replacement else "")
			)
		if not self.template: self.content = temp
		return temp
