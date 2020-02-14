from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from main import Phaazebot

import discord
import asyncio
import traceback
from .openchannel import openChannel

class PhaazebotDiscord(discord.Client):
	def __init__(self, BASE:"Phaazebot"):
		super().__init__()
		self.BASE:"Phaazebot" = BASE

	def __bool__(self):
		return self.BASE.IsReady.discord

	async def on_ready(self) -> None:
		try:
			await self.change_presence(
				activity = discord.Game(name = self.BASE.Vars.DISCORD_MODT),
				status = discord.Status.online,
				afk = False
			)

			self.BASE.Logger.info("Discord connected")
			self.BASE.IsReady.discord = True

		except discord.errors.GatewayNotFound:
			self.BASE.Logger.warning("Discord Gatway Error --> Changing.")
			await asyncio.sleep(3)
			await self.on_ready()

	async def on_message(self, Message:discord.Message) -> None:

		if Message.author == self.user: return
		if not self.BASE.IsReady.discord: return
		if Message.author.bot: return

		if "phaaze" in Message.content.lower():
			try: await Message.channel.trigger_typing()
			except: pass

		if type(Message.channel) is discord.TextChannel:
			return await openChannel(self, Message)

		else:
			self.BASE.Logger.warning("TODO: " + type(Message.channel))

	async def on_message_delete(self, message):
		pass

	async def on_message_edit(self, Before:discord.Message, After:discord.Message) -> None:
		await self.on_message(After)

	#member management
	async def on_member_join(self, Member:discord.Member) -> None:
		# set member active, if there was a known entry
		self.BASE.PhaazeDB.updateQuery(
			table = "discord_user",
			content = {"on_server":"1"},
			where = "guild_id = %s AND member_id = %s",
			where_values = ( str(Member.guild.id), str(Member.id) )
		)

	async def on_member_remove(self, Member:discord.Member) -> None:
		# set member inactive
		self.BASE.PhaazeDB.updateQuery(
			table = "discord_user",
			content = {"on_server":"0"},
			where = "guild_id = %s AND member_id = %s",
			where_values = ( str(Member.guild.id), str(Member.id) )
		)

	async def on_member_ban(self, member):
		pass

	async def on_member_unban(self, server, user):
		pass

	async def on_member_update(self, before, after):
		pass

	#channel management
	async def on_channel_create(self, channel):
		pass

	async def on_channel_delete(self, channel):
		pass

	#role management
	async def on_server_role_create(self, role):
		pass

	async def on_server_role_delete(self, role):
		pass

	# errors
	async def on_error(self, event_method, *args, **kwargs):
		tb = traceback.format_exc()
		self.BASE.Logger.error(f'(Discord) Ignoring exception in {event_method}\n{tb}')
