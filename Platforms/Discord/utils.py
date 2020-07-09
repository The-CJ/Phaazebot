from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from .main_discord import PhaazebotDiscord

import discord

# utility functions
def getDiscordChannelFromString(cls:"PhaazebotDiscord", Guild:discord.Guild, search:str or int, Message:discord.Message=None, required_type:str=None) -> discord.abc.GuildChannel or None:
	"""
		Tryes to get a channel from a guild, the search input may be,
		the channel name or the id, else None is given

		Also can take Message mentions in account if Message given
	"""
	SearchChannel:discord.abc.GuildChannel = None

	search_str:str = str(search)
	search_id:int = 0
	if search_str.isdigit():
		search_id = int(search)

	# mention
	if Message:
		if Message.channel_mentions:
			SearchChannel = Message.channel_mentions[0]

	for Chan in Guild.channels:
		if (Chan.name == search_str) or (Chan.id == search_id):
			SearchChannel = Chan
			break

	# type check
	if required_type:
		if required_type == "text" and type(SearchChannel) is not discord.TextChannel:
			return None
		if required_type == "voice" and type(SearchChannel) is not discord.VoiceChannel:
			return None
		if required_type == "category" and type(SearchChannel) is not discord.CategoryChannel:
			return None

	return SearchChannel

def getDiscordMemberFromString(cls:"PhaazebotDiscord", Guild:discord.Guild, search:str or int, Message:discord.Message=None) -> discord.Member or None:
	"""
		Tryes to get a member from a guild, the search input may be,
		the user name or his id, else None is given

		Also can take Message mentions in account if Message given
	"""

	# mention
	if Message:
		if Message.mentions:
			return Message.mentions[0]

	search:str = str(search)
	Member:discord.Member = None

	# id
	if search.isdigit():
		Member = Guild.get_member(int(search))
		if Member: return Member

	# name
	Member = Guild.get_member_named(search)
	if Member:
		return Member

def getDiscordRoleFromString(cls:"PhaazebotDiscord", Guild:discord.Guild, search:str or int, Message:discord.Message=None) -> discord.Role or None:
	"""
		Tryes to get a role from a guild, the search input may be,
		the role name or the id, else None is given

		Also can take Message role mentions in account if Message given
	"""

	# mention
	if Message:
		if Message.role_mentions:
			return Message.role_mentions[0]

	search:str = str(search)

	for Ro in Guild.roles:
		if search.isdigit():
			if Ro.id == int(search): return Ro

		if Ro.name == search: return Ro
