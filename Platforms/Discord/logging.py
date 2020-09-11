from typing import TYPE_CHECKING, Dict
if TYPE_CHECKING:
	from .main_discord import PhaazebotDiscord

import discord
import traceback
import datetime
from Utils.Classes.discordserversettings import DiscordServerSettings
from Platforms.Discord.utils import getDiscordChannelFromString

# there is only a small amount, because most things are handled by discord audit logs
TRACK_OPTIONS:Dict[str, int] = {
	"Member.join": 1,
	"Member.remove": 1<<1,
	"Quote.create": 1<<2,
	"Quote.edit": 1<<3,
	"Quote.delete": 1<<4,
	"Command.create": 1<<5,
	"Command.edit": 1<<6,
	"Command.delete": 1<<7,
	"Twitchalert.create": 1<<8,
	"Twitchalert.edit": 1<<9,
	"Twitchalert.delete": 1<<10,
	"Regular.create": 1<<11,
	"Regular.delete": 1<<12,
	"Level.edit": 1<<13,
	"Levelmedal.create": 1<<14,
	"Levelmedal.delete": 1<<15,
	"Config.edit": 1<<16,
}
EVENT_COLOR_POSITIVE:int = 0x00FF00
EVENT_COLOR_WARNING:int = 0xFFAA00
EVENT_COLOR_NEGATIVE:int = 0xFF0000
EVENT_COLOR_INFO:int = 0x00FFFF

# Member.join : 1
async def loggingOnMemberJoin(cls:"PhaazebotDiscord", Settings:DiscordServerSettings, **kwargs:dict) -> None:
	"""
	Logs the event when a member is added (joins) a guild.
	If track option `Member.join` is active, it will send a message to discord

	Required keywords:
	------------------
	* NewMember `discord.Member`

	Optional keywords:
	------------------
	* link_in_name `bool` : (Default: False)
	"""
	NewMember:discord.Member = kwargs.get("NewMember", None)
	link_in_name:bool = kwargs.get("link_in_name", False)

	if not NewMember: raise AttributeError("missing `NewMember`")

	cls.BASE.PhaazeDB.insertQuery(
		table="discord_log",
		content={
			"guild_id": Settings.server_id,
			"event_value": TRACK_OPTIONS["Member.join"],
			"initiator_id": str(NewMember.id),
			"content": f"{NewMember.name} joined the server"
		}
	)

	if not (TRACK_OPTIONS["Member.join"] & Settings.track_value): return # track option not active, skip message to discord server

	TargetChannel:discord.TextChannel = getDiscordChannelFromString(cls, NewMember.guild, Settings.track_channel, required_type="text")
	if not TargetChannel: return # no channel found

	Emb:discord.Embed = discord.Embed(
		description = f"Initial name: {NewMember.name}\nMention: {NewMember.mention}\nID: {NewMember.id}",
		timestamp = datetime.datetime.now(),
		color = EVENT_COLOR_POSITIVE
	)
	Emb.set_thumbnail(url=NewMember.avatar_url or NewMember.default_avatar_url)
	Emb.set_author(name="Log Event - [Member Join]")
	if link_in_name:
		Emb.add_field(":warning: Blocked public announcements", "Link in name", inline=True)

	try:
		await TargetChannel.send(embed=Emb)
	except Exception as E:
		cls.BASE.Logger.warning(f"Can't log message: {E} {traceback.format_exc()}")

# Member.remove : 10
async def loggingOnMemberRemove(cls:"PhaazebotDiscord", Settings:DiscordServerSettings, **kwargs:dict) -> None:
	"""
	Logs the event when a member was removed from a guild.
	If track option `Member.remove` is active, it will send a message to discord

	Required keywords:
	------------------
	* OldMember `discord.Member`

	Optional keywords:
	------------------
	* link_in_name `bool` : (Default: False)
	"""
	OldMember:discord.Member = kwargs.get("OldMember", None)
	link_in_name:bool = kwargs.get("link_in_name", False)

	if not OldMember: raise AttributeError("missing `OldMember`")

	cls.BASE.PhaazeDB.insertQuery(
		table="discord_log",
		content={
			"guild_id": Settings.server_id,
			"event_value": TRACK_OPTIONS["Member.remove"],
			"initiator_id": str(OldMember.id),
			"content": f"{OldMember.name} left the server"
		}
	)

	if not (TRACK_OPTIONS["Member.remove"] & Settings.track_value): return # track option not active, skip message to discord server

	TargetChannel:discord.TextChannel = getDiscordChannelFromString(cls, OldMember.guild, Settings.track_channel, required_type="text")
	if not TargetChannel: return # no channel found

	Emb:discord.Embed = discord.Embed(
		description = f"User name: {OldMember.name}\nLast known nickname: {OldMember.nick}\nMention: {OldMember.mention}\nID: {OldMember.id}",
		timestamp = datetime.datetime.now(),
		color = EVENT_COLOR_NEGATIVE
	)
	Emb.set_thumbnail(url=OldMember.avatar_url or OldMember.default_avatar_url)
	Emb.set_author(name="Log Event - [Member remove]")
	if link_in_name:
		Emb.add_field(":warning: Blocked public announcements", "Link in name", inline=True)

	try:
		await TargetChannel.send(embed=Emb)
	except Exception as E:
		cls.BASE.Logger.warning(f"Can't log message: {E} {traceback.format_exc()}")

# Quote.create : 100
async def loggingOnQuoteCreate(cls:"PhaazebotDiscord", Settings:DiscordServerSettings, **kwargs:dict) -> None:
	"""
	Logs the event when someone creates a new quote, doesn't matter if in discord or web.
	If track option `Quote.create` is active, it will send a message to discord

	Required keywords:
	------------------
	* Creator `discord.Member`
	* quote_content `str`
	* quote_id `str`
	"""
	Creator:discord.Member = kwargs.get("Creator", None)
	quote_content:str = kwargs.get("quote_content", None)
	quote_id:str = kwargs.get("quote_id", None)

	if not Creator: raise AttributeError("missing `Creator`")
	if not quote_content: raise AttributeError("missing `quote_content`")
	if not quote_id: raise AttributeError("missing `quote_id`")

	cls.BASE.PhaazeDB.insertQuery(
		table="discord_log",
		content={
			"guild_id": Settings.server_id,
			"event_value": TRACK_OPTIONS["Quote.create"],
			"initiator_id": str(Creator.id),
			"content": f"New Quote Created (#{quote_id}): {quote_content}"
		}
	)

	if not (TRACK_OPTIONS["Quote.create"] & Settings.track_value): return # track option not active, skip message to discord server

	TargetChannel:discord.TextChannel = getDiscordChannelFromString(cls, Creator.guild, Settings.track_channel, required_type="text")
	if not TargetChannel: return # no channel found

	Emb:discord.Embed = discord.Embed(
		description = f"{Creator.name} created a new quote. (#{quote_id})",
		timestamp = datetime.datetime.now(),
		color = EVENT_COLOR_INFO
	)
	Emb.set_thumbnail(url=Creator.avatar_url or Creator.default_avatar_url)
	Emb.set_author(name="Log Event - [Quote Create]")
	Emb.add_field(name="Content:", value=quote_content[:500], inline=True)

	try:
		await TargetChannel.send(embed=Emb)
	except Exception as E:
		cls.BASE.Logger.warning(f"Can't log message: {E} {traceback.format_exc()}")

# Quote.edit : 1000
async def loggingOnQuoteEdit(cls:"PhaazebotDiscord", Settings:DiscordServerSettings, **kwargs:dict) -> None:
	"""
	Logs the event when someone edits a quote, doesn't matter if in discord or web. (You can only do this in web duh)
	If track option `Quote.create` is active, it will send a message to discord

	Required keywords:
	------------------
	* ChangeMember `discord.Member`
	* quote_id `str`
	* old_content `str`
	* new_content `str`
	"""
	ChangeMember:discord.Member = kwargs.get("ChangeMember", None)
	quote_id:str = kwargs.get("quote_id", None)
	old_content:str = kwargs.get("old_content", None)
	new_content:str = kwargs.get("new_content", None)

	if not ChangeMember: raise AttributeError("missing `ChangeMember`")
	if not quote_id: raise AttributeError("missing `quote_id`")
	if not old_content: raise AttributeError("missing `old_content`")
	if not new_content: raise AttributeError("missing `new_content`")

	cls.BASE.PhaazeDB.insertQuery(
		table="discord_log",
		content={
			"guild_id": Settings.server_id,
			"event_value": TRACK_OPTIONS["Quote.edit"],
			"initiator_id": str(ChangeMember.id),
			"content": f"Quote (#{quote_id}) Updated: {old_content} -> {new_content}"
		}
	)

	if not (TRACK_OPTIONS["Quote.edit"] & Settings.track_value): return # track option not active, skip message to discord server

	TargetChannel:discord.TextChannel = getDiscordChannelFromString(cls, ChangeMember.guild, Settings.track_channel, required_type="text")
	if not TargetChannel: return # no channel found

	Emb:discord.Embed = discord.Embed(
		description = f"{ChangeMember.name} changed a quote.",
		timestamp = datetime.datetime.now(),
		color = EVENT_COLOR_WARNING
	)
	Emb.set_thumbnail(url=ChangeMember.avatar_url or ChangeMember.default_avatar_url)
	Emb.set_author(name="Log Event - [Quote Edit]")
	Emb.add_field(name="Content:", value=f"{old_content[:500]} -> {new_content[:500]}", inline=True)

	try:
		await TargetChannel.send(embed=Emb)
	except Exception as E:
		cls.BASE.Logger.warning(f"Can't log message: {E} {traceback.format_exc()}")

# Quote.delete : 10000
async def loggingOnQuoteDelete(cls:"PhaazebotDiscord", Settings:DiscordServerSettings, **kwargs:dict) -> None:
	"""
	Logs the event when someone deletes a quote, doesn't matter if in discord or web.
	If track option `Quote.create` is active, it will send a message to discord

	Required keywords:
	------------------
	* Deleter `discord.Member`
	* quote_id `str`
	* deleted_content `str`
	"""
	Deleter:discord.Member = kwargs.get("Deleter", None)
	quote_id:str = kwargs.get("quote_id", None)
	deleted_content:str = kwargs.get("deleted_content", None)

	if not Deleter: raise AttributeError("missing `Deleter`")
	if not quote_id: raise AttributeError("missing `quote_id`")
	if not deleted_content: raise AttributeError("missing `deleted_content`")

	cls.BASE.PhaazeDB.insertQuery(
		table="discord_log",
		content={
			"guild_id": Settings.server_id,
			"event_value": TRACK_OPTIONS["Quote.delete"],
			"initiator_id": str(Deleter.id),
			"content": f"Quote (#{quote_id}) deleted: {deleted_content}"
		}
	)

	if not (TRACK_OPTIONS["Quote.delete"] & Settings.track_value): return # track option not active, skip message to discord server

	TargetChannel:discord.TextChannel = getDiscordChannelFromString(cls, Deleter.guild, Settings.track_channel, required_type="text")
	if not TargetChannel: return # no channel found

	Emb:discord.Embed = discord.Embed(
		description = f"{Deleter.name} deleted a quote.",
		timestamp = datetime.datetime.now(),
		color = EVENT_COLOR_NEGATIVE
	)
	Emb.set_thumbnail(url=Deleter.avatar_url or Deleter.default_avatar_url)
	Emb.set_author(name="Log Event - [Quote Deleted]")
	Emb.add_field(name="Content:", value=deleted_content[:500], inline=True)

	try:
		await TargetChannel.send(embed=Emb)
	except Exception as E:
		cls.BASE.Logger.warning(f"Can't log message: {E} {traceback.format_exc()}")

# Command.create : 100000
async def loggingOnCommandCreate(cls:"PhaazebotDiscord", Settings:DiscordServerSettings, **kwargs:dict) -> None:
	"""
	Logs the event when someone creates a new command (mostly) via web.
	If track option `Command.create` is active, it will send a message to discord

	Required keywords:
	------------------
	* Creator `discord.Member`
	* command_trigger `str`
	* command_info `dict`
	"""
	Creator:discord.Member = kwargs.get("Creator", None)
	command_trigger:str = kwargs.get("command_trigger", None)
	command_info:dict = kwargs.get("command_info", None)

	if not Creator: raise AttributeError("missing `Creator`")
	if not command_trigger: raise AttributeError("missing `command_trigger`")
	if not command_info: raise AttributeError("missing `command_info`")

	cls.BASE.PhaazeDB.insertQuery(
		table="discord_log",
		content={
			"guild_id": Settings.server_id,
			"event_value": TRACK_OPTIONS["Command.create"],
			"initiator_id": str(Creator.id),
			"content": f"Command ({command_trigger}) created. {str(command_info)}"
		}
	)

	if not (TRACK_OPTIONS["Command.create"] & Settings.track_value): return # track option not active, skip message to discord server

	TargetChannel:discord.TextChannel = getDiscordChannelFromString(cls, Creator.guild, Settings.track_channel, required_type="text")
	if not TargetChannel: return # no channel found

	Emb:discord.Embed = discord.Embed(
		description = f"{Creator.name} created a command.",
		timestamp = datetime.datetime.now(),
		color = EVENT_COLOR_POSITIVE
	)
	Emb.set_thumbnail(url=Creator.avatar_url or Creator.default_avatar_url)
	Emb.set_author(name="Log Event - [Command Created]")
	Emb.add_field(name="New Trigger:", value=command_trigger, inline=True)

	try:
		await TargetChannel.send(embed=Emb)
	except Exception as E:
		cls.BASE.Logger.warning(f"Can't log message: {E} {traceback.format_exc()}")
