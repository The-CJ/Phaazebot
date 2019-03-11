import json, mimetypes

#BASE.modules._Web_.Base.root.web.img
async def main(self, request):

	file_name = request.match_info.get('file', None)

	# no file define
	if file_name == None or file_name == "":
		return self.root.response(
			status=400,
			content_type='application/json',
			text=json.dumps( dict( error="no_file_defined",status=400 ) )
		)
	file_name = file_name.strip('/')
	path_str = f"_WEB_/img/{file_name}"
	path_str = path_str.replace('..','')

	# open file
	try:
		img_file = open(path_str, 'rb').read()
	except Exception as e:
		self.root.BASE.modules.Console.DEBUG(f"Exception in file open: {str(e)}", require="web:img")
		img_file = None

	# no file found
	if img_file == None:
		return self.root.response(
			status=400,
			content_type='application/json',
			text=json.dumps( dict( error="file_not_found",status=400,file=file_name ) )
		)

	content_type = mimetypes.guess_type(path_str, strict=True)
	# file found -> return
	return self.root.response(
		status=200,
		content_type=content_type[0],
		body=img_file
	)
