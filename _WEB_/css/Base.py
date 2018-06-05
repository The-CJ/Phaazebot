
import json

#BASE.modules._Web_.Base.root.css
def main(self, request):

	file_name = request.match_info.get('file', None)

	# no file define
	if file_name == None or file_name == "":
		return self.response(
			status=400,
			content_type='application/json',
			text=json.dumps( dict( error="no_file_defined",status=400 ) )
		)
	file_name = file_name.strip('/')
	path_str = f"_WEB_/css/{file_name}"
	path_str = path_str.replace('..','')

	# tryed to get a non .css
	if not path_str.endswith(".css"):
		return self.response(
			status=403,
			content_type='application/json',
			text=json.dumps( dict( error="not_allowed",status=403 ) )
		)

	# open file
	try:
		css_file = open(path_str, 'rb').read()
	except Exception as e:
		css_file = None

	# no file found
	if css_file == None:
		return self.response(
			status=400,
			content_type='application/json',
			text=json.dumps( dict( error="file_not_found",status=400,file=file_name ) )
		)

	# file found -> return
	return self.response(
		status=200,
		content_type='text/css',
		body=css_file
	)
