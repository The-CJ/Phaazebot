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

		if not message.author.id in self.BASE.vars.developer_id: return #During Dev. + Patrons
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
		return #TODO: Fix this
		await self.BASE.moduls._Discord_.Discord_Events.event_logs.message_delete(self.BASE, message)

	async def on_message_edit(self, before, after):
		# await self.BASE.moduls._Discord_.Discord_Events.event_logs.message_edited(self.BASE, before, after)

		if after.author.id != "117746512380952582": return #During Dev.
		if after.author == self.BASE.phaaze.user: return
		if not self.BASE.is_ready.discord: return
		if after.author.bot: return

		if after.channel.is_private:
			await self.BASE.moduls._Discord_.Priv.base(self.BASE, after)
		else:
			await self.BASE.moduls._Discord_.Open.base(self.BASE, after)

	#member management
	async def on_member_join(self, member):
		return #TODO: Fix this
		await self.BASE.moduls._Discord_.Discord_Events.member_join(self.BASE, member)

	async def on_member_remove(self, member):
		return #TODO: Fix this
		await self.BASE.moduls._Discord_.Discord_Events.member_remove(self.BASE, member)

	async def on_member_ban(self, member):
		return #TODO: Fix this
		await self.BASE.moduls._Discord_.Discord_Events.event_logs.member_ban(self.BASE, member)

	async def on_member_unban(self, server, user):
		return #TODO: Fix this
		await self.BASE.moduls._Discord_.Discord_Events.event_logs.member_unban(self.BASE, server, user)

	async def on_member_update(self, before, after):
		return #TODO: Fix this
		await self.BASE.moduls._Discord_.Discord_Events.event_logs.member_update(self.BASE, before, after)

	#channel management
	async def on_channel_create(self, channel):
		return #TODO: Fix this
		if channel.is_private: return
		await self.BASE.moduls._Discord_.Discord_Events.event_logs.channel_update(self.BASE, channel, "add")

	async def on_channel_delete(self, channel):
		return #TODO: Fix this
		if channel.is_private: return
		await self.BASE.moduls._Discord_.Discord_Events.event_logs.channel_update(self.BASE, channel, "rem")

	#role management
	async def on_server_role_create(self, role):
		return #TODO: Fix this
		await self.BASE.moduls._Discord_.Discord_Events.event_logs.role_updates(self.BASE, role, "add")

	async def on_server_role_delete(self, role):
		return #TODO: Fix this
		await self.BASE.moduls._Discord_.Discord_Events.event_logs.role_updates(self.BASE, role, "rem")

	#errors
	async def on_error(self, event_method, *args, **kwargs):
		print('Ignoring exception in {}'.format(event_method))
		traceback.print_exc()
