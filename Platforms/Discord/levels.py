from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from .main_discord import PhaazebotDiscord

import discord
import math
from Utils.Classes.discordserversettings import DiscordServerSettings
from Utils.Classes.discorduserstats import DiscordUserStats
from .utils import getDiscordServerUsers

DEFAULT_LEVEL_MESSAGE = "[mention] is now Level **[lvl]** :tada:"

async def checkLevel(cls:"PhaazebotDiscord", Message:discord.Message, ServerSettings:DiscordServerSettings) -> None:
	"""
		Run every time a user writes a message (not edited) and updates the exp.
		(running checks on every message, even if level progress is disabled,
		so every user has a entry in the db, for currency and other stuff)
	"""

	# TODO: Cooldown

	result:list = await getDiscordServerUsers(cls, Message.guild.id, member_id=Message.author.id)

	if not result:
		LevelUser:DiscordUserStats = await newUser(cls, Message.guild.id, Message.author.id, username=Message.author.name, nickname=Message.author.nick)
	else:
		# there should be only one in the list
		LevelUser:DiscordUserStats = result.pop(0)

	# we check here so we ensure a new user entry, if needed
	if str(Message.channel.id) in ServerSettings.disabled_levelchannels: return
	if ServerSettings.owner_disable_level: return

	LevelUser.exp += 1

	cls.BASE.PhaazeDB.query("""
		UPDATE `discord_user`
		SET
			`exp` = `exp` + 1,
			`username` = %s,
			`nickname` = %s
		WHERE `discord_user`.`guild_id` = %s
			AND `discord_user`.`member_id` = %s""",
		( Message.author.name, Message.author.nick, str(LevelUser.server_id), str(LevelUser.member_id) )
	)

	await checkLevelProgress(cls, Message, LevelUser, ServerSettings)

async def newUser(cls:"PhaazebotDiscord", guild_id:str, member_id:str, **more_infos:dict) -> DiscordUserStats:
	"""
		Creates a new entry in discord_user table
		more_infos can contain optional infos:
			guild_id:str
			member_id:str
			exp:int
			currency:int
	"""

	user_info:dict = dict(
		guild_id = str(guild_id),
		member_id = str(member_id)
	)

	if "username" in more_infos:
		user_info["username"] = more_infos["username"]

	if "nickname" in more_infos:
		user_info["nickname"] = more_infos["nickname"]

	if "exp" in more_infos:
		user_info["exp"] = more_infos["exp"]

	if "currency" in more_infos:
		user_info["currency"] = more_infos["currency"]

	try:
		cls.BASE.PhaazeDB.insertQuery(
			table = "discord_user",
			content = user_info
		)
		cls.BASE.Logger.debug(f"(Discord) New entry into levels: S:{guild_id} M:{member_id}", require="discord:level")
		return DiscordUserStats( user_info, guild_id )
	except:
		cls.BASE.Logger.critical(f"(Discord) New entry into levels failed: S:{guild_id} M:{member_id}")
		raise RuntimeError("New entry into levels failed")

async def checkLevelProgress(cls:"PhaazebotDiscord", Message:discord.Message, LevelUser:DiscordUserStats, ServerSettings:DiscordServerSettings) -> None:

	current_level:int = Calc.getLevel(LevelUser.exp)
	next_level_exp:int = Calc.getExp(current_level + 1)

	if next_level_exp == LevelUser.exp:
		await announceLevelUp(cls, Message, LevelUser, ServerSettings, current_level + 1)

async def announceLevelUp(cls:"PhaazebotDiscord", Message:discord.Message, LevelUser:DiscordUserStats, ServerSettings:DiscordServerSettings, level_to_announce:str or int) -> None:

	LevelChannel:discord.TextChannel = None

	if ServerSettings.level_announce_chan:
		LevelChannel = discord.utils.get(Message.guild.channels, id=int(ServerSettings.level_announce_chan))
	if not LevelChannel:
		LevelChannel = Message.channel

	level_message:str = None
	if ServerSettings.level_custom_msg != None:
		level_message = ServerSettings.level_custom_msg
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
