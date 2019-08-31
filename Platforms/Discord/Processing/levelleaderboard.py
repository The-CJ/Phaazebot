from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Discord.main_discord import PhaazebotDiscord

import discord
from Utils.Classes.discordcommand import DiscordCommand
from Utils.Classes.discordcommandcontext import DiscordCommandContext
from Utils.Classes.discordleveluser import DiscordLevelUser
from Platforms.Discord.utils import getDiscordServerLevels
from Platforms.Discord.levels import Calc as LevelCalc

DEFAULT_LEADERBOARD_LEN:int = 5
MAX_LEADERBOARD_LEN:int = 15

async def levelLeaderboard(cls:"PhaazebotDiscord", Command:DiscordCommand, CommandContext:DiscordCommandContext) -> dict:

	# other than, normal, mod or regular commands that get blocked in commands.py
	# we can not tell if that command is a level command until now, so we end it now

	# owner disabled level commands serverwide
	if CommandContext.ServerSettings.owner_disable_level:
		return {}

	# same as above just for a a specific channel
	if CommandContext.Message.channel.id in CommandContext.ServerSettings.disable_chan_level:
		return {}

	specific_len:str = CommandContext.part(1)
	if specific_len:
		if not specific_len.isdigit():
			specific_len:int = DEFAULT_LEADERBOARD_LEN
		else:
			specific_len:int = int(specific_len)

	else:
		specific_len:int = DEFAULT_LEADERBOARD_LEN

	if specific_len > MAX_LEADERBOARD_LEN or not specific_len:
		return {"content": f":warning: `{specific_len}` is unsupported, length must be between 1 and 15"}

	Command.server_id = "117801129496150019" #debug testing, using R.o.D. data
	users:list = await getDiscordServerLevels(cls, Command.server_id, limit=specific_len, order_str="ORDER BY exp")

	print(users)

	return {"content": "Emb"}
