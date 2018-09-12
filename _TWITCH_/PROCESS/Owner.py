# BASE.modules._Twitch_.PROCESS.Owner

import asyncio

class Everything(object):

	async def join(BASE, message, kwargs):

		#admin override
		if await BASE.modules._Twitch_.Utils.is_admin(BASE, message):
			m = message.content.split(' ')
			if len(m) > 1:
				n = " ".join(f for f in m[1:])
				check = BASE.PhaazeDB.select(of='setting/twitch_channel', where=f"str(data['twitch_name']) == str('{n.lower()}')")
				data = check.get('data', [])

				if data != []:
					return await BASE.twitch.send_message(message.channel_name, f'@{message.display_name} > Override >> Phaaze already is in "{n}\'s" channel')
				else:
					u = BASE.modules._Twitch_.Utils.get_user(BASE, n.lower(), search="name")
					if u == None:
						return await BASE.twitch.send_message(message.channel_name, f'@{message.display_name} > Override >> No channel found. "{n}"')

					BASE.PhaazeDB.insert(
						into='setting/twitch_channel',
						content=dict(
							twitch_id = u['_id'],
							twitch_name = u['name']
						))
					await BASE.twitch.join_channel(u['name'])
					return await BASE.twitch.send_message(message.channel_name, f'@{message.display_name} > Override >> Phaaze successfull joined "{u["display_name"]}"')

		#check if not already in
		check = BASE.PhaazeDB.select(of='setting/twitch_channel', where=f"str(data['twitch_id']) == str('{message.user_id}')")
		data = check.get('data', [])
		#is in
		if data != []:
			return await BASE.twitch.send_message(message.channel_name, f'@{message.display_name} > Phaaze already is in your channel')

		#its not in -> add it
		else :
			BASE.PhaazeDB.insert(
				into='setting/twitch_channel',
				content=dict(
					twitch_id = message.user_id,
					twitch_name = message.name
				))
			await BASE.twitch.join_channel(message.name)
			return await BASE.twitch.send_message(message.channel_name, f'@{message.display_name} > Phaaze successfull joined your channel!')


	async def leave(BASE, message, kwargs):
		#check if in
		check = BASE.PhaazeDB.select(of='setting/twitch_channel', where=f"str(data['twitch_id']) == str('{message.user_id}')")
		data = check.get('data', [])
		#is in
		if data == []:
			return await BASE.twitch.send_message(message.channel_name, f'@{message.display_name} > Phaaze is not in your channel')

		#its in -> remove it
		else :
			BASE.PhaazeDB.delete(
				of='setting/twitch_channel',
				where = f"str(data['twitch_id']) == str('{message.user_id}')"
				)
			await BASE.twitch.part_channel(message.name)
			return await BASE.twitch.send_message(message.channel_name, f'@{message.display_name} > Phaaze successfully left your channel!')


