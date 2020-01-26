from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Discord.main_discord import PhaazebotDiscord

import discord
from Utils.Classes.discordcommand import DiscordCommand
from Utils.Classes.discordcommandcontext import DiscordCommandContext
from Utils.Classes.discorduserstats import DiscordUserStats
from Platforms.Discord.utils import getDiscordServerUsers, getDiscordMemberFromString
from Platforms.Discord.levels import Calc as LevelCalc
from Utils.stringutils import prettifyNumbers

async def levelStatus(cls:"PhaazebotDiscord", Command:DiscordCommand, CommandContext:DiscordCommandContext) -> dict:

	# other than, normal, mod or regular commands that get blocked in commands.py
	# we can not tell if that command is a level command until now, so we end it now

	# owner disabled level commands serverwide
	if CommandContext.ServerSettings.owner_disable_level:
		return {}

	# same as above just for a a specific channel
	if CommandContext.Message.channel.id in CommandContext.ServerSettings.disabled_levelchannels:
		return {}

	Member:discord.Member = None

	search_from:str = " ".join([x for x in CommandContext.parts[1:]])
	# no search use author
	if not search_from:
		Member = CommandContext.Message.author
	# try a search
	else:
		Member:discord.Member = getDiscordMemberFromString(cls, Guild=CommandContext.Message.guild, search=search_from, Message=CommandContext.Message)
		if not Member:
			return {"content": ":warning: Could not find a user with your query"}

	users:list = await getDiscordServerUsers(cls, Command.server_id, member_id=Member.id)

	if not users:
		return {"content": f":warning: Seems like there are no statistics for `{Member.name}`\nMaybe the user never typed anything or got deleted."}

	LevelUser:DiscordUserStats = users.pop(0)

	exp_current:int = LevelUser.exp
	lvl_current:int = LevelCalc.getLevel(exp_current)
	exp_next:int = LevelCalc.getExp(lvl_current+1)
	rank:str = prettifyNumbers(LevelUser.rank) if LevelUser.rank else "[N/A]"
	avatar:str = Member.avatar_url if Member.avatar_url else Member.default_avatar_url

	Emb:discord.Embed = discord.Embed(color=0x00ffdd)
	Emb.set_author(name=Member.name, icon_url=avatar)

	Emb.add_field(name="Level:", value=f"{prettifyNumbers(lvl_current)}", inline=True)
	Emb.add_field(name="Exp:", value=f"{prettifyNumbers(exp_current)} / {prettifyNumbers(exp_next)}", inline=True)
	Emb.add_field(name="Rank:", value=f"# {rank}", inline=True)

	if LevelUser.edited:
		Emb.add_field(name=":warning: EDITED",value="Exp value got edited.", inline=False)

	if LevelUser.medals:
		Emb.add_field(name="Medals:",value="\n".join(m for m in LevelUser.medals), inline=False)

	return {"embed": Emb}
