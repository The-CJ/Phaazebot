from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Discord.main_discord import PhaazebotDiscord

import discord
from Utils.Classes.discordcommand import DiscordCommand
from Utils.Classes.discordcommandcontext import DiscordCommandContext
from Utils.Classes.discordleveluser import DiscordLevelUser
from Platforms.Discord.utils import getDiscordServerLevels, getDiscordMemberFromString

async def levelStatus(cls:"PhaazebotDiscord", Command:DiscordCommand, CommandContext:DiscordCommandContext) -> dict:

	# other than, normal, mod or regular commands that get blocked in commands.py
	# we can not tell if that command is a level command until now, so we end it now

	# owner disabled level commands serverwide
	if CommandContext.ServerSettings.owner_disable_level:
		return {}

	# same as above just for a a specific channel
	if CommandContext.Message.channel.id in CommandContext.ServerSettings.disable_chan_level:
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

	users:list = await getDiscordServerLevels(cls, Command.server_id, member_id=Member.id)

	if not users:
		return {"content": f":warning: Seems like there are no statistics for `{Member.name}`\nMaybe the user never typed anything or got deleted."}

	LevelUser:DiscordLevelUser = users.pop(0)

	print(LevelUser)

	return {"content": ":white_check_mark:"}
