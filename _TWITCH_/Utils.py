#BASE.moduls._Twitch_.Utils

import asyncio, json, requests

MAIN = "https://api.twitch.tv/kraken/"

#settings
async def get_twitch_file(BASE, room_id):
	#has file in lib
	if hasattr(BASE.twitchfiles, "channel_"+room_id):
		file = getattr(BASE.twitchfiles, "channel_"+room_id)
		return file

	try:
		file = open("_TWITCH_/Channel_files/{0}.json".format(room_id), "r")
		file = file.read()
		file = json.loads(file)

		#add to lib
		setattr(BASE.twitchfiles, "channel_"+room_id, file)

		return file

	#none found, make new
	except FileNotFoundError:

		file = await make_twitch_file(BASE, room_id)
		return file

	#json bullsahit
	except json.decoder.JSONDecodeError:
		BASE.moduls.Console.RED("CRITICAL ERROR", "Broken json twitch channel file")

	#something new
	except Exception as e:
		print(str(e.__class__) + "in File")

async def make_twitch_file(BASE, room_id):
	struktur = {"room_id": room_id}
	with open("_TWITCH_/Channel_files/{0}.json".format(room_id), "w") as new:
		json.dump(struktur, new)

	BASE.moduls.Console.CYAN("INFO", "New Twitch Channel created")

	file = open("_TWITCH_/Channel_files/{0}.json".format(room_id), "r")
	file = file.read()
	file = json.loads(file)

	return file

#level
async def get_twitch_level_file_(BASE, room_id):
	#has file in lib
	if hasattr(BASE.twitchlevelfiles, "channel_"+room_id):
		file = getattr(BASE.twitchlevelfiles, "channel_"+room_id)
		return file

	try:
		file = open("_TWITCH_/Channel_level_files/{0}.json".format(room_id), "r")
		file = file.read()
		file = json.loads(file)

		#add to lib
		setattr(BASE.twitchlevelfiles, "channel_"+room_id, file)

		return file

	#none found, make new
	except FileNotFoundError:

		file = await make_twitch_level_file(BASE, room_id)
		return file

	#json bullsahit
	except json.decoder.JSONDecodeError:
		BASE.moduls.Console.RED("CRITICAL ERROR", "Broken json twitch level file")

	#something new
	except Exception as e:
		print(str(e.__class__) + "in Level")
#level
async def get_twitch_level_file(BASE, room_id):
	#has file in lib
	if hasattr(BASE.twitchlevelfiles, "channel_"+room_id):
		file = getattr(BASE.twitchlevelfiles, "channel_"+room_id)
		return file

	try:
		file = open("_TWITCH_/Channel_level_files/{0}.json".format(room_id), "r")
		file = file.read()
		file = json.loads(file)

		#add to lib
		setattr(BASE.twitchlevelfiles, "channel_"+room_id, file)

		return file

	#none found, make new
	except FileNotFoundError:

		file = await make_twitch_level_file(BASE, room_id)
		return file

	#json bullsahit
	except json.decoder.JSONDecodeError:
		BASE.moduls.Console.RED("CRITICAL ERROR", "Broken json twitch level file")

async def make_twitch_level_file(BASE, room_id):
	struktur = {"room_id": room_id, "user": []}
	with open("_TWITCH_/Channel_level_files/{0}.json".format(room_id), "w") as new:
		json.dump(struktur, new)

	BASE.moduls.Console.CYAN("INFO", "New Twitch Level created")

	file = open("_TWITCH_/Channel_level_files/{0}.json".format(room_id), "r")
	file = file.read()
	file = json.loads(file)

	return file

#channel objects
async def get_channel_object(BASE, id=None, name=None):
	found = None

	if id != None:
		for channel in BASE.Twitch_IRC_connection.channels:
			if channel.room_id == id:
				return channel

	if name != None:
		for channel in BASE.Twitch_IRC_connection.channels:
			if channel.name.lower() == name.lower():
				return channel
	return found

# # #

def API_call(BASE, url):
	key = BASE.access.Twitch_API_Token
	header = {"Client-ID": key, "Accept": "application/vnd.twitchtv.v5+json"}
	try:
		resp = requests.get(url, headers = header)
		return resp.json()
	except:
		raise ConnectionError('No Twitch API Response')

def get_user(BASE, twitch_info, search="id"):
	try:
		if search == "id":
			s = "users/"
			link = MAIN + s + twitch_info
			res = API_call(BASE, link)
			return res

		elif search == "name":
			s = "users?login="
			link = MAIN + s + twitch_info
			res = API_call(BASE, link)

			#No User
			if res.get("_total", 0) != 1: return None

			return res["users"][0]

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
