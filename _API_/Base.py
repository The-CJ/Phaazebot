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

async def games_webosu(self, request, **kwargs):
	if request.method == "GET":
		state = request.query.get('story', 'False')
		state = "true" if state == "True" else "false"
		str_ = f"data['story'] == '{state}'"
		all_records = self.root.BASE.PhaazeDB.select(of='game/webosu', where=str_)
		return self.root.response(
			text=json.dumps( dict(status=200,data=all_records['data']) ),
			content_type="application/json",
			headers={'Access-Control-Allow-Origin':'*'},
			status=200
		)
	if request.method == "POST":

		_POST = await request.post()
		data = dict(
			name = _POST.get('name', None),
			score = _POST.get('score', None),
			story = _POST.get('story', None),
			story_diff = _POST.get('story_diff', None),
			ar = _POST.get('ar', None),
			cs = _POST.get('cs', None),
			od = _POST.get('od', None),
			hp = _POST.get('hp', None),
			multiplyer = _POST.get('multiplyer', None),
			count_hit = _POST.get('count_hit', None),
			count_fail = _POST.get('count_fail', None),
			highest_combo = _POST.get('highest_combo', None),
		)

		if any( [x == None for x in data] ):
			return self.root.response(
				text=json.dumps( dict(status=400,error='no_content_can_be_none') ),
				content_type="application/json",
				headers={'Access-Control-Allow-Origin':'*'},
				status=400
			)

		add_record = self.root.BASE.PhaazeDB.insert(into='game/webosu',content=data)

		return self.root.response(
			headers={'Access-Control-Allow-Origin':'*'},
			status=204
		)
