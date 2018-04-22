import asyncio, discord, traceback

class phaaze(discord.Client):
	def __init__(self, BASE):
		BASE.phaaze = self
		self.BASE = BASE
		super().__init__()

	async def on_ready(self):
		try:
			await self.BASE.phaaze.change_presence(	game=discord.Game(	type=0,
																		name=self.BASE.version_nr),
													status=discord.Status.online)
			setattr(self.BASE.vars, "app", await self.BASE.phaaze.application_info() )
			self.BASE.moduls.Console.GREEN("SUCCESS", "Discord Connected")
			setattr(self.BASE.is_ready, "discord", True )
		except:
			self.BASE.moduls.Console.YELLOW("WARNING", "Discord Gatway Error --> Changing.")
			await asyncio.sleep(3)
			await self.on_ready()

	#message management
	async def on_message(self, message):

		if message.author == self.BASE.phaaze.user: return
		if not self.BASE.is_ready.discord: return
		if message.author.bot: return

		if "phaaze" in message.content.lower():
			try: await self.BASE.phaaze.send_typing(message.channel)
			except: pass

		if message.channel.is_private:
			await self.BASE.moduls._Discord_.Priv.base(self.BASE, message)
		else:
			await self.BASE.moduls._Discord_.Open.base(self.BASE, message)

	async def on_message_delete(self, message):
		await self.BASE.moduls._Discord_.Discord_Events.Message.delete(self.BASE, message) # TODO:

	async def on_message_edit(self, before, after):
		await self.BASE.moduls._Discord_.Discord_Events.Message.edit(self.BASE, after) # TODO:

		if after.author == self.BASE.phaaze.user: return
		if not self.BASE.is_ready.discord: return
		if after.author.bot: return

		if after.channel.is_private:
			await self.BASE.moduls._Discord_.Priv.base(self.BASE, after)
		else:
			await self.BASE.moduls._Discord_.Open.base(self.BASE, after)

	#member management
	async def on_member_join(self, member):
		await self.BASE.moduls._Discord_.Discord_Events.Member.join(self.BASE, member) # TODO: Logs

	async def on_member_remove(self, member):
		await self.BASE.moduls._Discord_.Discord_Events.Member.remove(self.BASE, member) # TODO: Logs

	async def on_member_ban(self, member):
		await self.BASE.moduls._Discord_.Discord_Events.Member.ban(self.BASE, member) # TODO:

	async def on_member_unban(self, server, user):
		await self.BASE.moduls._Discord_.Discord_Events.Member.unban(self.BASE, server, user) # TODO:

	async def on_member_update(self, before, after):
		await self.BASE.moduls._Discord_.Discord_Events.Member.update(self.BASE, before, after) # TODO:

	#channel management
	async def on_channel_create(self, channel):
		if channel.is_private: return
		await self.BASE.moduls._Discord_.Discord_Events.Channel.create(self.BASE, channel) # TODO:

	async def on_channel_delete(self, channel):
		if channel.is_private: return
		await self.BASE.moduls._Discord_.Discord_Events.Channel.delete(self.BASE, channel) # TODO:

	#role management
	async def on_server_role_create(self, role):
		await self.BASE.moduls._Discord_.Discord_Events.Role.create(self.BASE, role) # TODO:

	async def on_server_role_delete(self, role):
		await self.BASE.moduls._Discord_.Discord_Events.Role.delete(self.BASE, role) # TODO:

	#errors
	async def on_error(self, event_method, *args, **kwargs):
		print('Ignoring exception in {}'.format(event_method))
		traceback.print_exc()
