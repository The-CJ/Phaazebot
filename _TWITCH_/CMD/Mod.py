#BASE.modules._TWITCH_.CMD.Mod

import asyncio

async def Base(BASE, message, **kwargs):
	m = message.content[len(BASE.vars.TRIGGER_TWITCH):].lower().split(" ")
	check = m[0]

	if kwargs.get('channel_settings', {}).get('owner_disable_mod', False) and not await BASE.modules._Twitch_.Utils.is_Owner(BASE, message): return

	if check.startswith("addcom"):
		return await BASE.modules._Twitch_.Custom.add(BASE, message, kwargs)

	if check.startswith("delcom"):
		return await BASE.modules._Twitch_.Custom.rem(BASE, message, kwargs)

	if check.startswith("addquote"):
		return await BASE.modules._Twitch_.PROCESS.Mod.Quote.add(BASE, message, kwargs)

	if check.startswith("delquote"):
		return await BASE.modules._Twitch_.PROCESS.Mod.Quote.rem(BASE, message, kwargs)

	if check.startswith("setting"):
		return await BASE.modules._Twitch_.PROCESS.Mod.Settings.Base(BASE, message, kwargs)
