##BASE.moduls.Help

import asyncio, discord

cmds = 	[
		"custom", "doujin", "phaaze", "help", "addcom", "delcom",
		"blacklist", "settings", "commands","command", "quote", "define", "wiki",
		"whois", "serverinfo", "level", "master", "about", "welcome", "leave", "logs",
		"twitch", "leaderboard", "autorole", "news"
		]

async def base(BASE, message):
	formated_message = message.content.lower().replace(BASE.vars.PT, "")
	check = formated_message.split(" ")

	if len(check) == 1:
		return await HELP_RESPONSE.main(BASE, message)

	if not check[1] in cmds:
		return await HELP_RESPONSE.Not_a_cmd(BASE, message)

	if check[1] == "custom":
		return await HELP_RESPONSE.custom(BASE, message)

	if check[1] == "doujin":
		return await HELP_RESPONSE.doujin(BASE, message)

	if check[1] == "phaaze":
		return await HELP_RESPONSE.phaaze(BASE, message)

	if check[1] == "help":
		return await HELP_RESPONSE.help(BASE, message)

	if check[1] == "addcom":
		return await HELP_RESPONSE.addcom(BASE, message)

	if check[1] == "delcom":
		return await HELP_RESPONSE.delcom(BASE, message)

	if check[1] == "blacklist":
		return await HELP_RESPONSE.blacklist(BASE, message)

	if check[1] == "settings":
		return await HELP_RESPONSE.settings(BASE, message)

	if check[1] in ["commands", "command"]:
		return await HELP_RESPONSE.commands(BASE, message)

	if check[1] == "quote":
		return await HELP_RESPONSE.quote(BASE, message)

	if check[1] == "define":
		return await HELP_RESPONSE.define(BASE, message)

	if check[1] == "wiki":
		return await HELP_RESPONSE.wiki(BASE, message)

	if check[1] == "whois":
		return await HELP_RESPONSE.whois(BASE, message)

	if check[1] == "serverinfo":
		return await HELP_RESPONSE.serverinfo(BASE, message)

	if check[1] == "level":
		return await HELP_RESPONSE.level(BASE, message)

	if check[1] == "master":
		return await HELP_RESPONSE.master(BASE, message)

	if check[1] == "about":
		return await HELP_RESPONSE.about(BASE, message)

	if check[1] == "welcome":
		return await HELP_RESPONSE.welcome(BASE, message)

	if check[1] == "leave":
		return await HELP_RESPONSE.leave(BASE, message)

	if check[1] == "logs":
		return await HELP_RESPONSE.logs(BASE, message)

	if check[1] == "twitch":
		return await HELP_RESPONSE.twitch(BASE, message)

	if check[1] == "leaderboard":
		return await HELP_RESPONSE.leaderboard(BASE, message)

	if check[1] == "autorole":
		return await HELP_RESPONSE.leaderboard(BASE, message)

	if check[1] == "news":
		return await HELP_RESPONSE.news(BASE, message)



class HELP_RESPONSE:
	async def main(BASE, message):
		res = discord.Embed(
							title="Main help",
							color=int(0x00FFD0),
							description="For a list of all commands type: `{0}commands`\n"\
										"Based on your access level (normal/mod/owner) you get all commands you can use on the server via a PM.:incoming_envelope:\n\n"\
										"If you need help for a command you can use: `{0}help [command name]`\n"\
										"Also accessable via {1} DM\n\n".format(BASE.vars.PT, BASE.phaaze.user.mention))
		res.set_author(name="Help", icon_url=BASE.vars.app.icon_url)
		res.add_field(name="Command Access Level", value="`{0}` No requirement \n`{0}{0}` A role that contains \"mod\", \"admin\" or \"bot commander\"\n`{0}{0}{0}` server owner only".format(BASE.vars.PT), inline=False)
		res.add_field(name="Intresed in stats?", value="Type `{0}phaaze` to get the status of the PhaazeOS:tm:,\nincluding Discord, Twitch, Twitter, osu!, etc..".format(BASE.vars.PT), inline=False)
		#res.add_field(name="Need more help?", value="Look at the Wiki: https://github.com/The-CJ/Phaazebot/wiki", inline=False)
		res.add_field(name="Need even more help?", value="Join the offical Phaaze Server and ask the community or the creator for help,\nmake suggestions or report bugs.\nhttps://discord.gg/ZymrebS | https://discord.me/phaaze", inline=False)
		res.set_footer(text="Also helpful --> '{0}about' to get Bot invite links for all platforms".format(BASE.vars.PT))
		return await BASE.phaaze.send_message(message.channel, content=message.author.mention, embed=res)

	async def Not_a_cmd(BASE, message):
		m = message.content.lower().split(" ")
		res = discord.Embed(
							title=":exclamation: Unknown command",
							color=int(0xFF5500),
							description="`{0}` is not a Phaaze command, try `{1}commands` or just `{1}help`".format(m[1], BASE.vars.PT))
		res.set_author(name="Help", icon_url=BASE.vars.app.icon_url)
		return await BASE.phaaze.send_message(message.channel, content=message.author.mention, embed=res)

	##

	async def custom(BASE, message):
		m = message.content.lower().split(" ")
		res = discord.Embed(
							title="{0}custom".format(BASE.vars.PT),
							color=int(0x00FFD0),
							description="This will return a list of all available commands of a server\n\n"\
							":speech_balloon: Commands can be set by a moderator or higher,\n"\
							"		but also disabled in set channels")
		res.set_author(name="Help", icon_url=BASE.vars.app.icon_url)
		return await BASE.phaaze.send_message(message.channel, content=message.author.mention, embed=res)

	async def doujin(BASE, message):
		m = message.content.lower().split(" ")
		res = discord.Embed(

							title="{0}doujin".format(BASE.vars.PT),
							color=int(0x00FFD0),
							description="Returns a doujin by the search criteria\n\n"\
							":speech_balloon: This command is very complex, for a detailed \"How To\", use `{0}doujin help` (PM response),\n"\
							":grey_exclamation: Can only used in enabled channels".format(BASE.vars.PT))
		res.set_author(name="Help", icon_url=BASE.vars.app.icon_url)
		res.set_footer(text="Provided by Tsumino", icon_url="http://www.tsumino.com/content/res/logo.png")
		return await BASE.phaaze.send_message(message.channel, content=message.author.mention, embed=res)

	async def phaaze(BASE, message):
		m = message.content.lower().split(" ")
		res = discord.Embed(
							title="{0}phaaze".format(BASE.vars.PT),
							color=int(0x00FFD0),
							description="Returns the status and all stats of the PhaazeOS to you.\n\n"\
							":speech_balloon: Including stats from Twitch, Discord, osu!, Twitter and more.".format(BASE.vars.PT))
		res.set_author(name="Help", icon_url=BASE.vars.app.icon_url)
		return await BASE.phaaze.send_message(message.channel, content=message.author.mention, embed=res)

	async def help(BASE, message):
		m = message.content.lower().split(" ")
		res = discord.Embed(
							title="{0}help".format(BASE.vars.PT),
							color=int(0x00FFD0),
							description="Gives you help and infomation about a given command.\n\n"\
							"Usage:  `{0}help [command]`\n"\
							":speech_balloon: Typing \"{0}help help\" is pretty much the same as to google, \"google\"".format(BASE.vars.PT))
		res.set_author(name="Help", icon_url=BASE.vars.app.icon_url)
		return await BASE.phaaze.send_message(message.channel, content=message.author.mention, embed=res)

	async def addcom(BASE, message):
		m = message.content.lower().split(" ")
		res = discord.Embed(
							title="{0}{0}addcom".format(BASE.vars.PT),
							color=int(0x00FFD0),
							description="Allows mods and higher to add/edit custom commands.\n\n"\
							"Usage:  `{0}{0}addcom [trigger] [text]`\n\n"\
							"`[trigger]` can only be one word.\n"\
							"`[text]` is the awnser of the command, tokens can be used and will be replaced with info\n\n"\
							"__Tokens:__\n"\
							"[user] - Member who triggered the command\n"\
							"[server] - Server the command has been triggered\n"\
							"[count] - Number of members the server has right now\n"\
							"[mention] - @ mention the member\n"\
							"[uses] - How many times a command has been used".format(BASE.vars.PT))
		res.set_author(name="Help", icon_url=BASE.vars.app.icon_url)
		return await BASE.phaaze.send_message(message.channel, content=message.author.mention, embed=res)

	async def delcom(BASE, message):
		m = message.content.lower().split(" ")
		res = discord.Embed(
							title="{0}{0}delcom".format(BASE.vars.PT),
							color=int(0x00FFD0),
							description="Allows mods and higher to remove a custom command.\n\n"\
							"Usage:  `{0}{0}delcom [command]`".format(BASE.vars.PT))
		res.set_author(name="Help", icon_url=BASE.vars.app.icon_url)
		return await BASE.phaaze.send_message(message.channel, content=message.author.mention, embed=res)

	async def blacklist(BASE, message):
		m = message.content.lower().split(" ")
		res = discord.Embed(
							title="{0}{0}blacklist".format(BASE.vars.PT),
							color=int(0x00FFD0),
							description="Allows mods and higher to add/remove banned words.\n\n"\
							":speech_balloon: Messages that contain banned words will be deleted.\n"\
							":grey_exclamation: Phaaze need the `Manage Messages` Permission\n\nOptions:".format(BASE.vars.PT))
		res.add_field(name="{0}{0}blacklist get".format(BASE.vars.PT), value="Returns all blacklisted words.", inline=False)
		res.add_field(name="{0}{0}blacklist clear".format(BASE.vars.PT), value="Clears the blacklist completely.", inline=False)
		res.add_field(name="{0}{0}blacklist add [word]".format(BASE.vars.PT), value="Adds a word or phrase to the blacklist.", inline=False)
		res.add_field(name="{0}{0}blacklist rem [word]".format(BASE.vars.PT), value="Removes a word or phrase from the blacklist.", inline=False)
		res.set_author(name="Help", icon_url=BASE.vars.app.icon_url)
		return await BASE.phaaze.send_message(message.channel, content=message.author.mention, embed=res)

	async def settings(BASE, message):
		m = message.content.lower().split(" ")
		res = discord.Embed(
							title="{0}{0}settings".format(BASE.vars.PT),
							color=int(0x00FFD0),
							description="Allows mods and higher to enable or disable parts of Phaaze, for each channel,\n\n"\
							"Usage: `{0}{0}settings [option]`\n"\
							":speech_balloon: This Command is needed to use certain commands.".format(BASE.vars.PT))
		res.add_field(name="Available Options:", value=" - ".join("`"+g+"`" for g in BASE.moduls.Mod_Commands.Available), inline=False)
		res.set_author(name="Help", icon_url=BASE.vars.app.icon_url)
		return await BASE.phaaze.send_message(message.channel, content=message.author.mention, embed=res)

	async def commands(BASE, message):
		m = message.content.lower().split(" ")
		res = discord.Embed(
							title="{0}command".format(BASE.vars.PT),
							color=int(0x00FFD0),
							description="That will return all commands you can use on a server. (via PM)\n\n"\
							":speech_balloon: The response is based on your access level (normal, mod, server owner).".format(BASE.vars.PT))
		res.set_author(name="Help", icon_url=BASE.vars.app.icon_url)
		return await BASE.phaaze.send_message(message.channel, content=message.author.mention, embed=res)

	async def quote(BASE, message):
		m = message.content.lower().split(" ")
		res = discord.Embed(
							title="{0}quote and {0}{0}quote".format(BASE.vars.PT),
							color=int(0x00FFD0))
							#description="\n\n".format(BASE.vars.PT))
		res.add_field(name="{0}quote	(normal command)".format(BASE.vars.PT), value="`{0}quote` - returns a random qoute, but you can add a number after quote to get the quote from the index (if available)".format(BASE.vars.PT), inline=False)
		res.add_field(name="{0}{0}quote	(mod command)".format(BASE.vars.PT), value="`{0}{0}quote add [quote]` - To add a new quote\n`{0}{0}quote rem [indexnumber]` - To delete a quote\n`{0}{0}quote clear` - To delete all quotes".format(BASE.vars.PT), inline=False)
		res.set_author(name="Help", icon_url=BASE.vars.app.icon_url)
		return await BASE.phaaze.send_message(message.channel, content=message.author.mention, embed=res)

	async def define(BASE, message):
		m = message.content.lower().split(" ")
		res = discord.Embed(
							title="{0}define".format(BASE.vars.PT),
							color=int(0x00FFD0),
							description="Tryes to define the given term.\n\n"\
							"Usage: `{0}define [stuff you wanna define]`".format(BASE.vars.PT))
		res.set_author(name="Help", icon_url=BASE.vars.app.icon_url)
		res.set_footer(text="Provided by Urban dictionary",icon_url="https://lh5.ggpht.com/oJ67p2f1o35dzQQ9fVMdGRtA7jKQdxUFSQ7vYstyqTp-Xh-H5BAN4T5_abmev3kz55GH=w300")
		return await BASE.phaaze.send_message(message.channel, content=message.author.mention, embed=res)

	async def wiki(BASE, message):
		m = message.content.lower().split(" ")
		res = discord.Embed(
							title="{0}wiki".format(BASE.vars.PT),
							color=int(0x00FFD0),
							description="Ask Wikipedia about everything, tryes to autocomplete searches and and giving you suggestions.\n\n"\
							"Usage: `{0}wiki(lang) [stuff]`\n"\
							"`(lang)` - Can be empty or used with a \"/\" to change the return language e.g.: `{0}wiki/de Apfelbaum`, Default is \"en\"\n"\
							"`[thing]` - Whatever you wanna search\n\n"\
							":exclamation: `{0}wiki` use a lot API requests, thats why this command has a extra 15s cooldown per user".format(BASE.vars.PT))
		res.set_author(name="Help", icon_url=BASE.vars.app.icon_url)
		res.set_footer(text="Provided by Wikipedia",icon_url="https://upload.wikimedia.org/wikipedia/en/archive/2/28/20150803040129!WikipediaMobileAppLogo.png")
		return await BASE.phaaze.send_message(message.channel, content=message.author.mention, embed=res)

	async def whois(BASE, message):
		m = message.content.lower().split(" ")
		res = discord.Embed(
							title="{0}whois".format(BASE.vars.PT),
							color=int(0x00FFD0),
							description="Gives you a lot of informations about a user.\n\n"\
							"Usage: `{0}whois (member)`\n\n"\
							"`(member)` - Can be a @mention, the id, the exact name **Not nickname** or leave it empty to get you".format(BASE.vars.PT))
		res.set_author(name="Help", icon_url=BASE.vars.app.icon_url)
		return await BASE.phaaze.send_message(message.channel, content=message.author.mention, embed=res)

	async def serverinfo(BASE, message):
		m = message.content.lower().split(" ")
		res = discord.Embed(
							title="{0}{0}serverinfo".format(BASE.vars.PT),
							color=int(0x00FFD0),
							description="Gives you a lot of informations about the server you are using this command.")
		res.set_author(name="Help", icon_url=BASE.vars.app.icon_url)
		return await BASE.phaaze.send_message(message.channel, content=message.author.mention, embed=res)

	async def level(BASE, message):
		m = message.content.lower().split(" ")
		res = discord.Embed(
							title="{0}level and {0}{0}level".format(BASE.vars.PT),
							color=int(0x00FFD0))
		res.add_field(name="{0}level	(normal command)".format(BASE.vars.PT), value="`{0}level` - returns your level on the Server (`{0}level calc X` for asking X Levels needed Exp)".format(BASE.vars.PT), inline=False)
		res.add_field(name="{0}{0}level	(mod command)".format(BASE.vars.PT), value="`{0}{0}level` - to edit users, exp, level, medals and more...".format(BASE.vars.PT), inline=False)
		res.set_author(name="Help", icon_url=BASE.vars.app.icon_url)
		return await BASE.phaaze.send_message(message.channel, content=message.author.mention, embed=res)

	async def master(BASE, message):
		m = message.content.lower().split(" ")
		res = discord.Embed(
							title="{0}{0}{0}master".format(BASE.vars.PT),
							color=int(0x00FFD0),
							description="Allows the owner to make serverwide changes to Phaaze behavior,\n\n"\
							"Usage: `{0}{0}{0}master [option]`\n"\
							":speech_balloon: This Command is very powerfull, be careful.".format(BASE.vars.PT))
		res.add_field(name="Available Options:", value=" - ".join("`"+g+"`" for g in BASE.cmds.OWNER.Available), inline=False)
		res.set_author(name="Help", icon_url=BASE.vars.app.icon_url)
		return await BASE.phaaze.send_message(message.channel, content=message.author.mention, embed=res)

	async def welcome(BASE, message):
		m = message.content.lower().split(" ")
		res = discord.Embed(
							title="{0}{0}{0}welcome".format(BASE.vars.PT),
							color=int(0x00FFD0),
							description="Allows the owner to set messages that greet new members,\n\n"\
							"Usage: `{0}{0}{0}welcome [Option]`\n"\
							"Options:".format(BASE.vars.PT))
		res.add_field(name="get", value="Returns the current welcome message and the channel it appears.", inline=False)
		res.add_field(name="getraw", value="Same as `get`, but unformated in a Code block", inline=False)
		res.add_field(name="set", value="Set the welcome message.\n(There are Token available, Type `{0}{0}{0}welcome set` without arguments to get them.)".format(BASE.vars.PT), inline=False)
		res.add_field(name="chan", value="Set the welcome channel, where the message appears. If none set, it appears in your server default channel (#general)".format(BASE.vars.PT), inline=False)
		res.add_field(name="priv", value="Set a message that Phaaze will send the new member via PM".format(BASE.vars.PT), inline=False)
		res.add_field(name="clear", value="Removes welcome message and channel back to none".format(BASE.vars.PT), inline=False)
		res.add_field(name="clearpriv", value="Removes the private message for new members".format(BASE.vars.PT), inline=False)
		res.add_field(name="--INFO--", value="If Phaaze cannot send the message because of missing permissions or to a deleted channel, it automatically clears the settings and give the server owner a call".format(BASE.vars.PT), inline=False)
		res.set_author(name="Help", icon_url=BASE.vars.app.icon_url)
		return await BASE.phaaze.send_message(message.channel, content=message.author.mention, embed=res)

	async def leave(BASE, message):
		m = message.content.lower().split(" ")
		res = discord.Embed(
							title="{0}{0}{0}leave".format(BASE.vars.PT),
							color=int(0x00FFD0),
							description="Allows the owner to set leave that appears when members leave,\n\n"\
							"Usage: `{0}{0}{0}leave [Option]`\n"\
							"Options:".format(BASE.vars.PT))
		res.add_field(name="get", value="Returns the current leave message and the channel it appears.", inline=False)
		res.add_field(name="getraw", value="Same as `get`, but unformated in a Code block", inline=False)
		res.add_field(name="set", value="Set the leave message.\n(There are Token available, Type `{0}{0}{0}leave set` without arguments to get them.)".format(BASE.vars.PT), inline=False)
		res.add_field(name="chan", value="Set the leave channel, where the message appears. If none set, it appears in your server default channel (#general)".format(BASE.vars.PT), inline=False)
		res.add_field(name="clear", value="Removes leave message and channel back to none".format(BASE.vars.PT), inline=False)
		res.add_field(name="--INFO--", value="If Phaaze cannot send the message because of missing permissions or to a deleted channel, it automatically  clears the settings and give the server owner a call".format(BASE.vars.PT), inline=False)
		res.set_author(name="Help", icon_url=BASE.vars.app.icon_url)
		return await BASE.phaaze.send_message(message.channel, content=message.author.mention, embed=res)

	async def about(BASE, message):
		m = message.content.lower().split(" ")
		res = discord.Embed(
							title="{0}about".format(BASE.vars.PT),
							color=int(0x00FFD0),
							description="Returns a quick summary what Phaaze is, togetheer with invite links for all platforms".format(BASE.vars.PT))
		res.set_author(name="Help", icon_url=BASE.vars.app.icon_url)
		return await BASE.phaaze.send_message(message.channel, content=message.author.mention, embed=res)

	async def logs(BASE, message):
		m = message.content.lower().split(" ")
		res = discord.Embed(
							title="{0}{0}{0}logs".format(BASE.vars.PT),
							color=int(0x00FFD0),
							description="Allows the owner to track every activity on the server,\n\n"\
							"Usage: `{0}{0}{0}logs [Option]`\n"\
							"Options:".format(BASE.vars.PT))
		res.add_field(name="track", value="`track` followed by a option turns a eventtrack on/off.", inline=False)
		res.add_field(name="chan", value="Set the track channel, where every event gets posted", inline=False)
		res.add_field(name="--INFO--", value="If Phaaze cannot send the message because of missing permissions or to a deleted channel, it automatically  clears the settings and give the server owner a call".format(BASE.vars.PT), inline=False)
		res.add_field(name="--WARNING--", value="Track gets temporaly disabled if the eventlimit get hit for 5min\n(Limit is based on Phaaze Global Traffic)".format(BASE.vars.PT), inline=False)
		res.set_author(name="Help", icon_url=BASE.vars.app.icon_url)
		return await BASE.phaaze.send_message(message.channel, content=message.author.mention, embed=res)

	async def twitch(BASE, message):
		m = message.content.lower().split(" ")
		res = discord.Embed(
							title="{0}{0}{0}twitch".format(BASE.vars.PT),
							color=int(0x00FFD0),
							description="Allows the owner to track twitch channels and send alerts on live or game change events,\n\n"\
							"Usage: `{0}{0}{0}twitch [Option]`\n"\
							"Options:".format(BASE.vars.PT))
		res.add_field(name="track", value="`track` followed by the Twitch channel **name (NOT LINK)** turns tracking in this channel on/off.", inline=False)
		res.add_field(name="custom", value="Allows the server owner to customize the message that appears on a Twitch event", inline=False)
		res.add_field(name="get", value="Returns all Twitch Channel that are announced in the Channel", inline=False)
		res.set_author(name="Help", icon_url=BASE.vars.app.icon_url)
		return await BASE.phaaze.send_message(message.channel, content=message.author.mention, embed=res)

	async def leaderboard(BASE, message):
		m = message.content.lower().split(" ")
		res = discord.Embed(
							title="{0}leaderboard".format(BASE.vars.PT),
							color=int(0x00FFD0),
							description="Returns a leaderboard with the top levels from the server,\n\n"\
							"Usage: `{0}leaderboard (number)`\n\n"\
							"`(number)` -Can be a Number from 1-15 or Empty (default: 5)".format(BASE.vars.PT))
		res.set_author(name="Help", icon_url=BASE.vars.app.icon_url)
		return await BASE.phaaze.send_message(message.channel, content=message.author.mention, embed=res)

	async def autorole(BASE, message):
		m = message.content.lower().split(" ")
		res = discord.Embed(
							title="{0}{0}{0}autorole".format(BASE.vars.PT),
							color=int(0x00FFD0),
							description="Allows the Server Owner to set a role, that every new member assigned to.\n\n"\
							"Usage: `{0}{0}{0}autorole [Role]`\n\n"\
							"`[Role]` - Mention, Name or ID from the role.".format(BASE.vars.PT))
		res.add_field(name="INFO:", value="Giving every new member a role on join will allow them to bypass Server security settings (Verify Email. etc.)", inline=False)
		res.set_author(name="Help", icon_url=BASE.vars.app.icon_url)
		return await BASE.phaaze.send_message(message.channel, content=message.author.mention, embed=res)

	async def news(BASE, message):
		m = message.content.lower().split(" ")
		res = discord.Embed(
							title="{0}{0}{0}news".format(BASE.vars.PT),
							color=int(0x00FFD0),
							description="If you run this command in a channel, the channel its been added to the global news feed.\nMeans you will see update posts from Phaaze")
		res.set_author(name="Help", icon_url=BASE.vars.app.icon_url)
		return await BASE.phaaze.send_message(message.channel, content=message.author.mention, embed=res)



































#
