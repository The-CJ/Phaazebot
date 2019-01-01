#BASE.modules._Twitch_.Utils

import asyncio, requests, json

MAIN = "https://api.twitch.tv/helix/"

#auth
async def is_Mod(BASE, message):
	if message.mod: return True
	if message.user_type.lower() == "mod": return True
	if message.user_type.lower() == "global_mod": return True
	if message.user_type.lower() == "admin": return True
	if message.user_type.lower() == "staff": return True

	if message.name == message.channel.name: return True

	return False

async def is_Owner(BASE, message):
	if message.user_type.lower() == "admin": return True
	if message.user_type.lower() == "staff": return True

	if message.name == message.channel.name: return True

	return False

async def is_admin(BASE, message):
	if message.user_type.lower() == "admin": return True
	if message.user_type.lower() == "staff": return True

	return False

#channelfiles
async def get_channel_settings(BASE, id, prevent_new=False):
	"""
	Get settings for a channel
	"""
	data = BASE.PhaazeDB.select(of="twitch/channel_settings", where=f"data['channel_id'] == '{str(id)}'", limit=1)

	if len(data['data']) == 0:
		#didn't find entry -> make new
		if prevent_new:
			return None
		else:
			return await make_channel_settings(BASE, id)
	else:
		return data['data'][0]

async def make_channel_settings(BASE, id):
	"""
	create new entry in server file
	"""
	insert_ = dict()

	insert_['channel_id'] = str(id)

	insert_['active_quotes'] = False
	insert_['active_custom'] = True
	insert_['active_games'] = False
	insert_['active_level'] = True

	insert_['ban_links'] = False
	insert_['regulars'] = []
	insert_['link_whitelist'] = []

	insert_['gain_currency'] = 1
	insert_['gain_currency_message'] = 1

	insert_['blacklist'] = []
	insert_['blacklist_punishment'] = 0
	insert_['blacklist_notify'] = True
	insert_['blacklist_message'] = None
	insert_['blacklist_link_message'] = None

	BASE.PhaazeDB.insert(into="twitch/channel_settings", content=insert_)
	BASE.modules.Console.INFO("New Twitch Setting DB entry")

	return insert_

#customfiles
async def get_channel_commands(BASE, id, trigger=None, prevent_new=False):
	"""
	Get custom commands from a channel, if trigger = None, get all
	else only get one associated with trigger
	"""
	l = None
	w = None

	if trigger != None:
		l = 1
		w = f"str(data['trigger']) == str({ json.dumps(trigger) })"

	try:
		data = BASE.PhaazeDB.select(of=f"twitch/commands/commands_{str(id)}", where=w, limit=l)
	except:
		data = dict()

	if data.get('status', 'error') == "error":
		#didn't find entry -> make new
		if prevent_new:
			return None
		else:
			return await make_channel_commands(BASE, id)
	else:
		return data['data']

async def make_channel_commands(BASE, id):
	"""
	Create a new DB container for Twitch commands
	"""
	BASE.PhaazeDB.create(name="twitch/commands/commands_"+str(id))
	BASE.modules.Console.INFO("New Twitch Channel Command DB-Container created")

	return []

#levelfiles
async def get_channel_levels(BASE, id, user_id=None, prevent_new=False):
	"""
	Get server levels, if user_id = None, get all
	else only get one associated with the user_id
	"""

	l = None
	w = None

	if user_id != None:
		l = 1
		w = f"str(data['user_id']) == str({ json.dumps(user_id) })"

	try:
		data = BASE.PhaazeDB.select(of=f"twitch/level/level_{str(id)}", where=w, limit=l)
	except:
		data = dict()

	if data.get('status', 'error') == "error":
		#didn't find entry -> make new
		if prevent_new:
			return None
		else:
			return await make_channel_levels(BASE, id)
	else:
		return data['data']

async def make_channel_levels(BASE, id):
	"""
	Create a new DB container for Twitch level
	"""
	BASE.PhaazeDB.create(name="twitch/level/level_"+str(id))
	BASE.modules.Console.INFO("New Twitch Channel Level DB-Container created")

	return []

#quotefiles
async def get_channel_quotes(BASE, id, prevent_new=False):
	"""
	Get quotes for a channel
	"""
	try:
		data = BASE.PhaazeDB.select(of="twitch/quotes/quotes_"+str(id))
	except:
		data = dict()

	if data.get('status', 'error') == "error":
		#didn't find entry -> make new
		if prevent_new:
			return None
		else:
			return await make_channel_quotes(BASE, id)
	else:
		return data['data']

async def make_channel_quotes(BASE, id):
	"""
	Create a new DB container for Twitch quotes
	"""
	BASE.PhaazeDB.create(name="twitch/quotes/quotes_"+str(id))
	BASE.modules.Console.INFO("New Twitch Quote Level DB-Container created")

	return []

# API #

def API_call(BASE, url):
	#main api call
	key = BASE.access.Twitch_API_Token
	header = {"Client-ID": key}#, "Accept": "application/vnd.twitchtv.v5+json"}
	try:
		resp = requests.get(url, headers = header)
		return resp.json()
	except:
		raise ConnectionError('No Twitch API Response')

def get_user(BASE, twitch_info, search="id"):
	try:

		if type(twitch_info) == str:
			twitch_info = [twitch_info]

		s = "id"
		if search.lower() in ["name", "login"]:
			s = "login"
		elif search.lower() in ["id"]:
			s = "id"

		query = ""
		for thing in twitch_info:
			if query:
				query += f"&{s}={thing}"
			else:
				query += f"?{s}={thing}"

		link = MAIN + "users" + query

		res = API_call(BASE, link)

		result = res.get("data", None)

		#No User
		if result: return result
		else: return None

	except:
		return None

def get_streams(BASE, streams):
	if type(streams) == str:
		streams = [streams]
	try:
		link = MAIN + 'streams?channel=' + ",".join(stream for stream in streams)
		res = API_call(BASE, link)
		return res
	except:
		return None

# Stuff #

def repair_twitch_streams(BASE):
	""" execute to ensure, that every entry in twitch/stream has: twitch_id and twitch_name set. """
	streams = BASE.PhaazeDB.select(of="twitch/stream", where="not ( data.get('twitch_id', False) and data.get('twitch_name', False) )")

	need_name = []
	need_id = []

	for entry in streams['data']:
		if entry.get("twitch_name", None) == None: need_name.append(entry)
		elif entry.get("twitch_id", None) == None: need_id.append(entry)
		else: BASE.modules.Console.INFO("Error for entry "+str(entry))

	twitch_api_name = get_user(BASE, [x.get("twitch_id", "0") for x in need_name], search="id")
	twitch_api_id = get_user(BASE, [x.get("twitch_name", "0") for x in need_id], search="name")

	for nn in twitch_api_name:
		BASE.PhaazeDB.update(of="twitch/stream", content=dict(twitch_name=nn.get("name", None)), where=f"data['twitch_id'] == {json.dumps(nn.get('_id','---'))}")

	for ni in twitch_api_id:
		BASE.PhaazeDB.update(of="twitch/stream", content=dict(twitch_id=ni.get("_id", None)), where=f"data['twitch_name'] == {json.dumps(ni.get('name','---'))}")

	return True
