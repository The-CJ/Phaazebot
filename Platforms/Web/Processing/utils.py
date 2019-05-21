from typing import TYPE_CHECKING, Any
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex

import re

def formatHtml(self:"WebIndex", html_string:str, **values:Any) -> str:
	"""
	This function will take all
	|>>>(kwarg)<<<|
	in the html_string, and replace kwarg with the right key match from **values
	else empty string

	returns formated html
	"""
	search_results:re.Match = re.finditer(self.FormatHTMLRegex, html_string)
	for hit in search_results:
		html_string = html_string.replace(
			hit.group(0),
			str( values.get(hit.group(1), "") )
		)

	return html_string
