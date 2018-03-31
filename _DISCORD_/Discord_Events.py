#BASE.moduls._Discord_.Discord_Events

import discord, asyncio, json, datetime

async def member_join(BASE, member):
	file = await BASE.moduls.Utils.get_server_file(BASE, member.server.id)
	file["private_welcome_message"] = file.get("private_welcome_message", "")
	await event_logs.join(BASE, member)
	file["welcome"] = file.get("welcome", "")
	file["private_welcome_message"] = file.get("private_welcome_message", "")
	file["autorole_id"] = file.get("autorole_id", "")

	if file["welcome"] != "":
		try:
			chan = discord.Object(id=file["wel_chan"]) if file["wel_chan"] != "" else member.server.default_channel

			entry = file["welcome"]

			entry = entry.replace("[name]", member.name)
			entry = entry.replace("[server]", member.server.name)
			entry = entry.replace("[count]", str(member.server.member_count))
			entry = entry.replace("[mention]", member.mention)

			try: await BASE.phaaze.send_message(chan, entry[:1997])
			except Exception as e:

				file["welcome"] = ""
				file["wel_chan"] = ""

				with open("SERVERFILES/{0}.json".format(member.server.id), "w") as save:
					json.dump(file, save)
					setattr(BASE.serverfiles, "server_"+member.server.id, file)

					if str(e.__class__) == "<class 'discord.errors.NotFound'>":
						await BASE.phaaze.send_message(member.server.owner, ":warning: The welcome announcement channel in `{0}` wasn't found. Welcome setting has been reset.".format(member.server.name))

					if str(e.__class__) == "<class 'discord.errors.Forbidden'>":
						await BASE.phaaze.send_message(member.server.owner, ":warning: Phaaze don't have permissions in `{0}` to send the welcome message. Welcome setting has been reset.".format(member.server.name))
		except:
			pass

	if file["private_welcome_message"] != "":
		try:
			entry = file["private_welcome_message"]

			entry = entry.replace("[name]", member.name)
			entry = entry.replace("[server]", member.server.name)
			entry = entry.replace("[count]", str(member.server.member_count))
			entry = entry.replace("[mention]", member.mention)

			try: await BASE.phaaze.send_message(member, entry[:1997])
			except Exception as e:

				file["private_welcome_message"] = ""

				with open("SERVERFILES/{0}.json".format(member.server.id), "w") as save:
					json.dump(file, save)
					setattr(BASE.serverfiles, "server_"+member.server.id, file)

					if str(e.__class__) == "<class 'discord.errors.Forbidden'>":
						await BASE.phaaze.send_message(member.server.owner, ":warning: Phaaze could not send the Private welcome message for a new member in `{0}` Private welcome setting has been reset.".format(member.server.name))
		except:
			pass

	if file["autorole_id"] != "":
		try:
			role = discord.utils.get(member.server.roles, id=file["autorole_id"])
			if role == None:
				file["autorole_id"] = ""
				with open("SERVERFILES/{0}.json".format(member.server.id), "w") as save:
					json.dump(file, save)
					setattr(BASE.serverfiles, "server_"+member.server.id, file)
					return await BASE.phaaze.send_message(member.server.owner, ":warning: The Autorole in `{0}` wasn't found. Autorole has been reset.".format(member.server.name))

			return await BASE.phaaze.add_roles(member, role)

		except Exception as e:
			file["autorole_id"] = ""
			with open("SERVERFILES/{0}.json".format(member.server.id), "w") as save:
				json.dump(file, save)
				setattr(BASE.serverfiles, "server_"+member.server.id, file)

			if str(e.__class__) == "<class 'discord.errors.NotFound'>":
				return await BASE.phaaze.send_message(member.server.owner, ":warning: The Autorole in `{0}` wasn't found. Autorole has been reset.".format(member.server.name))

			if str(e.__class__) == "<class 'discord.errors.Forbidden'>":
				return await BASE.phaaze.send_message(member.server.owner, ":warning: Phaaze doesn't have permissions to give `{1}` the Autorole in `{0}`. Autorole has been reset.".format(member.server.name, member.name))

async def member_remove(BASE, member):
	file = await BASE.moduls.Utils.get_server_file(BASE, member.server.id)
	await event_logs.leave(BASE, member)
	file["leave"] = file.get("leave", "")
	if file["leave"] != "":
		chan = discord.Object(id=file["lea_chan"]) if file["lea_chan"] != "" else member.server.default_channel

		entry = file["leave"]

		entry = entry.replace("[name]", member.name)
		entry = entry.replace("[server]", member.server.name)
		entry = entry.replace("[count]", str(member.server.member_count))
		entry = entry.replace("[mention]", member.mention)

		try: return await BASE.phaaze.send_message(chan, entry[:1997])
		except Exception as e:

			file["leave"] = ""
			file["lea_chan"] = ""

			with open("SERVERFILES/{0}.json".format(member.server.id), "w") as save:
				json.dump(file, save)
				setattr(BASE.serverfiles, "server_"+member.server.id, file)

				if str(e.__class__) == "<class 'discord.errors.NotFound'>":
					return await BASE.phaaze.send_message(member.server.owner, ":warning: The welcome announcement channel in `{0}` wasn't found. **Welcome setting has been reset.**".format(member.server.name))

				if str(e.__class__) == "<class 'discord.errors.Forbidden'>":
					return await BASE.phaaze.send_message(member.server.owner, ":warning: Phaaze don't have permissions in `{0}` to send the welcome message. **Welcome setting has been reset.**".format(member.server.name))

class event_logs(object):
	async def join(BASE, member):
		file = await BASE.moduls.Utils.get_track_file(BASE, member.server.id)
		if file["track_chan"] != "" and file["join"] == 1:
			try:
				fff = discord.Embed(	title= "Log-Event [Join]",
										timestamp=datetime.datetime.now(),
										color=0x69ff0c,
										description="{0} joined! \n{1}".format(member.name, member.mention))
				if member.avatar_url != "": fff.set_thumbnail(url=member.avatar_url)
				else: fff.set_thumbnail(url=member.default_avatar_url)

				return await BASE.phaaze.send_message(discord.Object(id=file["track_chan"]), embed=fff)
			except:
				file["track_chan"] = ""

				with open("SERVERFILES/TRACKFILES/{0}.json".format(member.server.id), "w") as save:
					json.dump(file, save)
					setattr(BASE.trackfiles, "track_"+member.server.id, file)

					try: return await BASE.phaaze.send_message(member.server.owner, ":warning: Phaaze wasn't able to send the logs for `{0}` to your set channel. The channel and the track option \"MEJO\" (Member join) has been reset".format(member.server.name))
					except: pass

	async def leave(BASE, member):
		file = await BASE.moduls.Utils.get_track_file(BASE, member.server.id)
		if file["track_chan"] != "" and file["leave"] == 1:
			try:
				fff = discord.Embed(	title= "Log-Event [Leave]",
										timestamp=datetime.datetime.now(),
										color=0xff0c0c,
										description="{0} left!\n{1}".format(member.name, member.mention))
				if member.avatar_url != "": fff.set_thumbnail(url=member.avatar_url)
				else: fff.set_thumbnail(url=member.default_avatar_url)

				return await BASE.phaaze.send_message(discord.Object(id=file["track_chan"]), embed=fff)
			except:
				file["track_chan"] = ""

				with open("SERVERFILES/TRACKFILES/{0}.json".format(member.server.id), "w") as save:
					json.dump(file, save)
					setattr(BASE.trackfiles, "track_"+member.server.id, file)

					try: return await BASE.phaaze.send_message(member.server.owner, ":warning: Phaaze wasn't able to send the logs for `{0}` to your set channel. The channel and the track option \"MELE\" (Member leave) has been reset".format(member.server.name))
					except: pass

	async def message_delete(BASE, message):
		file = await BASE.moduls.Utils.get_track_file(BASE, message.server.id)
		if file["track_chan"] != "" and file["message_deleted"] == 1 and message.author.id != BASE.phaaze.user.id and message.id not in BASE.cooldown.SPECIAL_COOLDOWNS.No_Prune_alert:
			try:
				fff = discord.Embed(	title= "Log-Event [Message deleted]",
										timestamp=datetime.datetime.now(),
										color=0x7e7e7e,
										description="A message by: {0} got deleted [{2}] :\n```{1}```".format(message.author.mention, message.content[:1900], message.channel.mention))

				return await BASE.phaaze.send_message(discord.Object(id=file["track_chan"]), embed=fff)
			except:
				file["track_chan"] = ""

				with open("SERVERFILES/TRACKFILES/{0}.json".format(message.server.id), "w") as save:
					json.dump(file, save)
					setattr(BASE.trackfiles, "track_"+message.server.id, file)

					try: return await BASE.phaaze.send_message(message.server.owner, ":warning: Phaaze wasn't able to send the logs for `{0}` to your set channel. The channel and the track option \"MDEL\" (Message deleted) has been reset".format(message.server.name))
					except: pass

	async def message_edited(BASE, old, new):
		try:
			file = await BASE.moduls.Utils.get_track_file(BASE, new.server.id)
			if file["track_chan"] != "" and file["message_edited"] == 1 and old.content != new.content and old.author.id != BASE.phaaze.user.id:
				try:
					fff = discord.Embed(	title= "Log-Event [Message edited]",
											timestamp=datetime.datetime.now(),
											color=0xfefefe,
											description="A message by: {0} in [{3}] got edited:\nFrom:\n```{1}```to```{2}```".format(old.author.mention, old.content[:950], new.content[:950], old.channel.mention))

					return await BASE.phaaze.send_message(discord.Object(id=file["track_chan"]), embed=fff)
				except:
					file["track_chan"] = ""

					with open("SERVERFILES/TRACKFILES/{0}.json".format(message.server.id), "w") as save:
						json.dump(file, save)
						setattr(BASE.trackfiles, "track_"+message.server.id, file)

						try: return await BASE.phaaze.send_message(message.server.owner, ":warning: Phaaze wasn't able to send the logs for `{0}` to your set channel. The channel and the track option \"MEDI\" (Message edited) has been reset".format(new.server.name))
						except: pass
		except:
			pass

	async def pruned(BASE, message, value):
		file = await BASE.moduls.Utils.get_track_file(BASE, message.server.id)
		if file["track_chan"] != "" and file["prune"] == 1:
			try:
				fff = discord.Embed(	title= "Log-Event [Message prune]",
										timestamp=datetime.datetime.now(),
										color=0xff7b08,
										description="{0} pruned {1} messages in {2}".format(message.author.mention, value, message.channel.mention))

				return await BASE.phaaze.send_message(discord.Object(id=file["track_chan"]), embed=fff)
			except:
				file["track_chan"] = ""

				with open("SERVERFILES/TRACKFILES/{0}.json".format(message.server.id), "w") as save:
					json.dump(file, save)
					setattr(BASE.trackfiles, "track_"+message.server.id, file)

					try: return await BASE.phaaze.send_message(message.server.owner, ":warning: Phaaze wasn't able to send the logs for `{0}` to your set channel. The channel and the track option \"MEDI\" (Message edited) has been reset".format(message.server.name))
					except: pass

	async def member_ban(BASE, member):
		file = await BASE.moduls.Utils.get_track_file(BASE, member.server.id)
		if file["track_chan"] != "" and file["banned"] == 1:
			try:
				fff = discord.Embed(	title= "Log-Event [Member banned]",
										timestamp=datetime.datetime.now(),
										color=0xEE0000,
										description="`{0}` got banned".format(member.name))

				return await BASE.phaaze.send_message(discord.Object(id=file["track_chan"]), embed=fff)
			except:
				file["track_chan"] = ""

				with open("SERVERFILES/TRACKFILES/{0}.json".format(message.server.id), "w") as save:
					json.dump(file, save)
					setattr(BASE.trackfiles, "track_"+message.server.id, file)

					try: return await BASE.phaaze.send_message(message.server.owner, ":warning: Phaaze wasn't able to send the logs for `{0}` to your set channel. The channel and the track option \"UBAN\" (User ban) has been reset".format(member.server.name))
					except: pass

	async def member_unban(BASE, server, user):
		file = await BASE.moduls.Utils.get_track_file(BASE, server.id)
		if file["track_chan"] != "" and file["banned"] == 1:
			try:
				fff = discord.Embed(	title= "Log-Event [Member unbanned]",
										timestamp=datetime.datetime.now(),
										color=0x00CC00,
										description="`{0}` got unbanned.".format(user.name))

				return await BASE.phaaze.send_message(discord.Object(id=file["track_chan"]), embed=fff)
			except:
				file["track_chan"] = ""

				with open("SERVERFILES/TRACKFILES/{0}.json".format(message.server.id), "w") as save:
					json.dump(file, save)
					setattr(BASE.trackfiles, "track_"+message.server.id, file)

					try: return await BASE.phaaze.send_message(message.server.owner, ":warning: Phaaze wasn't able to send the logs for `{0}` to your set channel. The channel and the track option \"UBAN\" (User unbanned) has been reset".format(message.server.name))
					except: pass

	async def role_updates(BASE, role, status):
		file = await BASE.moduls.Utils.get_track_file(BASE, role.server.id)
		file["role_update"] =  file.get("role_update", 0)

		if file["track_chan"] != "" and file["role_update"] == 1:
			try:
				stat = "created" if status == "add" else "deleted"
				fff = discord.Embed(	title= "Log-Event [Role {0}]".format(stat),
										timestamp=datetime.datetime.now(),
										color= 0x87e744 if status == "add" else 0xb81c1c ,
										description="The role: `{0}` has been {1}".format(role.name, stat) if status == "rem" else "A new Role hase been {0}\n ID: {1}".format(stat, role.id))

				return await BASE.phaaze.send_message(discord.Object(id=file["track_chan"]), embed=fff)
			except:
				file["track_chan"] = ""

				with open("SERVERFILES/TRACKFILES/{0}.json".format(role.server.id), "w") as save:
					json.dump(file, save)
					setattr(BASE.trackfiles, "track_"+role.server.id, file)

					try: return await BASE.phaaze.send_message(role.server.owner, ":warning: Phaaze wasn't able to send the logs for `{0}` to your set channel. The channel and the track option \"ROUP\" (Role Updates) has been reset".format(role.server.name))
					except: pass

	async def member_update(BASE, old, new):
		def diff(first, second):
			second = set(second)
			return [item for item in first if item not in second]

		file = await BASE.moduls.Utils.get_track_file(BASE, new.server.id)
		if file["track_chan"] == "": return

		file["role_update"] = _roles_ = file.get("role_update", 0)
		file["name_change"] = _names_ = file.get("name_change", 0)
		file["nickname_change"] = _n_names_ = file.get("nickname_change", 0)

		if _roles_ == 1 and old.roles != new.roles:
			#roles removed
			if len(old.roles) > len(new.roles):
				diff_ = diff(old.roles, new.roles)
				try:
					fff = discord.Embed(	title= "Log-Event [Member role update]",
											timestamp=datetime.datetime.now(),
											color= 0xc27215 ,
											description="The Member `{0}` just lost the role `{1}`".format(new.name, ", ".join(r.name for r in diff_)))
					return await BASE.phaaze.send_message(discord.Object(id=file["track_chan"]), embed=fff)

				except:
					file["track_chan"] = ""

					with open("SERVERFILES/TRACKFILES/{0}.json".format(new.server.id), "w") as save:
						json.dump(file, save)
						setattr(BASE.trackfiles, "track_"+new.server.id, file)

						try: return await BASE.phaaze.send_message(new.server.owner, ":warning: Phaaze wasn't able to send the logs for `{0}` to your set channel. The channel and the track option \"ROUP\" (Role Updates) has been reset".format(new.server.name))
						except: pass

			#roles added
			elif len(old.roles) < len(new.roles):
				diff_ = diff(new.roles, old.roles)
				try:
					fff = discord.Embed(	title= "Log-Event [Member role update]",
											timestamp=datetime.datetime.now(),
											color= 0xb940c ,
											description="The Member `{0}` just gained the role `{1}`".format(new.name, ", ".join(r.name for r in diff_)))
					return await BASE.phaaze.send_message(discord.Object(id=file["track_chan"]), embed=fff)


				except:
					file["track_chan"] = ""

					with open("SERVERFILES/TRACKFILES/{0}.json".format(new.server.id), "w") as save:
						json.dump(file, save)
						setattr(BASE.trackfiles, "track_"+new.server.id, file)

						try: return await BASE.phaaze.send_message(new.server.owner, ":warning: Phaaze wasn't able to send the logs for `{0}` to your set channel. The channel and the track option \"ROUP\" (Role Updates) has been reset".format(new.server.name))
						except: pass

		if _names_ == 1 and old.name != new.name:
			try:
				fff = discord.Embed(	title= "Log-Event [Member Global Name update]",
										timestamp=datetime.datetime.now(),
										color= 0x2474c7 ,
										description="The Member `{0}` is now called `{1}`".format(old.name, new.name))
				return await BASE.phaaze.send_message(discord.Object(id=file["track_chan"]), embed=fff)

			except:
				file["track_chan"] = ""
				file["name_change"] = 0

				with open("SERVERFILES/TRACKFILES/{0}.json".format(new.server.id), "w") as save:
					json.dump(file, save)
					setattr(BASE.trackfiles, "track_"+new.server.id, file)

					try: return await BASE.phaaze.send_message(new.server.owner, ":warning: Phaaze wasn't able to send the logs for `{0}` to your set channel. The channel and the track option \"NACH\" (Name update) has been reset".format(new.server.name))
					except: pass

		if _names_ == 1 and old.nick != new.nick:
			try:
				fff = discord.Embed(	title= "Log-Event [Nickname update]",
										timestamp=datetime.datetime.now(),
										color= 0x2474c7 ,
										description="The Member `{0}` changed his nickname to `{1}`".format(new.name, new.nick))
				return await BASE.phaaze.send_message(discord.Object(id=file["track_chan"]), embed=fff)

			except:
				file["track_chan"] = ""
				file["name_change"] = 0

				with open("SERVERFILES/TRACKFILES/{0}.json".format(new.server.id), "w") as save:
					json.dump(file, save)
					setattr(BASE.trackfiles, "track_"+new.server.id, file)

					try: return await BASE.phaaze.send_message(new.server.owner, ":warning: Phaaze wasn't able to send the logs for `{0}` to your set channel. The channel and the track option \"NICH\" (Nickname update) has been reset".format(new.server.name))
					except: pass

	async def channel_update(BASE, channel, status):
		file = await BASE.moduls.Utils.get_track_file(BASE, channel.server.id)
		file["channel_update"] =  file.get("channel_update", 0)

		if file["track_chan"] != "" and file["channel_update"] == 1:
			try:
				stat = "created" if status == "add" else "deleted"
				fff = discord.Embed(	title = "Log-Event [Channel {0}]".format(stat),
										timestamp =datetime.datetime.now(),
										color = 0x27d19e if status == "add" else 0xc78f14 ,
										description = "The {2} channel:\n`{0}` has been {1}".format(channel.name, stat, "text" if str(channel.type) == "text" else "voice"))

				return await BASE.phaaze.send_message(discord.Object(id=file["track_chan"]), embed=fff)
			except:
				file["track_chan"] = ""

				with open("SERVERFILES/TRACKFILES/{0}.json".format(channel.server.id), "w") as save:
					json.dump(file, save)
					setattr(BASE.trackfiles, "track_"+channel.server.id, file)

					try: return await BASE.phaaze.send_message(channel.server.owner, ":warning: Phaaze wasn't able to send the logs for `{0}` to your set channel. The channel and the track option \"CHUP\" (Channel Updates) has been reset".format(channel.server.name))
					except: pass

	async def custom_update(BASE, message, trigger, status):
		file = await BASE.moduls.Utils.get_track_file(BASE, message.server.id)
		file["custom_commands"] =  file.get("custom_commands", 0)

		if file["track_chan"] != "" and file["custom_commands"] == 1:
			try:
				stat = "created" if status == "add" else "deleted"
				fff = discord.Embed(	title = "Log-Event [Custom command {0}]".format(stat),
										timestamp =datetime.datetime.now(),
										color = 0x10c33a if status == "add" else 0xfe7c3c ,
										description = "The command: `{0}` has been {1}".format(trigger, stat))

				return await BASE.phaaze.send_message(discord.Object(id=file["track_chan"]), embed=fff)
			except:
				file["track_chan"] = ""

				with open("SERVERFILES/TRACKFILES/{0}.json".format(message.server.id), "w") as save:
					json.dump(file, save)
					setattr(BASE.trackfiles, "track_"+message.server.id, file)

					try: return await BASE.phaaze.send_message(message.server.owner, ":warning: Phaaze wasn't able to send the logs for `{0}` to your set channel. The channel and the track option \"CCED\" (Custom command edits) has been reset".format(message.server.name))
					except: pass
