from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Discord.main_discord import PhaazebotDiscord

import discord
import datetime
from Utils.Classes.discordcommand import DiscordCommand
from Utils.Classes.discordcommandcontext import DiscordCommandContext
from Platforms.Discord.utils import getDiscordMemberFromString

MAX_PRUNE_AMOUNT:int = 500
DELETE_VIA_MEMBER:int = 300

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

class PruneCheck(object):
	"""
		Used to provide a lookup for prune messages,
		all messages go through self.check and all messages that should be deleted return true.
		Following messages should be deleted:
			# Only delete messages that are in time range of 2 weeks
			- Inital Message (the message that executed prune)
			-- If `method` == 1:
				- all messages
			-- if `method` == 2:
				- up to 300 messages of found member as `Member` in channel
	"""
	def __init__(self, InitMsg:discord.Message, method:int=0, Member:discord.Member=None):
		self.InitalMessage:discord.Message = InitMsg

		self.method:int = method
		self.Member:discord.Member = Member

		self.amount_deleted:int = 0
		self.amount_to_old:int = 0

		self.MaxAge:datetime.datetime = (datetime.datetime.now() - datetime.timedelta(weeks = 2))

	def check(self, CheckMessage:discord.Message) -> bool:
		"""
			checks a message, if anything is wrong,
			return False, and kee pthe message,
			else True for delete
		"""
		# Inital Message
		if CheckMessage.id == self.InitalMessage.id:
			self.amount_deleted += 1
			return True

		# check for member as author, if not False
		if self.method == 2:
			if self.Member.id != CheckMessage.author.id:
				return False

		# message is too old, skip
		if CheckMessage.created_at < self.MaxAge:
			self.amount_to_old += 1
			return False

		# if not stopped, delete it
		self.amount_deleted += 1
		return True

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
