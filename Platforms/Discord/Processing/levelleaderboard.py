from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Discord.main_discord import PhaazebotDiscord

import discord
from tabulate import tabulate
from Utils.Classes.discordcommand import DiscordCommand
from Utils.Classes.discordcommandcontext import DiscordCommandContext
from Platforms.Discord.utils import getDiscordServerUsers
from Platforms.Discord.levels import Calc as LevelCalc
from Utils.stringutils import prettifyNumbers

DEFAULT_LEADERBOARD_LEN:int = 5
MAX_LEADERBOARD_LEN:int = 15

async def levelLeaderboard(cls:"PhaazebotDiscord", Command:DiscordCommand, CommandContext:DiscordCommandContext) -> dict:

	# other than, normal, mod or regular commands that get blocked in commands.py
	# we can not tell if that command is a level command until now, so we end it now

	# owner disabled level commands serverwide
	if CommandContext.ServerSettings.owner_disable_level:
		return {}

	# same as above just for a a specific channel
	if CommandContext.Message.channel.id in CommandContext.ServerSettings.disabled_levelchannels:
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

	users:list = await getDiscordServerUsers(cls, Command.server_id, limit=specific_len, order_str="ORDER BY exp DESC")

	if not users:
		return {"content": ":question: Seems like there are no member with level for a leaderboard :("}

	# there are less member ín the return than the limit requests, very rare
	if len(users) < specific_len:
		specific_len = len(users)

	return_table:list = [ ["#", "|", "LVL", "|", "EXP", "|", "Name"], ["---", "|", "---", "|", "---", "|", "---"] ]
	for LevelUser in users:

		e:str = " [EDITED]" if LevelUser.edited else ""
		lvl:str = prettifyNumbers( LevelCalc.getLevel(LevelUser.exp) )
		exp:str = prettifyNumbers( LevelUser.exp )
		Member:discord.Member = CommandContext.Message.guild.get_member( int(LevelUser.member_id) )
		if Member:
			user_name:str = Member.name
		else:
			user_name:str = "[N/A]"

		return_table.append( [f"#{LevelUser.rank}", "|", lvl, "|", f"{exp}{e}", "|", user_name] )

	table:str = tabulate(return_table, tablefmt="plain")

	return {"content": f"**Top: {specific_len} leaderboard** :link: {cls.BASE.Vars.WEB_ROOT}/discord/level/{Command.server_id} ```{table}```"}
