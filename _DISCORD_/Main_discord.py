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
													status=discord.Status.offline)
			setattr(self.BASE.vars, "app", await self.BASE.phaaze.application_info() )
			self.BASE.moduls.Console.GREEN("SUCCESS", "Discord Connected")
			setattr(self.BASE.vars, "discord_is_NOT_ready", False )
		except:
			self.BASE.moduls.Console.YELLOW("WARNING", "Discord Gatway Error --> Changing.")
			await asyncio.sleep(3)
			await self.on_ready()

	#message management
	async def on_message(self, message):

		if message.author == self.BASE.phaaze.user: return
		if self.BASE.vars.discord_is_NOT_ready: return
		if message.author.bot: return

		if "phaaze" in message.content.lower():
			try: await self.BASE.phaaze.send_typing(message.channel)
			except: pass

		if message.channel.is_private:
			await self.BASE.moduls.Priv.base(self.BASE, message)
		else:
			await self.BASE.moduls.Open.base(self.BASE, message)

	async def on_message_delete(self, message):
		await self.BASE.moduls.Discord_Events.event_logs.message_delete(self.BASE, message)

	async def on_message_edit(self, before, after):
		await self.BASE.moduls.Discord_Events.event_logs.message_edited(self.BASE, before, after)

		if after.author == self.BASE.phaaze.user: return
		if self.BASE.vars.discord_is_NOT_ready: return
		if after.author.bot: return

		if after.channel.is_private:
			await self.BASE.moduls.Priv.base(self.BASE, after)
		else:
			await self.BASE.moduls.Open.base(self.BASE, after)


	#member management
	async def on_member_join(self, member):
		self.BASE.moduls.logging_.log_member(member, "add")
		await self.BASE.moduls.Discord_Events.member_join(self.BASE, member)

	async def on_member_remove(self, member):
		self.BASE.moduls.logging_.log_member(member, "rem")
		await self.BASE.moduls.Discord_Events.member_remove(self.BASE, member)

	async def on_member_ban(self, member):
		await self.BASE.moduls.Discord_Events.event_logs.member_ban(self.BASE, member)

	async def on_member_unban(self, server, user):
		await self.BASE.moduls.Discord_Events.event_logs.member_unban(self.BASE, server, user)

	async def on_member_update(self, before, after):
		await self.BASE.moduls.Discord_Events.event_logs.member_update(self.BASE, before, after)

	#channel management
	async def on_channel_create(self, channel):
		if channel.is_private: return
		await self.BASE.moduls.Discord_Events.event_logs.channel_update(self.BASE, channel, "add")

	async def on_channel_delete(self, channel):
		if channel.is_private: return
		await self.BASE.moduls.Discord_Events.event_logs.channel_update(self.BASE, channel, "rem")

	#role management
	async def on_server_role_create(self, role):
		await self.BASE.moduls.Discord_Events.event_logs.role_updates(self.BASE, role, "add")

	async def on_server_role_delete(self, role):
		await self.BASE.moduls.Discord_Events.event_logs.role_updates(self.BASE, role, "rem")

	#logs
	async def on_server_join(self, server):
		self.BASE.moduls.logging_.log_server(server, "add")

	async def on_server_remove(self, server):
		self.BASE.moduls.logging_.log_server(server, "rem")

	#errors
	async def on_error(self, event_method, *args, **kwargs):
		print('Ignoring exception in {}'.format(event_method))
		traceback.print_exc()
