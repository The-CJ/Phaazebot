##BASE.modules._Twitch_.Blacklist

import asyncio, re

link_regex = re.compile(r'(https?:\/\/)?(\.?[a-zA-Z0-9]+)+\.[a-zA-Z0-9]{2,8}(\/[^ \n]+)*')

async def check(BASE, message, channel_settings):
	#ignore mods
	if await BASE.modules._Twitch_.Utils.is_Mod(BASE, message):	pass#return

	# TODO: Get own permissons

	blacklist = channel_settings.get("blacklist", [])
	ban_links = channel_settings.get("ban_links", False)
	link_whitelist = channel_settings.get("link_whitelist", [])

	for word in blacklist:
		if word.lower() in message.content.lower():
			return await punish(BASE, message, channel_settings, reason="word")

	if ban_links:
		found_links = re.finditer(link_regex, message.content)
		if found_links != None:

			for hit in found_links:
				p = True

				for white_link in link_whitelist:
					if re.search(white_link, hit.group(0)) != None:
						p = False
						break

				if p:
					return await punish(BASE, message, channel_settings, reason="link")

async def punish(BASE, message, channel_settings, reason="word"):
	punishment_level = channel_settings.get("blacklist_punishment", 0)
	print(reason)