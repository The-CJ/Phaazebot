from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from .main_discord import PhaazebotDiscord

import discord
import json
from Utils.Classes.discordserversettings import DiscordServerSettings

async def getDiscordSeverSettings(cls:"PhaazebotDiscord", origin:discord.Message or str or int, prevent_new:bool=False) -> DiscordServerSettings:
	"""
		Get server settings for a discord server/guild
		create new one if not prevented
	"""
	if type(origin) is discord.Message:
		server_id:str = str(origin.guild.id)

	elif type(origin) is str:
		server_id:str = str(origin)

	else:
		server_id:str = origin

	data:dict = cls.BASE.PhaazeDB.select(
		of = "discord/server_setting",
		where = f"data['server_id'] == {json.dumps(server_id)}",
	)

	if not data['data']:
		if prevent_new:
			return DiscordServerSettings()
		else:
			return await makeDiscordSeverSettings(cls, server_id)

	else:
		return DiscordServerSettings( infos = data["data"][0] )

async def makeDiscordSeverSettings(cls:"PhaazebotDiscord", server_id:str) -> DiscordServerSettings:
	"""
		Makes a new entry in the PhaazeDB for a discord server.
		since the new version v5+ we dont add a base construct to the db,
		it should be covered by DB defaults
	"""

	res:dict = cls.BASE.PhaazeDB.insert(
		into = "discord/server_setting",
		content = {"server_id":server_id}
	)

	if res["status"] == "inserted":
		cls.BASE.Logger.info(f"(Discord) New server settings DB entry: {server_id}")
		return DiscordServerSettings( infos = {} )
	else:
		cls.BASE.Logger.critical(f"(Discord) New server settings failed: {server_id}")
		raise RuntimeError("Creating new DB entry failed")
