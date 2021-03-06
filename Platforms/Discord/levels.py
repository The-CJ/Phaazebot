from typing import TYPE_CHECKING, Dict, Optional
if TYPE_CHECKING:
	from Platforms.Discord.main_discord import PhaazebotDiscord

import math
import asyncio
import discord
from Utils.Classes.discordserversettings import DiscordServerSettings
from Utils.Classes.discorduserstats import DiscordUserStats

DEFAULT_LEVEL_MESSAGE:str = "[user-mention] is now Level **[lvl]** :tada:"

class GlobalDiscordLevelMessageCooldownStorage(object):
	"""
	i present the GDLMCS, short for "Global Discord Level Message Cooldown Storage" (my short names get worse, right?)
	after a user typed something, the unique key is saved.
	while its in there, a user cant gain xp again
	after cooldown is gone, remove unique key from here and unlock user
	"""
	def __init__(self):
		self.in_cooldown:Dict[str, bool] = {}

	def check(self, Message:discord.Message) -> bool:
		key:str = f"{Message.guild.id}-{Message.author.id}"
		if self.in_cooldown.get(key, None): return True
		else: return False

	def cooldown(self, cls:"PhaazebotDiscord", Message:discord.Message) -> None:
		asyncio.ensure_future(self.cooldownCoro(cls, Message))

	async def cooldownCoro(self, cls:"PhaazebotDiscord", Message:discord.Message) -> None:
		key:str = f"{Message.guild.id}-{Message.author.id}"
		if self.in_cooldown.get(key, None): return

		# add
		self.in_cooldown[key] = True

		# wait
		await asyncio.sleep(cls.BASE.Limit.discord_level_cooldown)

		# remove
		self.in_cooldown.pop(key, None)


GDLMCS:GlobalDiscordLevelMessageCooldownStorage = GlobalDiscordLevelMessageCooldownStorage()

async def checkLevel(cls:"PhaazebotDiscord", Message:discord.Message, ServerSettings:DiscordServerSettings, DiscordUser:DiscordUserStats) -> None:
	"""
		Run every time a user writes a message (not edited) and updates the exp.
		(running checks on every message, even if level progress is disabled,
		so every user has a entry in the db, for currency and other stuff)
	"""

	# author is still in cooldown
	if GDLMCS.check(Message): return

	# are levels disabled in any means?
	if str(Message.channel.id) in ServerSettings.disabled_levelchannels: return
	if ServerSettings.owner_disable_level: return

	if not DiscordUser:
		# we check here so we ensure a new user entry, if needed
		DiscordUser = await newUser(cls, Message.guild.id, Message.author.id, username=Message.author.name, nickname=Message.author.nick)

	DiscordUser.exp += 1

	cls.BASE.PhaazeDB.query("""
		UPDATE `discord_user`
		SET
			`exp` = `exp` + 1,
			`username` = %s,
			`nickname` = %s
		WHERE `discord_user`.`guild_id` = %s
			AND `discord_user`.`member_id` = %s""",
		(Message.author.name, Message.author.nick, str(DiscordUser.server_id), str(DiscordUser.member_id))
	)

	# add author to cooldown
	GDLMCS.cooldown(cls, Message)

	# check level progress, send level up messages yes/no?
	await checkLevelProgress(cls, Message, DiscordUser, ServerSettings)

async def newUser(cls:"PhaazebotDiscord", guild_id:str, member_id:str, **more_info:dict) -> DiscordUserStats:
	"""
		Creates a new entry in discord_user table,
		`more_info` can contain optional info's:

		* `guild_id` : Optional[str]
		* `member_id` : Optional[str]
		* `exp` : Optional[int]
		* `currency` : Optional[int]
	"""

	user_info:dict = dict(
		guild_id=str(guild_id),
		member_id=str(member_id)
	)

	if "username" in more_info:
		user_info["username"] = more_info["username"]

	if "nickname" in more_info:
		user_info["nickname"] = more_info["nickname"]

	if "exp" in more_info:
		user_info["exp"] = more_info["exp"]

	if "currency" in more_info:
		user_info["currency"] = more_info["currency"]

	try:
		cls.BASE.PhaazeDB.insertQuery(
			table="discord_user",
			content=user_info
		)
		cls.BASE.Logger.debug(f"(Discord) New entry into levels: S:{guild_id} M:{member_id}", require="discord:level")
		return DiscordUserStats(user_info)
	except:
		cls.BASE.Logger.critical(f"(Discord) New entry into levels failed: S:{guild_id} M:{member_id}")
		raise RuntimeError("New entry into levels failed")

async def checkLevelProgress(cls:"PhaazebotDiscord", Message:discord.Message, LevelUser:DiscordUserStats, ServerSettings:DiscordServerSettings) -> None:

	current_level:int = Calc.getLevel(LevelUser.exp)
	next_level_exp:int = Calc.getExp(current_level + 1)

	if next_level_exp == LevelUser.exp:
		await announceLevelUp(cls, Message, LevelUser, ServerSettings, current_level + 1)

async def announceLevelUp(_cls:"PhaazebotDiscord", Message:discord.Message, LevelUser:DiscordUserStats, ServerSettings:DiscordServerSettings, level_to_announce:str or int) -> None:

	LevelChannel:Optional[discord.TextChannel] = None

	if ServerSettings.level_announce_chan:
		LevelChannel = discord.utils.get(Message.guild.channels, id=int(ServerSettings.level_announce_chan))
	if not LevelChannel:
		LevelChannel = Message.channel

	level_message:str = DEFAULT_LEVEL_MESSAGE
	if ServerSettings.level_custom_msg:
		level_message = ServerSettings.level_custom_msg

	level_message = level_message.replace("[user-mention]", str(Message.author.mention))
	level_message = level_message.replace("[user-name]", str(Message.author.name))
	level_message = level_message.replace("[id]", str(Message.author.id))
	level_message = level_message.replace("[exp]", str(LevelUser.exp))
	level_message = level_message.replace("[lvl]", str(level_to_announce))

	try: await LevelChannel.send(level_message)
	except: pass

class Calc(object):
	# calculation data and functions
	# since its hardcoded and only for discord
	# there are not controlled in BASE.Limit or BASE.Vars

	LEVEL_DEFAULT_EXP = 65
	LEVEL_MULTIPLIER = 0.15

	@staticmethod
	def getLevel(xp:int) -> int:
		l:float = (-Calc.LEVEL_DEFAULT_EXP + (Calc.LEVEL_DEFAULT_EXP ** 2 - 4 * (Calc.LEVEL_DEFAULT_EXP * Calc.LEVEL_MULTIPLIER) * (-xp)) ** 0.5) / (2 * (Calc.LEVEL_DEFAULT_EXP * Calc.LEVEL_MULTIPLIER))
		return math.floor(l)

	@staticmethod
	def getExp(lvl:int) -> int:
		l:float = (lvl * Calc.LEVEL_DEFAULT_EXP) + ((Calc.LEVEL_MULTIPLIER * lvl) * (lvl * Calc.LEVEL_DEFAULT_EXP))
		return math.floor(l)
