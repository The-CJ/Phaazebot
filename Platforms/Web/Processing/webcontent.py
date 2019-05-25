# error handling
async def noFileDefined(cls:"WebIndex") -> Response:
	return cls.response(
		status=400,
		content_type='application/json',
		body=json.dumps( dict( error="no_file_defined",status=400 ) )
	)

async def fileNotFound(cls:"WebIndex") -> Response:
	return cls.response(
		status=400,
		content_type='application/json',
		body=json.dumps( dict( error="file_not_found",status=400 ) )
	)
