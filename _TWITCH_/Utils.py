#BASE.moduls._Twitch_.Utils

import asyncio, json

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

#debug
async def debug(BASE, message):
	m = message.content.split(" ")

	if message.content.startswith("!!!!!debug++"):
		return await BASE.Twitch_IRC_connection.send_message(message.channel, "Unknown Operations")

	elif message.content.startswith("!!!!!debug+"):
		if len(m) == 1:
			return await BASE.Twitch_IRC_connection.send_message(message.channel, "Missing Operations")
		try:
			f = await eval(" ".join(tt for tt in m[1:]))
			await BASE.Twitch_IRC_connection.send_message(message.channel, str(f))
		except Exception as Fail:
			await BASE.Twitch_IRC_connection.send_message(message.channel, "ERROR: " + str(Fail))

	elif message.content.startswith("!!!!!debug"):
		if len(m) == 1:
			return await BASE.Twitch_IRC_connection.send_message(message.channel, "Missing Operations")
		try:
			f = eval(" ".join(tt for tt in m[1:]))
			await BASE.Twitch_IRC_connection.send_message(message.channel, str(f))
		except Exception as Fail:
			await BASE.Twitch_IRC_connection.send_message(message.channel, "ERROR: " + str(Fail))

	elif message.content.startswith("!!!!!reload"):
		try:
			await BASE.Twitch_IRC_connection.send_message(message.channel, "imGlitch Reloading PhaazeOS Infobase...")
			BASE.queue.TO_DISCORD_T.put_nowait(BASE.moduls.Utils.reload_(BASE))
			await asyncio.sleep(3)
			await BASE.Twitch_IRC_connection.send_message(message.channel, "SeemsGood Reload successfull.")
		except Exception as Fail:
			await BASE.Twitch_IRC_connection.send_message(message.channel, "panicBasket : Database is corrupted! Keeping old Database alive")

async def get_opposite_osu_twitch(BASE, search_term, platform=None):
	if platform == None or platform not in ["twitch", "osu"]:
		return

	file = json.loads(open("DATABASE/osu_twitch.json").read())

	for data_object in file["objects"]:

		if platform == "twitch":
			if str(data_object["twitch"]["id"]) == str(search_term):
				return data_object

		if platform == "osu":
			if data_object["osu"]["name"].lower() == search_term.lower():
				return data_object

	return None

async def delete_verify(BASE, search_term, platform="twitch"):
	file = json.loads(open("DATABASE/osu_twitch.json").read())

	for data_object in file["objects"]:

		if platform == "twitch":
			if str(data_object["twitch"]["id"]) == str(search_term):
				file["objects"].remove(data_object)

		if platform == "osu":
			if data_object["osu"]["name"].lower() == search_term.lower():
				file["objects"].remove(data_object)

		with open("DATABASE/osu_twitch.json", "w") as save:
			json.dump(file, save)
