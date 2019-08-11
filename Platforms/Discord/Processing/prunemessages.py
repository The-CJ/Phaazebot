from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Discord.main_discord import PhaazebotDiscord

import discord
# import datetime
from Utils.Classes.discordcommand import DiscordCommand
from Utils.Classes.discordcommandcontext import DiscordCommandContext
from Platforms.Discord.utils import getDiscordMemberFromString

MAX_PRUNE_AMOUNT:int = 500

async def pruneMessages(cls:"PhaazebotDiscord", Command:DiscordCommand, CommandContext:DiscordCommandContext) -> dict:

	Perm:discord.Permissions = CommandContext.Message.channel.permissions_for(CommandContext.Message.guild.me)
	if not Perm.manage_messages:
		return {"content": ":no_entry_sign: Phaaze need the `Manage messages` permissions to execute prune"}

	search_by:str = " ".join([x for x in CommandContext.parts[1:]])

	if not search_by:
		return {"content": ":warning: Please add a message amount or a member query string"}

	elif search_by.isdigit() and len(search_by) < 5:
		# digits that are not a id
		return await pruneMessagesByAmount(cls, Command, CommandContext, int(search_by))

	else:
		SearchMember = getDiscordMemberFromString(cls, CommandContext.Message.guild, search_by, Message=CommandContext.Message)
		if not SearchMember:
			return {"content": ":warning: Could not find a member..."}

		return await pruneMessagesByMember(cls, Command, CommandContext, SearchMember)

async def pruneMessagesByAmount(cls:"PhaazebotDiscord", Command:DiscordCommand, CommandContext:DiscordCommandContext, amount:int) -> dict:
	# to much
	if amount > MAX_PRUNE_AMOUNT:
		return {"content": f":no_entry_sign: **{str(amount)}** messages are to much in one. Try making 2 small request, instead of one big."}

	# secure ask
	if amount > 100:
		await CommandContext.Message.channel.send(content= f":question: **{str(amount)}** are a lot, are you sure you wanna delete all of them?\n\nType: yes")

		def check(Message:discord.Message):
			if Message.channel.id == CommandContext.Message.channel.id:
				if Message.author.id == CommandContext.Message.author.id:
					return True
			return False

		try:
			Res:discord.Message = await cls.wait_for("message", check=check, timeout=30)
		except:
			Res:discord.Message = None

		if (not Res) or (Res.content.lower()) != "yes":
			return {"content": ":warning: Prune canceled."}

		return {"content": "Should be pruned"}


async def pruneMessagesByMember(cls:"PhaazebotDiscord", Command:DiscordCommand, CommandContext:DiscordCommandContext, Member:discord.Member) -> dict:

	return {"content": "Should be pruned"}
