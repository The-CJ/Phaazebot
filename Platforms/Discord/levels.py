from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from .main_discord import PhaazebotDiscord

import discord
import json
import math
from Utils.Classes.discordserversettings import DiscordServerSettings
from Utils.Classes.discordleveluser import DiscordLevelUser
from .utils import getDiscordServerLevels

DEFAULT_LEVEL_MESSAGE = "[mention] is now Level **[lvl]** :tada:"

async def checkLevel(cls:"PhaazebotDiscord", Message:discord.Message, ServerSettings:DiscordServerSettings) -> None:
	"""
		Run every time a user writes a message (not edited) and updates the exp.
	"""

	# TODO: Cooldown

	if Message.channel.id in ServerSettings.disable_chan_level: return
	if ServerSettings.owner_disable_level: return

	result:list = await getDiscordServerLevels(cls, Message.guild.id, member_id=Message.author.id)

	if not result:
		LevelUser:DiscordLevelUser = await newUser(cls, Message.guild.id, Message.author.id)
	else:
		# there should be only on in the list
		LevelUser:DiscordLevelUser = result[0]

	LevelUser.exp += 1
	if LevelUser.exp >= 0xFFFFF: #=1'048'575
		LevelUser.exp = 1

	res:dict = cls.BASE.PhaazeDB.update(
		of = f"discord/level/level_{LevelUser.server_id}",
		where = f"str(data['member_id']) == str({json.dumps(LevelUser.member_id)})",
		content = {"exp": LevelUser.exp}
	)

	if res.get("status", "error") == "updated":
		await checkLevelProgress(cls, Message, LevelUser, ServerSettings)

async def newUser(cls:"PhaazebotDiscord", server_id:str, member_id:str) -> DiscordLevelUser:

	res:dict = cls.BASE.PhaazeDB.insert(
		into = f"discord/level/level_{server_id}",
		content = {"member_id": member_id}
	)

	if res.get("status", "error") == "inserted":
		cls.BASE.Logger.debug(f"(Discord) New entry into levels: S:{server_id} M:{member_id}", require="discord:level")
		return DiscordLevelUser( {"member_id": member_id}, server_id )
	else:
		cls.BASE.Logger.critical(f"(Discord) New entry into levels failed: S:{server_id} M:{member_id}")
		raise RuntimeError("New entry into levels failed")

async def checkLevelProgress(cls:"PhaazebotDiscord", Message:discord.Message, LevelUser:DiscordLevelUser, ServerSettings:DiscordServerSettings) -> None:

	current_level:int = Calc.getLevel(LevelUser.exp)
	next_level_exp:int = Calc.getExp(current_level + 1)

	if next_level_exp == LevelUser.exp:
		await announceLevelUp(cls, Message, LevelUser, ServerSettings, current_level + 1)

async def announceLevelUp(cls:"PhaazebotDiscord", Message:discord.Message, LevelUser:DiscordLevelUser, ServerSettings:DiscordServerSettings, level_to_announce:str or int) -> None:

	LevelChannel:discord.TextChannel = None

	if ServerSettings.level_announce_channel:
		LevelChannel = discord.utils.get(Message.guild.channels, id=int(ServerSettings.level_announce_channel))
	if not LevelChannel:
		LevelChannel = Message.channel

	level_message:str = None
	if ServerSettings.level_custom_message != None:
		level_message = ServerSettings.level_custom_message
	else:
		level_message = DEFAULT_LEVEL_MESSAGE

	level_message = level_message.replace("[mention]", str(Message.author.mention))
	level_message = level_message.replace("[name]", str(Message.author.name))
	level_message = level_message.replace("[id]", str(Message.author.id))
	level_message = level_message.replace("[exp]", str(LevelUser.exp))
	level_message = level_message.replace("[lvl]", str(level_to_announce))

	try: await LevelChannel.send( level_message )
	except: pass

class Calc(object):
	# calculation data and functions
	# since its hardcoded and only for discord
	# there are not controlled in BASE.Limit or BASE.Vars

	LEVEL_DEFAULT_EXP = 65
	LEVEL_MULTIPLIER = 0.15

	def getLevel(xp:int) -> int:
		l:float = (-Calc.LEVEL_DEFAULT_EXP + (Calc.LEVEL_DEFAULT_EXP ** 2 - 4 * (Calc.LEVEL_DEFAULT_EXP * Calc.LEVEL_MULTIPLIER) * (-xp)) ** 0.5) / (2 * (Calc.LEVEL_DEFAULT_EXP * Calc.LEVEL_MULTIPLIER))
		return math.floor(l)

	def getExp(lvl:int) -> int:
		l:float = (lvl * Calc.LEVEL_DEFAULT_EXP) + ( (Calc.LEVEL_MULTIPLIER * lvl) * (lvl * Calc.LEVEL_DEFAULT_EXP) )
		return math.floor(l)