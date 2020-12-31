from typing import TYPE_CHECKING, Any
if TYPE_CHECKING:
	from phaazebot import Phaazebot

import discord
import asyncio
import traceback
from Platforms.Discord.openchannel import openChannel
from Platforms.Discord.events import (
	eventOnMemberJoin,
	eventOnMemberRemove
)

class PhaazebotDiscord(discord.Client):
	def __init__(self, BASE:"Phaazebot", *args, **kwargs):
		# changes to receive wanted events
		PhaazeIntents:discord.Intents = discord.Intents(
			guilds=True,
			members=True,
			messages=True,
		)
		kwargs["intents"] = PhaazeIntents

		super().__init__(*args, **kwargs)
		self.BASE:"Phaazebot" = BASE

	def __bool__(self):
		return self.BASE.IsReady.discord

	async def on_ready(self) -> None:
		"""
		Called when Phaaze is first connected, or sometimes when reconnected
		"""
		try:
			await self.change_presence(
				activity=discord.Game(name=self.BASE.Vars.discord_modt),
				status=discord.Status.online,
				afk=False
			)

			self.BASE.Logger.info("Discord connected")
			self.BASE.IsReady.discord = True

		except discord.errors.GatewayNotFound:
			self.BASE.Logger.warning("Discord Gateway Error --> Changing.")
			await asyncio.sleep(3)
			await self.on_ready()

	async def on_message(self, Message:discord.Message) -> None:
		"""
		Called everytime a message is new message is received
		"""

		if not self.BASE.IsReady.discord: return
		if Message.author == self.user: return
		if Message.author.bot: return
		if str(Message.author.id) in self.BASE.Vars.discord_debug_user_id:
			await self.debugCall(Message)

		if "phaaze" in Message.content.lower():
			try: await Message.channel.trigger_typing()
			except: pass

		if type(Message.channel) is discord.TextChannel:
			return await openChannel(self, Message)

		else:
			self.BASE.Logger.warning("Phaaze received message via a privat channel")

	async def on_message_edit(self, _Before:discord.Message, After:discord.Message) -> None:
		"""
		Called only when a message is edited, and this message is in the self.cached_messages buffer.
		max len(self.cached_messages) == self.max_messages
		"""
		await self.on_message(After)

	# member management
	async def on_member_join(self, Member:discord.Member) -> None:
		"""
		Called when a new user joins a guild
		"""
		await eventOnMemberJoin(self, Member)

	async def on_member_remove(self, Member:discord.Member) -> None:
		"""
		Called when a user leaves a guild
		"""
		await eventOnMemberRemove(self, Member)

	# errors
	async def on_error(self, event_method, *args, **kwargs):
		"""
		Default error function, called everytime something went wrong
		"""
		tb = traceback.format_exc()
		self.BASE.Logger.error(f'(Discord) Ignoring exception in {event_method}\n{tb}')

	# debug
	async def debugCall(self, Message:discord.Message):
		"""
		string evaluation on user input,
		only for the user associated with self.BASE.Vars.discord_debug_user_id
		starting a message with ### or !!! will execute everything after this
		### is a normal call
		!!! a coroutine
		"""

		# we check again... just to be sure
		if not str(Message.author.id) in self.BASE.Vars.discord_debug_user_id:
			return

		coroutine:bool
		command:str

		if Message.content.startswith("###"):
			command = Message.content.replace("###", '', 1)
			coroutine = False

		elif Message.content.startswith("!!!"):
			command = Message.content.replace("!!!", '', 1)
			coroutine = True
		else:
			return

		try:
			res:Any = eval(command)
			if coroutine: res = await res
			return await Message.channel.send(f"```{str(res)}```")

		except Exception as Fail:
			tb = traceback.format_exc()
			return await Message.channel.send(f"Exception: {str(Fail)}```{str(tb)}```")
