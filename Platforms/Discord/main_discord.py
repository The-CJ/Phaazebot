from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from main import Phaazebot

import discord
import asyncio
import traceback

class PhaazebotDiscord(discord.Client):
	def __init__(self, BASE:"Phaazebot"):
		super().__init__()
		self.BASE:"Phaazebot" = BASE

	async def on_ready(self) -> None:
		try:
			await self.change_presence(
				activity=discord.Game ( type=0, name=f"{self.BASE.Vars.TRIGGER_DISCORD}help | v{self.BASE.version}"	),
				status=discord.Status.online
			)

			self.BASE.Logger.info("Discord connected")
			self.BASE.IsReady.discord = True

		except discord.errors.GatewayNotFound:
			self.BASE.Logger.warning("Discord Gatway Error --> Changing.")
			await asyncio.sleep(3)
			await self.on_ready()

	async def on_message(self, message):
		pass

	async def on_message_delete(self, message):
		pass

	async def on_message_edit(self, before, after):
		pass

	#member management
	async def on_member_join(self, member):
		pass

	async def on_member_remove(self, member):
		pass

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
		self.BASE.Logger.error(f'Ignoring exception in {event_method}\n{tb}')
