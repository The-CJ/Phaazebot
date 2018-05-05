#BASE.modules._Discord_.Discord_Events

import discord, asyncio, datetime

class Message(object):
	prune_lock = []

	async def delete(BASE, message):
		try:
			if message.channel.id in Message.prune_lock:
				await asyncio.sleep(30)
				try: Message.prune_lock.remove(message.channel.id)
				except: pass
				return
			server_settings = await BASE.modules._Discord_.Utils.get_server_setting(BASE, message.server.id)

			#track: Message.delete
			if "Message.delete".lower() in server_settings.get('track_options',[]) and server_settings.get('track_channel',None) != None:
				chan = discord.Object(id=server_settings.get("track_channel"))

				emb = discord.Embed(
					description=f"```{message.content[:1990]}```",
					timestamp=datetime.datetime.now(),
					color=0xffa100
				)
				emb.add_field(name='Author', value=f"{message.author.name}\n{message.author.mention}\n{message.author.id}", inline=False)
				emb.set_author(name="Log Event - [Message Delete]")
				await BASE.discord.send_message(chan, embed=emb)
		except:
			pass

	async def edit(BASE, before, after):
		try:
			if before.content == after.content: return
			server_settings = await BASE.modules._Discord_.Utils.get_server_setting(BASE, after.server.id)

			#track: Message.edit
			if "Message.edit".lower() in server_settings.get('track_options',[]) and server_settings.get('track_channel',None) != None:
				chan = discord.Object(id=server_settings.get("track_channel"))

				emb = discord.Embed(
					description=f"From:```{before.content[:950]}```\nTo:```{after.content[:950]}```",
					timestamp=datetime.datetime.now(),
					color=0xbbbbbb
				)
				emb.add_field(name='Author', value=f"{after.author.name}\n{after.author.mention}\n{after.author.id}", inline=False)
				emb.set_author(name="Log Event - [Message Edited]")
				await BASE.discord.send_message(chan, embed=emb)
		except:
			pass

	async def prune(BASE, message, amount):
		try:
			server_settings = await BASE.modules._Discord_.Utils.get_server_setting(BASE, message.server.id)

			#track: Message.edit
			if "Message.prune".lower() in server_settings.get('track_options',[]) and server_settings.get('track_channel',None) != None:
				chan = discord.Object(id=server_settings.get("track_channel"))

				emb = discord.Embed(
					description=f"Pruned {str(amount)} in `{message.channel.name}`",
					timestamp=datetime.datetime.now(),
					color=0xff4b00
				)
				emb.add_field(name='Author', value=f"{message.author.name}\n{message.author.mention}\n{message.author.id}", inline=False)
				emb.set_author(name="Log Event - [Message Pruned]")
				await BASE.discord.send_message(chan, embed=emb)
		except:
			pass

class Member(object):
	async def join(BASE, member):
		try:
			server_settings = await BASE.modules._Discord_.Utils.get_server_setting(BASE, member.server.id)

			#track: Member.join
			if "Member.join".lower() in server_settings.get('track_options',[]) and server_settings.get('track_channel',None) != None:
				chan = discord.Object(id=server_settings.get("track_channel"))
				avatar = member.avatar_url if "" != member.avatar_url != None else member.default_avatar_url

				emb = discord.Embed(
					description=f"{member.name}\n{member.mention}\n{member.id}",
					timestamp=datetime.datetime.now(),
					color=0x00ff00
				)
				emb.set_thumbnail(url=avatar)
				emb.set_author(name="Log Event - [Member Join]")
				await BASE.discord.send_message(chan, embed=emb)
		except:
			pass

		#welcome message
		if server_settings.get("welcome_msg", None) != None:
			try:
				chan = discord.Object(id=server_settings.get("welcome_chan"))

				entry = server_settings.get("welcome_msg", None)

				entry = entry.replace("[name]", member.name)
				entry = entry.replace("[server]", member.server.name)
				entry = entry.replace("[count]", str(member.server.member_count))
				entry = entry.replace("[mention]", member.mention)

				try: await BASE.discord.send_message(chan, entry[:1997])
				except Exception as e:

					BASE.PhaazeDB.update(
						of=f"discord/server_setting",
						where=f"data['server_id'] == '{member.server.id}'",
						content=dict( welcome_chan=None, welcome_msg=None )
					)

					if str(e.__class__) == "<class 'discord.errors.NotFound'>":
						await BASE.discord.send_message(
							member.server.owner,
							f":warning: The welcome announcement channel in `{member.server.name}` wasn't found. Welcome settings has been reset.")

					if str(e.__class__) == "<class 'discord.errors.Forbidden'>":
						await BASE.discord.send_message(
							member.server.owner,
							f":warning: Phaaze don't have permissions in `{member.server.name}` to send the welcome message. Welcome setting has been reset.")
			except:
				pass

		#welcome private message
		if server_settings.get("welcome_msg_priv", None) != None:
			try:
				entry = server_settings.get("welcome_msg_priv", None)

				entry = entry.replace("[name]", member.name)
				entry = entry.replace("[server]", member.server.name)
				entry = entry.replace("[count]", str(member.server.member_count))
				entry = entry.replace("[mention]", member.mention)

				try: await BASE.discord.send_message(member, entry[:1997])
				except Exception as e:

					if str(e.__class__) == "<class 'discord.errors.Forbidden'>":
						await BASE.discord.send_message(
							member.server.owner,
							f":warning: Phaaze could not send the Private welcome message for a new member in `{member.server.name}` Private welcome setting has been reset.")
			except:
				pass

		#autorole
		if server_settings.get("autorole", None) != None:
			try:
				role = discord.utils.get(member.server.roles, id=server_settings.get("autorole", None))
				if role == None:
					BASE.PhaazeDB.update(
						of=f"discord/server_setting",
						where=f"data['server_id'] == '{member.server.id}'",
						content=dict( autorole=None )
					)

					return await BASE.discord.send_message(
						member.server.owner,
						f":warning: The Autorole in `{member.server.name}` wasn't found. Autorole has been reset.")

				await BASE.discord.add_roles(member, role)

			except Exception as e:
				BASE.PhaazeDB.update(
					of=f"discord/server_setting",
					where=f"data['server_id'] == '{member.server.id}'",
					content=dict( autorole=None )
				)

				if str(e.__class__) == "<class 'discord.errors.NotFound'>":
					return await BASE.discord.send_message(member.server.owner, ":warning: The Autorole in `{0}` wasn't found. Autorole has been reset.".format(member.server.name))

				if str(e.__class__) == "<class 'discord.errors.Forbidden'>":
					return await BASE.discord.send_message(member.server.owner, ":warning: Phaaze doesn't have permissions to give `{1}` the Autorole in `{0}`. Autorole has been reset.".format(member.server.name, member.name))

	async def remove(BASE, member):
		try:
			server_settings = await BASE.modules._Discord_.Utils.get_server_setting(BASE, member.server.id)

			#track: Member.remove
			if "Member.remove".lower() in server_settings.get('track_options',[]) and server_settings.get('track_channel',None) != None:
				chan = discord.Object(id=server_settings.get("track_channel"))
				avatar = member.avatar_url if "" != member.avatar_url != None else member.default_avatar_url

				emb = discord.Embed(
					description=f"{member.name}\n{member.mention}\n{member.id}",
					timestamp=datetime.datetime.now(),
					color=0xff0000
				)
				emb.set_thumbnail(url=avatar)
				emb.set_author(name="Log Event - [Member Leave]")
				await BASE.discord.send_message(chan, embed=emb)
		except:
			pass

		#welcome message
		if server_settings.get("leave_msg", None) != None:
			try:
				chan = discord.Object(id=server_settings.get("leave_chan"))

				entry = server_settings.get("leave_msg", None)

				entry = entry.replace("[name]", member.name)
				entry = entry.replace("[server]", member.server.name)
				entry = entry.replace("[count]", str(member.server.member_count))
				entry = entry.replace("[mention]", member.mention)

				try: await BASE.discord.send_message(chan, entry[:1997])
				except Exception as e:

					BASE.PhaazeDB.update(
						of=f"discord/server_setting",
						where=f"data['server_id'] == '{member.server.id}'",
						content=dict( leave_chan=None, leave_msg=None )
					)

					if str(e.__class__) == "<class 'discord.errors.NotFound'>":
						await BASE.discord.send_message(
							member.server.owner,
							f":warning: The leave announcement channel in `{member.server.name}` wasn't found. Leave settings has been reset.")

					if str(e.__class__) == "<class 'discord.errors.Forbidden'>":
						await BASE.discord.send_message(
							member.server.owner,
							f":warning: Phaaze don't have permissions in `{member.server.name}` to send the leave message. Leave setting has been reset.")
			except:
				pass

	async def ban(BASE, member):
		try:
			server_settings = await BASE.modules._Discord_.Utils.get_server_setting(BASE, member.server.id)

			#track: Member.remove
			if "Member.ban".lower() in server_settings.get('track_options',[]) and server_settings.get('track_channel',None) != None:
				chan = discord.Object(id=server_settings.get("track_channel"))
				avatar = member.avatar_url if "" != member.avatar_url != None else member.default_avatar_url

				emb = discord.Embed(
					description=f"{member.name}\n{member.mention}\n{member.id}",
					timestamp=datetime.datetime.now(),
					color=0xff0000
				)
				emb.set_thumbnail(url=avatar)
				emb.set_author(name="Log Event - [Member Ban]")
				await BASE.discord.send_message(chan, embed=emb)
		except:
			pass

	async def unban(BASE, server, user):
		try:
			server_settings = await BASE.modules._Discord_.Utils.get_server_setting(BASE, server.id)

			#track: Member.remove
			if "Member.unban".lower() in server_settings.get('track_options',[]) and server_settings.get('track_channel',None) != None:
				chan = discord.Object(id=server_settings.get("track_channel"))
				avatar = user.avatar_url if "" != user.avatar_url != None else user.default_avatar_url

				emb = discord.Embed(
					description=f"{user.name}\n{user.id}",
					timestamp=datetime.datetime.now(),
					color=0x55ff00
				)
				emb.set_thumbnail(url=avatar)
				emb.set_author(name="Log Event - [Member Unban]")
				await BASE.discord.send_message(chan, embed=emb)
		except:
			pass

	async def update(BASE, before, after):
		pass # NOTE: I have no idea what to log...

class Channel(object):
	async def create(BASE, channel):
		try:
			server_settings = await BASE.modules._Discord_.Utils.get_server_setting(BASE, channel.server.id)

			#track: Channel.create
			if "Channel.create".lower() in server_settings.get('track_options',[]) and server_settings.get('track_channel',None) != None:
				chan = discord.Object(id=server_settings.get("track_channel"))

				emb = discord.Embed(
					description=f"{channel.name}\n{channel.mention}\n{channel.id}",
					timestamp=datetime.datetime.now(),
					color=0x00ee00
				)
				emb.set_author(name="Log Event - [Channel Created]")
				await BASE.discord.send_message(chan, embed=emb)
		except:
			pass

	async def delete(BASE, channel):
		try:
			server_settings = await BASE.modules._Discord_.Utils.get_server_setting(BASE, channel.server.id)

			#track: Channel.delete
			if "Channel.delete".lower() in server_settings.get('track_options',[]) and server_settings.get('track_channel',None) != None:
				chan = discord.Object(id=server_settings.get("track_channel"))

				emb = discord.Embed(
					description=f"{channel.name}\n{channel.mention}\n{channel.id}",
					timestamp=datetime.datetime.now(),
					color=0xee0000
				)
				emb.set_author(name="Log Event - [Channel Deleted]")
				await BASE.discord.send_message(chan, embed=emb)
		except:
			pass

class Role(object):
	async def create(BASE, role):
		try:
			server_settings = await BASE.modules._Discord_.Utils.get_server_setting(BASE, role.server.id)

			#track: Channel.create
			if "Role.create".lower() in server_settings.get('track_options',[]) and server_settings.get('track_channel',None) != None:
				chan = discord.Object(id=server_settings.get("track_channel"))

				emb = discord.Embed(
					description=f"{role.name}\n{role.id}",
					timestamp=datetime.datetime.now(),
					color=0x00ee00
				)
				emb.set_author(name="Log Event - [Role Created]")
				await BASE.discord.send_message(chan, embed=emb)
		except:
			pass

	async def delete(BASE, role):
		try:
			server_settings = await BASE.modules._Discord_.Utils.get_server_setting(BASE, role.server.id)

			#track: Channel.delete
			if "Role.delete".lower() in server_settings.get('track_options',[]) and server_settings.get('track_channel',None) != None:
				chan = discord.Object(id=server_settings.get("track_channel"))

				emb = discord.Embed(
					description=f"{role.name}\n{role.id}",
					timestamp=datetime.datetime.now(),
					color=0x00ee00
				)
				emb.set_author(name="Log Event - [Role Deleted]")
				await BASE.discord.send_message(chan, embed=emb)
		except:
			pass

class Phaaze(object):
	async def custom(BASE, server_id, state, trigger=None):
		try:
			server_settings = await BASE.modules._Discord_.Utils.get_server_setting(BASE, server_id)

			#track: Phaaze.custom
			if "Phaaze.custom".lower() in server_settings.get('track_options',[]) and server_settings.get('track_channel',None) != None:
				chan = discord.Object(id=server_settings.get("track_channel"))

				if state.lower() == "add" and trigger != None:
					emb = discord.Embed(
						description=f"Trigger: {trigger}",
						timestamp=datetime.datetime.now(),
						color=0x00ee00
					)
					emb.set_author(name="Log Event - [Custom Command Created]")
					await BASE.discord.send_message(chan, embed=emb)

				if state.lower() == "remove" and trigger != None:
					emb = discord.Embed(
						description=f"Trigger: {trigger}",
						timestamp=datetime.datetime.now(),
						color=0xee0000
					)
					emb.set_author(name="Log Event - [Custom Command Removed]")
					await BASE.discord.send_message(chan, embed=emb)

				if state.lower() == "update" and trigger != None:
					emb = discord.Embed(
						description=f"Trigger: {trigger}",
						timestamp=datetime.datetime.now(),
						color=0xeeee00
					)
					emb.set_author(name="Log Event - [Custom Command Updated]")
					await BASE.discord.send_message(chan, embed=emb)
		except:
			pass

	async def quote(BASE, message, state):
		try:
			server_settings = await BASE.modules._Discord_.Utils.get_server_setting(BASE, message.server.id)

			#track: Phaaze.quote
			if "Phaaze.quote".lower() in server_settings.get('track_options',[]) and server_settings.get('track_channel',None) != None:
				chan = discord.Object(id=server_settings.get("track_channel"))

				if state.lower() == "add":
					emb = discord.Embed(
						description=f"Executed by: \n{message.author.name}\n{message.author.mention}\n{message.author.id}",
						timestamp=datetime.datetime.now(),
						color=0x00ee00
					)
					emb.set_author(name="Log Event - [Quote Created]")
					await BASE.discord.send_message(chan, embed=emb)

				if state.lower() == "remove":
					emb = discord.Embed(
						description=f"Executed by: \n{message.author.name}\n{message.author.mention}\n{message.author.id}",
						timestamp=datetime.datetime.now(),
						color=0xee0000
					)
					emb.set_author(name="Log Event - [Quote Removed]")
					await BASE.discord.send_message(chan, embed=emb)

				if state.lower() == "clear":
					emb = discord.Embed(
						description=f"Executed by: \n{message.author.name}\n{message.author.mention}\n{message.author.id}",
						timestamp=datetime.datetime.now(),
						color=0xff0000
					)
					emb.set_author(name="Log Event - [All Quotes Cleared]")
					await BASE.discord.send_message(chan, embed=emb)

		except:
			pass