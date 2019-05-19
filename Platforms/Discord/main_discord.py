from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from main import Phaazebot

import discord

class PhaazebotDiscord(discord.Client):
	def __init__(self, BASE:"Phaazebot"):
		self.BASE:"Phaazebot" = BASE
		super().__init__()

	async def on_ready(self):
		pass

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

	#errors
	async def on_error(self, event_method, *args, **kwargs):
		pass
