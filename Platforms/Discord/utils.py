from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from .main_discord import PhaazebotDiscord

import discord
import json
from Utils.Classes.discordserversettings import DiscordServerSettings
from Utils.Classes.discordcommand import DiscordCommand

async def getDiscordSeverSettings(cls:"PhaazebotDiscord", origin:discord.Message or str or int, prevent_new:bool=False) -> DiscordServerSettings:
	"""
		Get server settings for a discord server/guild
		create new one if not prevented.
		Returns a DiscordServerSettings()
	"""
	if type(origin) is discord.Message:
		server_id:str = str(origin.guild.id)

	elif type(origin) is str:
		server_id:str = str(origin)

	else:
		server_id:str = origin

	res:dict = cls.BASE.PhaazeDB.select(
		of = "discord/server_setting",
		where = f"data['server_id'] == {json.dumps(server_id)}",
	)

	if not res['data']:
		if prevent_new:
			return DiscordServerSettings()
		else:
			return await makeDiscordSeverSettings(cls, server_id)

	else:
		return DiscordServerSettings( infos = res["data"][0] )

async def makeDiscordSeverSettings(cls:"PhaazebotDiscord", server_id:str) -> DiscordServerSettings:
	"""
		Makes a new entry in the PhaazeDB for a discord server.
		since the new version v5+ we dont add a base construct to the db,
		it should be covered by DB defaults.
		Returns a DiscordServerSettings()
	"""

	res:dict = cls.BASE.PhaazeDB.insert(
		into = "discord/server_setting",
		content = {"server_id":server_id}
	)

	if res.get("status", "error") == "inserted":
		cls.BASE.Logger.info(f"(Discord) New server settings DB entry: {server_id}")
		return DiscordServerSettings( infos = {} )
	else:
		cls.BASE.Logger.critical(f"(Discord) New server settings failed: {server_id}")
		raise RuntimeError("Creating new DB entry failed")

async def getDiscordServerCommands(cls:"PhaazebotDiscord", server_id:str, trigger:str=None, prevent_new:bool=False) -> list:
	"""
		Get custom commands from a discord server, if trigger = None, get all
		else only get one associated with trigger.
		Returns a list of DiscordCommand()
	"""

	of = f"discord/commands/commands_{server_id}"

	if trigger:
		where:str = f"data['trigger'] == {json.dumps(trigger)}"
		limit:int = 1

	else:
		where:str = None
		limit:int = None

	try:
		res:dict = cls.BASE.PhaazeDB.select(of=of, limit=limit, where=where)
	except:
		res:dict = dict()

	if res.get("status", "error") == "error":
		if prevent_new:
			return []
		else:
			return await makeDiscordServerCommands(cls, server_id)

	else:
		return [DiscordCommand(x, server_id) for x in res["data"]]

async def makeDiscordServerCommands(cls:"PhaazebotDiscord", server_id:str) -> list:
	"""
		Create a new DB container for Discord server commands
	"""
	name = f"discord/commands/commands_{server_id}"
	res:dict = cls.BASE.PhaazeDB.create(name=name)

	if res.get("status", "error") == "created":
		default:dict = {
			"content": "",
			"trigger": "",
			"uses": 0,
			"complex": False,
			"function": "textOnly",
			"require": 0
		}
		res2:dict = cls.BASE.PhaazeDB.default(of=name, content = default)
		if res2.get("status", "error") == "default set":
			cls.BASE.Logger.info(f"(Discord) New server command container: {server_id}")
			return []

	cls.BASE.Logger.critical(f"(Discord) New server command container failed: {server_id}")
	raise RuntimeError("Creating new DB container failed")
