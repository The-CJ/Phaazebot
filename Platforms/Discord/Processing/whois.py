from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Discord.main_discord import PhaazebotDiscord

import discord
import datetime
import tabulate
from Utils.Classes.discordcommand import DiscordCommand
from Utils.Classes.discordcommandcontext import DiscordCommandContext
from Platforms.Discord.utils import getDiscordMemberFromString

async def whois(cls:"PhaazebotDiscord", Command:DiscordCommand, CommandContext:DiscordCommandContext) -> dict:

	Member:discord.Member = None

	search_from:str = " ".join([x for x in CommandContext.parts[1:]])
	# no search use author
	if not search_from:
		Member = CommandContext.Message.author
	# try a search
	else:
		Member:discord.Member = getDiscordMemberFromString(cls, Guild=CommandContext.Message.guild, search=search_from, Message=CommandContext.Message)
		if not Member:
			return {"content": ":warning: Could not find a user with your query"}

	nickname:str = None
	status:str = None
	roles:list = list()

	# nickname
	if Member.nick:
		nickname = f"Nickname: {Member.nick}"

	# status
	if str(Member.status) == "online":
		status = "Online"
	elif str(Member.status) == "offline":
		status = "Offline"
	elif str(Member.status) == "idle":
		status = "AFK"
	elif str(Member.status) == "dnd":
		status = "Do not disturb"
	else:
		status = str(Member.status)

	for Role in sorted(Member.roles, key=lambda role: role.position, reverse=True):
		if Role.name != "@everyone":
			roles.append([Role.position, Role.name])

	Now:datetime.datetime = datetime.datetime.now()

	create_date:str = Member.created_at.strftime("%Y-%m-%d (%H:%M)")
	join_date:str = Member.joined_at.strftime("%Y-%m-%d (%H:%M)")
	create_days:str = (Now - Member.created_at).days
	join_days:str = (Now - Member.joined_at).days

	main_info:str = f"**ID**: {Member.id}\n"\
		f"**Discriminator**: {Member.discriminator}\n"\
		f"**Acc. created at**: {create_date} *[{create_days} days ago]*\n"\
		f"**Joined at**: {join_date} *[{join_days} days ago]*"

	Emb = discord.Embed (
		title=nickname,
		color=Member.color.value,
		description=main_info)

	Emb.set_author(name=f"Name: {Member.name}")
	Emb.add_field(name=":satellite: Status:",value=status,inline=True)

	if Member.activity:
		if type(Member.activity) == discord.activity.Game:
			Emb.add_field(name=":game_die: Playing:", value=str(Member.activity),inline=True)

		elif type(Member.activity) == discord.activity.Streaming:
			Emb.add_field(name=":video_camera: Currently Streaming:",value=str(Member.activity),inline=True)

	if Member.bot:
		Emb.add_field(name=":robot: Bot-account:",value="True",inline=True)

	if len(roles) >= 1:
		formated_list:str = tabulate.tabulate(roles, tablefmt="plain")
		Emb.add_field(name=":notepad_spiral: Roles:", value=f"```{formated_list}```", inline=False)
	else:
		Emb.add_field(name=":notepad_spiral: Roles:", value="None", inline=False)

	if Member.avatar_url:
		Emb.set_image(url=Member.avatar_url)
	else:
		Emb.set_image(url=Member.default_avatar_url)

	return {"embed": Emb}
