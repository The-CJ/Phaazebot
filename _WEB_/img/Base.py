import json, mimetypes, io
from PIL import Image

# BASE.modules._Web_.Base.root.web.img
# /img/{file}
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
	path_str = f"{self.root.BASE.vars.IMAGE_PATH}{file_name}"
	path_str = path_str.replace('..','')

	# open file
	try:
		#img_file = Image.open(path_str)
		img_file = open(path_str, "rb")
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
	#finished_image = None
	#defaultX, defaultY = img_file.size
	#sizeX = int(request.query.get("sizeX", defaultX )) if request.query.get("sizeX", str(defaultX) ).isdigit() else defaultX
	#sizeY = int(request.query.get("sizeY", defaultY )) if request.query.get("sizeY", str(defaultY) ).isdigit() else defaultY
	#finished_image = img_file.resize((sizeX, sizeY))

	#bio = io.BytesIO()
	#finished_image.save(bio)

	return self.root.response(
		status=200,
		content_type=content_type[0],
		body=img_file
	)
