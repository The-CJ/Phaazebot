#BASE.modules._TWITCH_.CMD.Mod

import asyncio, random, json

async def Base(BASE, message, **kwargs):
	m = message.content[(BASE.vars.TRIGGER_TWITCH):].lower().split(" ")
	check = m[0]

	if check.startswith("addcom"):
		return await BASE.modules._Twitch_.Custom.add(BASE, message, kwargs)

	if check.startswith("delcom"):
		return await BASE.modules._Twitch_.Custom.rem(BASE, message, kwargs)

	if check.startswith("addquote"):
		return await BASE.modules._Twitch_.PROCESS.Mod.Quote.add(BASE, message, kwargs)

	if check.startswith("delquote"):
		return await BASE.modules._Twitch_.PROCESS.Mod.Quote.rem(BASE, message, kwargs)
