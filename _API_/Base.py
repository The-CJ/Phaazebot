import asyncio
import json

# /api/?
async def unknown(self, request, **kwargs):
	return self.root.response(
		text=json.dumps( dict(error="unknown_api",status=404) ),
		content_type="application/json",
		status=404
	)

# /api
async def nothing(self, request, **kwargs):
	return self.root.response(
		text=json.dumps( dict(error="no_path",status=400,message="Trying to find out the PhaazeAPI?. Try looking at phaaze.net/wiki/api") ),
		content_type="application/json",
		status=400
	)

# <403><401><404>
async def action_not_allowed(self, request, msg="Not allowed"):
	return self.root.response(
		text=json.dumps( dict(error="action_not_allowed",status=403,msg=msg) ),
		content_type="application/json",
		status=403
	)
