# BASE.modules._Twitch_.PROCESS.Owner

import asyncio, json

class Everything(object):

	async def join(BASE, message, kwargs):

		#admin override
		if await BASE.modules._Twitch_.Utils.is_admin(BASE, message):
			m = message.content[len(BASE.vars.TRIGGER_TWITCH):].split(' ')
			if len(m) > 1:
				name = " ".join(m[1:])
				user = BASE.modules._Twitch_.Utils.get_user(BASE, name.lower(), search="name")
				if len(user) <= 1:
					user = user[0]
				else:
					return await BASE.twitch.send_message(message.channel_name, f'@{message.display_name} > Override >> No channel found. "{name}"')

				check = BASE.modules._Twitch_.Streams.Main.get_stream(user["id"])

				if check != None and check.get("chat_managed", False):
					return await BASE.twitch.send_message(
						message.channel_name,
						f'@{message.display_name} > Override >> Phaaze already is in channel: {user["display_name"]}'
					)
				else:
					success = BASE.modules._Twitch_.Streams.Main.set_stream(user["id"], chat_managed=True, twitch_name=user["name"])
					if success != False:
						await BASE.twitch.join_channel(user['name'])
						return await BASE.twitch.send_message(
							message.channel_name,
							f'@{message.display_name} > Override >> Phaaze successfull joined "{user["display_name"]}"')
					else:
						return await BASE.twitch.send_message(message.channel_name, f'@{message.display_name} > Something went wrong, try again or contact the developer.')

		#check if not already in
		check = BASE.modules._Twitch_.Streams.Main.get_stream(message.user_id)
		if check != None and check.get("chat_managed", False):
			return await BASE.twitch.send_message(message.channel_name, f'@{message.display_name} > Phaaze already is in your channel')

		#it's not in -> add it
		else :
			success = BASE.modules._Twitch_.Streams.Main.set_stream(message.user_id, chat_managed=True, twitch_name=message.name)
			if success != False:
				await BASE.twitch.join_channel(message.name)
				return await BASE.twitch.send_message(message.channel_name, f'@{message.display_name} > Phaaze successfull joined your channel!')
			else:
				return await BASE.twitch.send_message(message.channel_name, f'@{message.display_name} > Something went wrong, try again or contact the developer.')

	async def leave(BASE, message, kwargs):
		#check if in
		check = BASE.modules._Twitch_.Streams.Main.get_stream(message.user_id)

		if check == None or not check.get("chat_managed", False):
			return await BASE.twitch.send_message(message.channel_name, f'@{message.display_name} > Phaaze is not in your channel')

		success = BASE.modules._Twitch_.Streams.Main.set_stream(message.user_id, chat_managed=False, twitch_name=message.name)
		if success != False:
			await BASE.twitch.part_channel(message.name)
			return await BASE.twitch.send_message(message.channel_name, f'@{message.display_name} > Phaaze successfull left your channel! :c')
		else:
			return await BASE.twitch.send_message(message.channel_name, f'@{message.display_name} > Something went wrong, try again or contact the developer.')

class OsuLink(object):

	in_linking_process = []

	class Linking_Object(object):
		def __init__(self, BASE, tw_id, tw_name, osu_acc):
			self.BASE = BASE
			self.twitch_id = tw_id
			self.twitch_name = tw_name
			self.osu_name = osu_acc
			self.pairing_code = BASE.modules.Utils.random_string(size=6)
			self.time_left = 300
			self.success = False

		def activate(self):
			if self.success: return

			tw_m = self.BASE.twitch.send_message(self.twitch_name, f"Link complete! You linked the osu! account '{self.osu_name.lower()}'")
			osu_m = self.BASE.osu.send_pm(self.osu_name, f"Link complete! You linked the twitch channel '{self.twitch_name.lower()}'")

			asyncio.ensure_future( tw_m, loop=self.BASE.Twitch_loop )
			asyncio.ensure_future( osu_m, loop=self.BASE.Osu_loop )

			self.BASE.PhaazeDB.update(
				of="twitch/channel_settings",
				content=dict(linked_osu_account=self.osu_name),
				where=f"data['channel_id'] == {json.dumps(self.twitch_id)}"
			)

			self.success = True

		async def start_timer(self):
			OsuLink.in_linking_process.append(self)
			while True:
				await asyncio.sleep(1)
				self.time_left -= 1
				if self.time_left <= 0 or self.success:
					break
			OsuLink.in_linking_process.remove(self) # no time left, remove pair object

	async def Base(BASE, message, kwargs):
		m = message.content[len(BASE.vars.TRIGGER_TWITCH):].split(' ')

		channel_settings = kwargs.get('channel_settings', None)
		if channel_settings == None:
			channel_settings = await BASE.modules._Twitch_.Utils.get_channel_settings(BASE, message.channel_id)

		linked_osu_account = channel_settings.get('linked_osu_account', None)

		#give instructions
		if len(m) == 1 and linked_osu_account == None:
			return await BASE.twitch.send_message(
				message.channel_name,
				f"To link your Twitch channel with a osu! account, type: {BASE.vars.TRIGGER_TWITCH}osulink [Your osu! account name]"
			)

		#get current info
		elif len(m) == 1 and linked_osu_account != None:
			return await BASE.twitch.send_message(
				message.channel_name,
				f"Your Twitch channel is currently linked with the osu! account: {linked_osu_account.lower()}, you can type: '{BASE.vars.TRIGGER_TWITCH}osulink unlink' to remove it")

		#start new link
		elif len(m) >= 2 and linked_osu_account == None:
			osu_name = " ".join(m[1:])
			return await OsuLink.startlink(BASE, message, kwargs, osu_name)

		#unlink
		elif linked_osu_account != None and m[1].lower() == "unlink":
			return await OsuLink.unlink(BASE, message, kwargs)

		else: # m[1] != "unlinked" and linked_osu_account
			return await BASE.twitch.send_message(
				message.channel_name,
				f"You are already linked with '{linked_osu_account.lower()}', you cannot link your twitch account with another osu account. Use '{BASE.vars.TRIGGER_TWITCH}osulink unlink' first"
			)

	async def startlink(BASE, message, kwargs, osu_account):

		# check if allready in progress
		for Link_O in OsuLink.in_linking_process:
			if message.channel_id == Link_O.twitch_id:
				return await BASE.twitch.send_message(
					message.channel_name,
					f"You are already in a pairing process, you have {Link_O.time_left}s left to send a ingame message to 'Phaazebot': '{BASE.vars.TRIGGER_OSU}twitchverify {Link_O.pairing_code}'"
				)

		Pair_Object = OsuLink.Linking_Object(BASE, message.channel_id, message.channel_name, osu_account)
		asyncio.ensure_future(Pair_Object.start_timer(), loop=BASE.Worker_loop)

		return await BASE.twitch.send_message(
			message.channel_name,
			f"Link Pending! Go to your osu! ingame chat and write a message to 'Phaazebot'. You have 5min to say '{BASE.vars.TRIGGER_OSU}twitchverify {Pair_Object.pairing_code}'"
		)

	async def unlink(BASE, message, kwargs):
		BASE.PhaazeDB.update(
			of="twitch/channel_settings",
			content=dict( linked_osu_account=None ),
			where=f"data['channel_id'] == {json.dumps(message.channel_id)}"
		)
		return await BASE.twitch.send_message(
			message.channel_name,
			f"Your osu! account got successfull unlinked."
		)


