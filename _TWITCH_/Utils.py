#BASE.modules._Twitch_.Utils

import asyncio, requests

MAIN = "https://api.twitch.tv/kraken/"

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
	#get
	data = BASE.PhaazeDB.select(of="twitch/channel_settings", where=f"data['channel_id'] == '{str(id)}'")

	if len(data['data']) == 0:
		#didn't find entry -> make new
		if prevent_new:
			return None
		else:
			return await make_channel_settings(BASE, id)
	else:
		return data['data'][0]

async def make_channel_settings(BASE, id):
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
async def get_channel_commands(BASE, id, prevent_new=False):
	#get
	try:
		data = BASE.PhaazeDB.select(of="twitch/commands/commands_"+str(id))
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

	BASE.PhaazeDB.create(name="twitch/commands/commands_"+str(id))
	BASE.modules.Console.INFO("New Twitch Channel Command DB-Container created")

	return []

#levelfiles
async def get_channel_levels(BASE, id, prevent_new=False):
	#get
	try:
		data = BASE.PhaazeDB.select(of="twitch/level/level_"+str(id))
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

	BASE.PhaazeDB.create(name="twitch/level/level_"+str(id))
	BASE.modules.Console.INFO("New Twitch Channel Level DB-Container created")

	return []

#quotefiles
async def get_channel_quotes(BASE, id, prevent_new=False):
	#get
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

	BASE.PhaazeDB.create(name="twitch/quotes/quotes_"+str(id))
	BASE.modules.Console.INFO("New Twitch Quote Level DB-Container created")

	return []

# # #

def API_call(BASE, url):
	#main api call
	key = BASE.access.Twitch_API_Token
	header = {"Client-ID": key, "Accept": "application/vnd.twitchtv.v5+json"}
	try:
		resp = requests.get(url, headers = header)
		return resp.json()
	except:
		raise ConnectionError('No Twitch API Response')

def get_user(BASE, twitch_info, search="id"):
	try:

		if type(twitch_info) == str:
			twitch_info = [twitch_info]

		s = "/"
		if search == "name":
			s = "?login="
		elif search == "id":
			s = "?id="

		link = MAIN + "users" + s + ",".join(thing for thing in twitch_info)

		res = API_call(BASE, link)

		#No User
		if res.get("_total", 0) == 0: return None

		return res["users"]

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
