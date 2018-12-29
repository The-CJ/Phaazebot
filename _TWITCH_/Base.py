#BASE.modules._Twitch_.Base

import asyncio, math

async def on_message(BASE, message):

	# NOTE: -
	# PhaazeDB can handle ~700 request/sec without a big delay.
	# Discord traffic at highest: ~200 request/s calculated with 5M+ Users
	# means there are ~500 request/s left, based on twitchstatus.com we have ~ 900-1000 msg/s on ALL channels
	# calculated with 200 - 400 channels (~5-20 msg/s) should not be a huge problem and have space for PhaazeWeb and more

	channel_settings = await BASE.modules._Twitch_.Utils.get_channel_settings(BASE, message.channel_id)

	#blacklist (Only, when links are banned or at least one word is in the blacklist AND there is a purge/timeout)
	if channel_settings.get("blacklist_punishment", 0) != 0 and (channel_settings.get('ban_links', False) or channel_settings.get('blacklist', []) != []):
		await BASE.modules._Twitch_.Blacklist.check(BASE, message, channel_settings)

	#custom command
	if channel_settings.get('active_custom', False):
		channel_commands = await BASE.modules._Twitch_.Utils.get_channel_commands(BASE, message.channel_id)
		if len(channel_commands) != 0:
			await BASE.modules._Twitch_.Custom.get(BASE, message, channel_settings=channel_settings, channel_commands=channel_commands)

	#level
	if channel_settings.get('active_level', False):
		await BASE.modules._Twitch_.Level.Base(BASE, message, channel_settings=channel_settings)

	#osu link
	if channel_settings.get('linked_osu_account', None) != None:
		await BASE.modules._Twitch_.PROCESS.Normal.OsuRequests.Base(BASE, message, channel_settings=channel_settings)

	#Phaaze Commands
	if message.content.startswith(BASE.vars.TRIGGER_TWITCH):
		if message.channel_name.lower() == BASE.twitch.nickname.lower():
		#phaaze channel only
			await BASE.modules._Twitch_.CMD.Normal.Main_channel(BASE, message, channel_settings=channel_settings)

		if await BASE.modules._Twitch_.Utils.is_Owner(BASE, message):
		#owner
			await BASE.modules._Twitch_.CMD.Owner.Base(BASE, message, channel_settings=channel_settings)

		if await BASE.modules._Twitch_.Utils.is_Mod(BASE, message):
		#mod
			await BASE.modules._Twitch_.CMD.Mod.Base(BASE, message, channel_settings=channel_settings)

		#normal
		await BASE.modules._Twitch_.CMD.Normal.Base(BASE, message, channel_settings=channel_settings)

