from typing import TYPE_CHECKING, Dict
if TYPE_CHECKING:
	from .main_discord import PhaazebotDiscord

import discord
import traceback
import datetime
from Utils.Classes.discordserversettings import DiscordServerSettings
from Platforms.Discord.utils import getDiscordChannelFromString, getDiscordMemberFromString, getDiscordRoleFromString

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
	"Assignrole.create": 1<<16,
	"Assignrole.edit": 1<<17,
	"Assignrole.delete": 1<<18,
	"Config.edit": 1<<19,
}
EVENT_COLOR_POSITIVE:int = 0x00FF00
EVENT_COLOR_WARNING:int = 0xFFAA00
EVENT_COLOR_NEGATIVE:int = 0xFF0000
EVENT_COLOR_INFO:int = 0x00FFFF

# Member.join : 1 : 1
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
	logging_signature:str = "Member.join"
	NewMember:discord.Member = kwargs["NewMember"]
	link_in_name:bool = kwargs.get("link_in_name", False)

	cls.BASE.PhaazeDB.insertQuery(
		table="discord_log",
		content={
			"guild_id": Settings.server_id,
			"event_value": TRACK_OPTIONS[logging_signature],
			"initiator_id": str(NewMember.id),
			"content": f"{NewMember.name} joined the server"
		}
	)

	if not (TRACK_OPTIONS[logging_signature] & Settings.track_value): return # track option not active, skip message to discord server

	TargetChannel:discord.TextChannel = getDiscordChannelFromString(cls, NewMember.guild, Settings.track_channel, required_type="text")
	if not TargetChannel: return # no channel found

	Emb:discord.Embed = discord.Embed(
		description = f"Initial name: {NewMember.name}\nMention: {NewMember.mention}\nID: {NewMember.id}",
		timestamp = datetime.datetime.now(),
		color = EVENT_COLOR_POSITIVE
	)
	Emb.set_thumbnail(url=NewMember.avatar_url or NewMember.default_avatar_url)
	Emb.set_author(name=f"Log Event - [{logging_signature}]")
	if link_in_name:
		Emb.add_field(":warning: Blocked public announcements", "Link in name", inline=True)

	try:
		await TargetChannel.send(embed=Emb)
	except Exception as E:
		cls.BASE.Logger.warning(f"Can't log message: {E} {traceback.format_exc()}")

# Member.remove : 10 : 2
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
	logging_signature:str = "Member.remove"
	OldMember:discord.Member = kwargs["OldMember"]
	link_in_name:bool = kwargs.get("link_in_name", False)

	cls.BASE.PhaazeDB.insertQuery(
		table="discord_log",
		content={
			"guild_id": Settings.server_id,
			"event_value": TRACK_OPTIONS[logging_signature],
			"initiator_id": str(OldMember.id),
			"content": f"{OldMember.name} left the server"
		}
	)

	if not (TRACK_OPTIONS[logging_signature] & Settings.track_value): return # track option not active, skip message to discord server

	TargetChannel:discord.TextChannel = getDiscordChannelFromString(cls, OldMember.guild, Settings.track_channel, required_type="text")
	if not TargetChannel: return # no channel found

	Emb:discord.Embed = discord.Embed(
		description = f"User name: {OldMember.name}\nLast known nickname: {OldMember.nick}\nMention: {OldMember.mention}\nID: {OldMember.id}",
		timestamp = datetime.datetime.now(),
		color = EVENT_COLOR_NEGATIVE
	)
	Emb.set_thumbnail(url=OldMember.avatar_url or OldMember.default_avatar_url)
	Emb.set_author(name=f"Log Event - [{logging_signature}]")
	if link_in_name:
		Emb.add_field(":warning: Blocked public announcements", "Link in name", inline=True)

	try:
		await TargetChannel.send(embed=Emb)
	except Exception as E:
		cls.BASE.Logger.warning(f"Can't log message: {E} {traceback.format_exc()}")

# Quote.create : 100 : 4
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
	logging_signature:str = "Quote.create"
	Creator:discord.Member = kwargs["Creator"]
	quote_content:str = kwargs["quote_content"]
	quote_id:str = kwargs["quote_id"]

	cls.BASE.PhaazeDB.insertQuery(
		table="discord_log",
		content={
			"guild_id": Settings.server_id,
			"event_value": TRACK_OPTIONS[logging_signature],
			"initiator_id": str(Creator.id),
			"content": f"{Creator.name} created a new quote (#{quote_id}): {quote_content}"
		}
	)

	if not (TRACK_OPTIONS[logging_signature] & Settings.track_value): return # track option not active, skip message to discord server

	TargetChannel:discord.TextChannel = getDiscordChannelFromString(cls, Creator.guild, Settings.track_channel, required_type="text")
	if not TargetChannel: return # no channel found

	Emb:discord.Embed = discord.Embed(
		description = f"{Creator.name} created a new quote.",
		timestamp = datetime.datetime.now(),
		color = EVENT_COLOR_POSITIVE
	)
	Emb.set_thumbnail(url=Creator.avatar_url or Creator.default_avatar_url)
	Emb.set_author(name=f"Log Event - [{logging_signature}]")
	Emb.add_field(name="Content:", value=quote_content[:500], inline=True)

	try:
		await TargetChannel.send(embed=Emb)
	except Exception as E:
		cls.BASE.Logger.warning(f"Can't log message: {E} {traceback.format_exc()}")

# Quote.edit : 1000 : 8
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
	logging_signature:str = "Quote.edit"
	ChangeMember:discord.Member = kwargs["ChangeMember"]
	quote_id:str = kwargs["quote_id"]
	old_content:str = kwargs["old_content"]
	new_content:str = kwargs["new_content"]

	cls.BASE.PhaazeDB.insertQuery(
		table="discord_log",
		content={
			"guild_id": Settings.server_id,
			"event_value": TRACK_OPTIONS[logging_signature],
			"initiator_id": str(ChangeMember.id),
			"content": f"{ChangeMember.name} changed quote #{quote_id}: {old_content} -> {new_content}"
		}
	)

	if not (TRACK_OPTIONS[logging_signature] & Settings.track_value): return # track option not active, skip message to discord server

	TargetChannel:discord.TextChannel = getDiscordChannelFromString(cls, ChangeMember.guild, Settings.track_channel, required_type="text")
	if not TargetChannel: return # no channel found

	Emb:discord.Embed = discord.Embed(
		description = f"{ChangeMember.name} changed a quote.",
		timestamp = datetime.datetime.now(),
		color = EVENT_COLOR_WARNING
	)
	Emb.set_thumbnail(url=ChangeMember.avatar_url or ChangeMember.default_avatar_url)
	Emb.set_author(name=f"Log Event - [{logging_signature}]")
	Emb.add_field(name="Content:", value=f"{old_content[:500]} -> {new_content[:500]}", inline=True)

	try:
		await TargetChannel.send(embed=Emb)
	except Exception as E:
		cls.BASE.Logger.warning(f"Can't log message: {E} {traceback.format_exc()}")

# Quote.delete : 10000 : 16
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
	logging_signature:str = "Quote.delete"
	Deleter:discord.Member = kwargs["Deleter"]
	quote_id:str = kwargs["quote_id"]
	deleted_content:str = kwargs["deleted_content"]

	cls.BASE.PhaazeDB.insertQuery(
		table="discord_log",
		content={
			"guild_id": Settings.server_id,
			"event_value": TRACK_OPTIONS[logging_signature],
			"initiator_id": str(Deleter.id),
			"content": f"{Deleter.name} deleted quote #{quote_id}: {deleted_content}"
		}
	)

	if not (TRACK_OPTIONS[logging_signature] & Settings.track_value): return # track option not active, skip message to discord server

	TargetChannel:discord.TextChannel = getDiscordChannelFromString(cls, Deleter.guild, Settings.track_channel, required_type="text")
	if not TargetChannel: return # no channel found

	Emb:discord.Embed = discord.Embed(
		description = f"{Deleter.name} deleted a quote.",
		timestamp = datetime.datetime.now(),
		color = EVENT_COLOR_NEGATIVE
	)
	Emb.set_thumbnail(url=Deleter.avatar_url or Deleter.default_avatar_url)
	Emb.set_author(name=f"Log Event - [{logging_signature}]")
	Emb.add_field(name="Content:", value=deleted_content[:500], inline=True)

	try:
		await TargetChannel.send(embed=Emb)
	except Exception as E:
		cls.BASE.Logger.warning(f"Can't log message: {E} {traceback.format_exc()}")

# Command.create : 100000 : 32
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
	logging_signature:str = "Command.create"
	Creator:discord.Member = kwargs["Creator"]
	command_trigger:str = kwargs["command_trigger"]
	command_info:dict = kwargs["command_info"]

	cls.BASE.PhaazeDB.insertQuery(
		table="discord_log",
		content={
			"guild_id": Settings.server_id,
			"event_value": TRACK_OPTIONS[logging_signature],
			"initiator_id": str(Creator.id),
			"content": f"{Creator.name} created a new command ({command_trigger}) : {str(command_info)}"
		}
	)

	if not (TRACK_OPTIONS[logging_signature] & Settings.track_value): return # track option not active, skip message to discord server

	TargetChannel:discord.TextChannel = getDiscordChannelFromString(cls, Creator.guild, Settings.track_channel, required_type="text")
	if not TargetChannel: return # no channel found

	Emb:discord.Embed = discord.Embed(
		description = f"{Creator.name} created a command.",
		timestamp = datetime.datetime.now(),
		color = EVENT_COLOR_POSITIVE
	)
	Emb.set_thumbnail(url=Creator.avatar_url or Creator.default_avatar_url)
	Emb.set_author(name=f"Log Event - [{logging_signature}]")
	Emb.add_field(name="New Trigger:", value=command_trigger, inline=True)

	try:
		await TargetChannel.send(embed=Emb)
	except Exception as E:
		cls.BASE.Logger.warning(f"Can't log message: {E} {traceback.format_exc()}")

# Command.edit : 1000000 : 64
async def loggingOnCommandEdit(cls:"PhaazebotDiscord", Settings:DiscordServerSettings, **kwargs:dict) -> None:
	"""
	Logs the event when someone edits a command (mostly) via web.
	If track option `Command.edit` is active, it will send a message to discord

	Required keywords:
	------------------
	* Editor `discord.Member`
	* command_trigger `str`
	* command_info `dict`
	"""
	logging_signature:str = "Command.edit"
	Editor:discord.Member = kwargs["Editor"]
	command_trigger:str = kwargs["command_trigger"]
	command_info:dict = kwargs["command_info"]

	cls.BASE.PhaazeDB.insertQuery(
		table="discord_log",
		content={
			"guild_id": Settings.server_id,
			"event_value": TRACK_OPTIONS[logging_signature],
			"initiator_id": str(Editor.id),
			"content": f"{Editor.name} edited the command: {command_trigger} : {str(command_info)}"
		}
	)

	if not (TRACK_OPTIONS[logging_signature] & Settings.track_value): return # track option not active, skip message to discord server

	TargetChannel:discord.TextChannel = getDiscordChannelFromString(cls, Editor.guild, Settings.track_channel, required_type="text")
	if not TargetChannel: return # no channel found

	Emb:discord.Embed = discord.Embed(
		description = f"{Editor.name} edited a command.",
		timestamp = datetime.datetime.now(),
		color = EVENT_COLOR_WARNING
	)
	Emb.set_thumbnail(url=Editor.avatar_url or Editor.default_avatar_url)
	Emb.set_author(name=f"Log Event - [{logging_signature}]")
	Emb.add_field(name="Changed command:", value=command_trigger, inline=True)

	try:
		await TargetChannel.send(embed=Emb)
	except Exception as E:
		cls.BASE.Logger.warning(f"Can't log message: {E} {traceback.format_exc()}")

# Command.delete : 10000000 : 128
async def loggingOnCommandDelete(cls:"PhaazebotDiscord", Settings:DiscordServerSettings, **kwargs:dict) -> None:
	"""
	Logs the event when someone deletes a command (mostly) via web.
	If track option `Command.delete` is active, it will send a message to discord

	Required keywords:
	------------------
	* Deleter `discord.Member`
	* command_trigger `str`
	"""
	logging_signature:str = "Command.delete"
	Deleter:discord.Member = kwargs["Deleter"]
	command_trigger:str = kwargs["command_trigger"]

	cls.BASE.PhaazeDB.insertQuery(
		table="discord_log",
		content={
			"guild_id": Settings.server_id,
			"event_value": TRACK_OPTIONS[logging_signature],
			"initiator_id": str(Deleter.id),
			"content": f"{Deleter.name} deleted the command: {command_trigger}"
		}
	)

	if not (TRACK_OPTIONS[logging_signature] & Settings.track_value): return # track option not active, skip message to discord server

	TargetChannel:discord.TextChannel = getDiscordChannelFromString(cls, Deleter.guild, Settings.track_channel, required_type="text")
	if not TargetChannel: return # no channel found

	Emb:discord.Embed = discord.Embed(
		description = f"{Deleter.name} deleted a command.",
		timestamp = datetime.datetime.now(),
		color = EVENT_COLOR_NEGATIVE
	)
	Emb.set_thumbnail(url=Deleter.avatar_url or Deleter.default_avatar_url)
	Emb.set_author(name=f"Log Event - [{logging_signature}]")
	Emb.add_field(name="Deleted command:", value=command_trigger, inline=True)

	try:
		await TargetChannel.send(embed=Emb)
	except Exception as E:
		cls.BASE.Logger.warning(f"Can't log message: {E} {traceback.format_exc()}")

# Twitchalert.create : 100000000 : 256
async def loggingOnTwitchalertCreate(cls:"PhaazebotDiscord", Settings:DiscordServerSettings, **kwargs:dict) -> None:
	"""
	Logs the event when someone creates a new twitch alert (mostly) via web.
	If track option `Twitchalert.create` is active, it will send a message to discord

	Required keywords:
	------------------
	* Creator `discord.Member`
	* twitch_channel `str`
	* discord_channel `str`
	"""
	logging_signature:str = "Twitchalert.create"
	Creator:discord.Member = kwargs["Creator"]
	twitch_channel:str = kwargs["twitch_channel"]
	discord_channel:str = kwargs["discord_channel"]

	cls.BASE.PhaazeDB.insertQuery(
		table="discord_log",
		content={
			"guild_id": Settings.server_id,
			"event_value": TRACK_OPTIONS[logging_signature],
			"initiator_id": str(Creator.id),
			"content": f"{Creator.name} created a new Twitch-Alert for {twitch_channel} in #{discord_channel}"
		}
	)

	if not (TRACK_OPTIONS[logging_signature] & Settings.track_value): return # track option not active, skip message to discord server

	TargetChannel:discord.TextChannel = getDiscordChannelFromString(cls, Creator.guild, Settings.track_channel, required_type="text")
	if not TargetChannel: return # no channel found

	Emb:discord.Embed = discord.Embed(
		description = f"{Creator.name} created a Twitch-Alert.",
		timestamp = datetime.datetime.now(),
		color = EVENT_COLOR_POSITIVE
	)
	Emb.set_thumbnail(url=Creator.avatar_url or Creator.default_avatar_url)
	Emb.set_author(name=f"Log Event - [{logging_signature}]")
	Emb.add_field(name="Twitch channel:", value=twitch_channel, inline=False)
	Emb.add_field(name="Discord channel:", value='#'+discord_channel, inline=False)

	try:
		await TargetChannel.send(embed=Emb)
	except Exception as E:
		cls.BASE.Logger.warning(f"Can't log message: {E} {traceback.format_exc()}")

# Twitchalert.edit : 1000000000 : 512
async def loggingOnTwitchalertEdit(cls:"PhaazebotDiscord", Settings:DiscordServerSettings, **kwargs:dict) -> None:
	"""
	Logs the event when someone changes a twitch alert (mostly) via web.
	If track option `Twitchalert.edit` is active, it will send a message to discord

	Required keywords:
	------------------
	* ChangeMember `discord.Member`
	* twitch_channel `str`
	* discord_channel_id `str`
	* changes `dict`
	"""
	logging_signature:str = "Twitchalert.edit"
	ChangeMember:discord.Member = kwargs["ChangeMember"]
	twitch_channel:str = kwargs["twitch_channel"]
	discord_channel_id:str = kwargs["discord_channel_id"]
	changes:str = kwargs["changes"]

	Chan:discord.TextChannel = getDiscordChannelFromString(cls, ChangeMember.guild, discord_channel_id, required_type="text")
	discord_channel_name:str = Chan.name if Chan else "(Unknown)"

	cls.BASE.PhaazeDB.insertQuery(
		table="discord_log",
		content={
			"guild_id": Settings.server_id,
			"event_value": TRACK_OPTIONS[logging_signature],
			"initiator_id": str(ChangeMember.id),
			"content": f"{ChangeMember.name} changed the Twitch-Alert for {twitch_channel} in #{discord_channel_name}: {str(changes)}"
		}
	)

	if not (TRACK_OPTIONS[logging_signature] & Settings.track_value): return # track option not active, skip message to discord server

	TargetChannel:discord.TextChannel = getDiscordChannelFromString(cls, ChangeMember.guild, Settings.track_channel, required_type="text")
	if not TargetChannel: return # no channel found

	Emb:discord.Embed = discord.Embed(
		description = f"{ChangeMember.name} changed a Twitch-Alert.",
		timestamp = datetime.datetime.now(),
		color = EVENT_COLOR_WARNING
	)
	Emb.set_thumbnail(url=ChangeMember.avatar_url or ChangeMember.default_avatar_url)
	Emb.set_author(name=f"Log Event - [{logging_signature}]")
	Emb.add_field(name="Twitch channel:", value=twitch_channel, inline=False)

	try:
		await TargetChannel.send(embed=Emb)
	except Exception as E:
		cls.BASE.Logger.warning(f"Can't log message: {E} {traceback.format_exc()}")

# Twitchalert.delete : 10000000000 : 1024
async def loggingOnTwitchalertDelete(cls:"PhaazebotDiscord", Settings:DiscordServerSettings, **kwargs:dict) -> None:
	"""
	Logs the event when someone deletes a twitch alert (mostly) via web.
	If track option `Twitchalert.delete` is active, it will send a message to discord

	Required keywords:
	------------------
	* Deleter `discord.Member`
	* twitch_channel `str`
	* discord_channel_id `str`
	"""
	logging_signature:str = "Twitchalert.delete"
	Deleter:discord.Member = kwargs["Deleter"]
	twitch_channel:str = kwargs["twitch_channel"]
	discord_channel_id:str = kwargs["discord_channel_id"]

	Chan:discord.TextChannel = getDiscordChannelFromString(cls, Deleter.guild, discord_channel_id, required_type="text")
	discord_channel_name:str = Chan.name if Chan else "(Unknown)"

	cls.BASE.PhaazeDB.insertQuery(
		table="discord_log",
		content={
			"guild_id": Settings.server_id,
			"event_value": TRACK_OPTIONS[logging_signature],
			"initiator_id": str(Deleter.id),
			"content": f"{Deleter.name} deleted the Twitch-Alert for {twitch_channel} in #{discord_channel_name}"
		}
	)

	if not (TRACK_OPTIONS[logging_signature] & Settings.track_value): return # track option not active, skip message to discord server

	TargetChannel:discord.TextChannel = getDiscordChannelFromString(cls, Deleter.guild, Settings.track_channel, required_type="text")
	if not TargetChannel: return # no channel found

	Emb:discord.Embed = discord.Embed(
		description = f"{Deleter.name} deleted a Twitch-Alert.",
		timestamp = datetime.datetime.now(),
		color = EVENT_COLOR_NEGATIVE
	)
	Emb.set_thumbnail(url=Deleter.avatar_url or Deleter.default_avatar_url)
	Emb.set_author(name=f"Log Event - [{logging_signature}]")
	Emb.add_field(name="Twitch channel:", value=twitch_channel, inline=False)

	try:
		await TargetChannel.send(embed=Emb)
	except Exception as E:
		cls.BASE.Logger.warning(f"Can't log message: {E} {traceback.format_exc()}")

# Regular.create : 100000000000 : 2048
async def loggingOnRegularCreate(cls:"PhaazebotDiscord", Settings:DiscordServerSettings, **kwargs:dict) -> None:
	"""
	Logs the event when someone adds a discord regular via web.
	If track option `Regular.create` is active, it will send a message to discord

	Required keywords:
	------------------
	* Creator `discord.Member`
	* NewRegular `discord.Member`
	"""
	logging_signature:str = "Regular.create"
	Creator:discord.Member = kwargs["Creator"]
	NewRegular:discord.Member = kwargs["NewRegular"]

	cls.BASE.PhaazeDB.insertQuery(
		table="discord_log",
		content={
			"guild_id": Settings.server_id,
			"event_value": TRACK_OPTIONS[logging_signature],
			"initiator_id": str(Creator.id),
			"content": f"{Creator.name} added {NewRegular.name} as a regular"
		}
	)

	if not (TRACK_OPTIONS[logging_signature] & Settings.track_value): return # track option not active, skip message to discord server

	TargetChannel:discord.TextChannel = getDiscordChannelFromString(cls, Creator.guild, Settings.track_channel, required_type="text")
	if not TargetChannel: return # no channel found

	Emb:discord.Embed = discord.Embed(
		description = f"{Creator.name} added a new regular.",
		timestamp = datetime.datetime.now(),
		color = EVENT_COLOR_POSITIVE
	)
	Emb.set_thumbnail(url=Creator.avatar_url or Creator.default_avatar_url)
	Emb.set_author(name=f"Log Event - [{logging_signature}]")
	Emb.add_field(name="New Regular:", value=NewRegular.name, inline=False)

	try:
		await TargetChannel.send(embed=Emb)
	except Exception as E:
		cls.BASE.Logger.warning(f"Can't log message: {E} {traceback.format_exc()}")

# Regular.delete : 1000000000000 : 4096
async def loggingOnRegularDelete(cls:"PhaazebotDiscord", Settings:DiscordServerSettings, **kwargs:dict) -> None:
	"""
	Logs the event when someone removes a discord regular via web.
	If track option `Regular.delete` is active, it will send a message to discord

	Required keywords:
	------------------
	* Remover `discord.Member`
	* old_regular_id `str`
	"""
	logging_signature:str = "Regular.delete"
	Remover:discord.Member = kwargs["Remover"]
	old_regular_id:str = kwargs["old_regular_id"]

	OldRegular:discord.Member = getDiscordMemberFromString(cls, Remover.guild, old_regular_id)
	old_regular_name:str = OldRegular.name if OldRegular else "(Unknown)"

	cls.BASE.PhaazeDB.insertQuery(
		table="discord_log",
		content={
			"guild_id": Settings.server_id,
			"event_value": TRACK_OPTIONS[logging_signature],
			"initiator_id": str(Remover.id),
			"content": f"{Remover.name} removed {old_regular_name} as a regular"
		}
	)

	if not (TRACK_OPTIONS[logging_signature] & Settings.track_value): return # track option not active, skip message to discord server

	TargetChannel:discord.TextChannel = getDiscordChannelFromString(cls, Remover.guild, Settings.track_channel, required_type="text")
	if not TargetChannel: return # no channel found

	Emb:discord.Embed = discord.Embed(
		description = f"{Remover.name} removed a regular.",
		timestamp = datetime.datetime.now(),
		color = EVENT_COLOR_NEGATIVE
	)
	Emb.set_thumbnail(url=Remover.avatar_url or Remover.default_avatar_url)
	Emb.set_author(name=f"Log Event - [{logging_signature}]")
	Emb.add_field(name="Old Regular:", value=old_regular_name, inline=False)

	try:
		await TargetChannel.send(embed=Emb)
	except Exception as E:
		cls.BASE.Logger.warning(f"Can't log message: {E} {traceback.format_exc()}")

# Level.edit : 10000000000000 : 8192
async def loggingOnLevelEdit(cls:"PhaazebotDiscord", Settings:DiscordServerSettings, **kwargs:dict) -> None:
	"""
	Logs the event when someone edits a discordmember-level via web.
	If track option `Level.edit` is active, it will send a message to discord

	Required keywords:
	------------------
	* Remover `discord.Member`
	* changed_member_id `str`
	* changes `dict`
	"""
	logging_signature:str = "Level.edit"
	Editor:discord.Member = kwargs["Editor"]
	changed_member_id:str = kwargs["changed_member_id"]
	changes:dict = kwargs["changes"]

	LevelMember:discord.Member = getDiscordMemberFromString(cls, Editor.guild, changed_member_id)
	level_member_name:str = LevelMember.name if LevelMember else "(Unknown)"

	cls.BASE.PhaazeDB.insertQuery(
		table="discord_log",
		content={
			"guild_id": Settings.server_id,
			"event_value": TRACK_OPTIONS[logging_signature],
			"initiator_id": str(Editor.id),
			"content": f"{Editor.name} edited the level stats of: {level_member_name} changes: {str(changes)}"
		}
	)

	if not (TRACK_OPTIONS[logging_signature] & Settings.track_value): return # track option not active, skip message to discord server

	TargetChannel:discord.TextChannel = getDiscordChannelFromString(cls, Editor.guild, Settings.track_channel, required_type="text")
	if not TargetChannel: return # no channel found

	Emb:discord.Embed = discord.Embed(
		description = f"{Editor.name} edited level stats",
		timestamp = datetime.datetime.now(),
		color = EVENT_COLOR_WARNING
	)
	Emb.set_thumbnail(url=Editor.avatar_url or Editor.default_avatar_url)
	Emb.set_author(name=f"Log Event - [{logging_signature}]")
	Emb.add_field(name="Edited member:", value=level_member_name, inline=False)
	if changes.get("edited", False):
		Emb.add_field(name="Warning:", value="EXP got changed, this member now has a [EDITED] mark", inline=False)

	try:
		await TargetChannel.send(embed=Emb)
	except Exception as E:
		cls.BASE.Logger.warning(f"Can't log message: {E} {traceback.format_exc()}")

# Levelmedal.create : 100000000000000 : 16384
async def loggingOnLevelmedalCreate(cls:"PhaazebotDiscord", Settings:DiscordServerSettings, **kwargs:dict) -> None:
	"""
	Logs the event when someone creates a discordmember medal via web.
	If track option `Levelmedal.create` is active, it will send a message to discord

	Required keywords:
	------------------
	* Creator `discord.Member`
	* medal_member_id `str`
	* medal_name `str`
	"""
	logging_signature:str = "Levelmedal.create"
	Creator:discord.Member = kwargs["Creator"]
	medal_member_id:str = kwargs["medal_member_id"]
	medal_name:dict = kwargs["medal_name"]

	MedalMember:discord.Member = getDiscordMemberFromString(cls, Creator.guild, medal_member_id)
	medal_member_name:str = MedalMember.name if MedalMember else "(Unknown)"

	cls.BASE.PhaazeDB.insertQuery(
		table="discord_log",
		content={
			"guild_id": Settings.server_id,
			"event_value": TRACK_OPTIONS[logging_signature],
			"initiator_id": str(Creator.id),
			"content": f"{Creator.name} gave a new medal to: {medal_member_name}, new medal: {medal_name}"
		}
	)

	if not (TRACK_OPTIONS[logging_signature] & Settings.track_value): return # track option not active, skip message to discord server

	TargetChannel:discord.TextChannel = getDiscordChannelFromString(cls, Creator.guild, Settings.track_channel, required_type="text")
	if not TargetChannel: return # no channel found

	Emb:discord.Embed = discord.Embed(
		description = f"{Creator.name} created a new medal",
		timestamp = datetime.datetime.now(),
		color = EVENT_COLOR_POSITIVE
	)
	Emb.set_thumbnail(url=Creator.avatar_url or Creator.default_avatar_url)
	Emb.set_author(name=f"Log Event - [{logging_signature}]")
	Emb.add_field(name="Target member:", value=medal_member_name, inline=False)
	Emb.add_field(name="New Medal:", value=medal_name, inline=False)

	try:
		await TargetChannel.send(embed=Emb)
	except Exception as E:
		cls.BASE.Logger.warning(f"Can't log message: {E} {traceback.format_exc()}")

# Levelmedal.delete : 1000000000000000 : 32768
async def loggingOnLevelmedalDelete(cls:"PhaazebotDiscord", Settings:DiscordServerSettings, **kwargs:dict) -> None:
	"""
	Logs the event when someone deletes a discordmember medal via web.
	If track option `Levelmedal.delete` is active, it will send a message to discord

	Required keywords:
	------------------
	* Deleter `discord.Member`
	* medal_member_id `str`
	* medal_name `str`
	"""
	logging_signature:str = "Levelmedal.delete"
	Deleter:discord.Member = kwargs["Deleter"]
	medal_member_id:str = kwargs["medal_member_id"]
	medal_name:dict = kwargs["medal_name"]

	MedalMember:discord.Member = getDiscordMemberFromString(cls, Deleter.guild, medal_member_id)
	medal_member_name:str = MedalMember.name if MedalMember else "(Unknown)"

	cls.BASE.PhaazeDB.insertQuery(
		table="discord_log",
		content={
			"guild_id": Settings.server_id,
			"event_value": TRACK_OPTIONS[logging_signature],
			"initiator_id": str(Deleter.id),
			"content": f"{Deleter.name} removed a medal from: {medal_member_name}, old medal: {medal_name}"
		}
	)

	if not (TRACK_OPTIONS[logging_signature] & Settings.track_value): return # track option not active, skip message to discord server

	TargetChannel:discord.TextChannel = getDiscordChannelFromString(cls, Deleter.guild, Settings.track_channel, required_type="text")
	if not TargetChannel: return # no channel found

	Emb:discord.Embed = discord.Embed(
		description = f"{Deleter.name} removed a medal",
		timestamp = datetime.datetime.now(),
		color = EVENT_COLOR_NEGATIVE
	)
	Emb.set_thumbnail(url=Deleter.avatar_url or Deleter.default_avatar_url)
	Emb.set_author(name=f"Log Event - [{logging_signature}]")
	Emb.add_field(name="Target member:", value=medal_member_name, inline=False)
	Emb.add_field(name="Medal:", value=medal_name, inline=False)

	try:
		await TargetChannel.send(embed=Emb)
	except Exception as E:
		cls.BASE.Logger.warning(f"Can't log message: {E} {traceback.format_exc()}")

# Assignrole.create : 10000000000000000 : 65536
async def loggingOnAssignroleCreate(cls:"PhaazebotDiscord", Settings:DiscordServerSettings, **kwargs:dict) -> None:
	"""
	Logs the event when someone creates a new assignrole via web.
	If track option `Assignrole.create` is active, it will send a message to discord

	Required keywords:
	------------------
	* Creator `discord.Member`
	* assign_role_id `str`
	* trigger `str`
	"""
	logging_signature:str = "Assignrole.create"
	Creator:discord.Member = kwargs["Creator"]
	assign_role_id:str = kwargs["assign_role_id"]
	trigger:str = kwargs["trigger"]

	AssignRole:discord.Role = getDiscordRoleFromString(cls, Creator.guild, assign_role_id)
	assign_role_name:str = AssignRole.name if AssignRole else "(Unknown)"

	cls.BASE.PhaazeDB.insertQuery(
		table="discord_log",
		content={
			"guild_id": Settings.server_id,
			"event_value": TRACK_OPTIONS[logging_signature],
			"initiator_id": str(Creator.id),
			"content": f"{Creator.name} created a new assign role {assign_role_name} with {trigger=}"
		}
	)

	if not (TRACK_OPTIONS[logging_signature] & Settings.track_value): return # track option not active, skip message to discord server

	TargetChannel:discord.TextChannel = getDiscordChannelFromString(cls, Creator.guild, Settings.track_channel, required_type="text")
	if not TargetChannel: return # no channel found

	Emb:discord.Embed = discord.Embed(
		description = f"{Creator.name} created a assignrole",
		timestamp = datetime.datetime.now(),
		color = EVENT_COLOR_POSITIVE
	)
	Emb.set_thumbnail(url=Creator.avatar_url or Creator.default_avatar_url)
	Emb.set_author(name=f"Log Event - [{logging_signature}]")
	Emb.add_field(name="Trigger:", value=trigger, inline=False)
	Emb.add_field(name="Linked with role:", value=assign_role_name, inline=False)

	try:
		await TargetChannel.send(embed=Emb)
	except Exception as E:
		cls.BASE.Logger.warning(f"Can't log message: {E} {traceback.format_exc()}")

# Assignrole.edit : 100000000000000000 : 131072
async def loggingOnAssignroleEdit(cls:"PhaazebotDiscord", Settings:DiscordServerSettings, **kwargs:dict) -> None:
	"""
	Logs the event when someone edits assignrole via web.
	If track option `Assignrole.edit` is active, it will send a message to discord

	Required keywords:
	------------------
	* Editor `discord.Member`
	* assign_role_trigger `str`
	* changes `dict`
	"""
	logging_signature:str = "Assignrole.edit"
	Editor:discord.Member = kwargs["Editor"]
	assign_role_trigger:str = kwargs["assign_role_trigger"]
	changes:dict = kwargs["changes"]

	cls.BASE.PhaazeDB.insertQuery(
		table="discord_log",
		content={
			"guild_id": Settings.server_id,
			"event_value": TRACK_OPTIONS[logging_signature],
			"initiator_id": str(Editor.id),
			"content": f"{Editor.name} edited the assign role with trigger='{assign_role_trigger}' changes: {str(changes)}"
		}
	)

	if not (TRACK_OPTIONS[logging_signature] & Settings.track_value): return # track option not active, skip message to discord server

	TargetChannel:discord.TextChannel = getDiscordChannelFromString(cls, Editor.guild, Settings.track_channel, required_type="text")
	if not TargetChannel: return # no channel found

	Emb:discord.Embed = discord.Embed(
		description = f"{Editor.name} edited a assignrole",
		timestamp = datetime.datetime.now(),
		color = EVENT_COLOR_WARNING
	)
	Emb.set_thumbnail(url=Editor.avatar_url or Editor.default_avatar_url)
	Emb.set_author(name=f"Log Event - [{logging_signature}]")
	Emb.add_field(name="Role trigger:", value=assign_role_trigger, inline=False)

	try:
		await TargetChannel.send(embed=Emb)
	except Exception as E:
		cls.BASE.Logger.warning(f"Can't log message: {E} {traceback.format_exc()}")

# Assignrole.delete : 1000000000000000000 : 262144
async def loggingOnAssignroleDelete(cls:"PhaazebotDiscord", Settings:DiscordServerSettings, **kwargs:dict) -> None:
	"""
	Logs the event when someone deletes a assignrole via web.
	If track option `Assignrole.delete` is active, it will send a message to discord

	Required keywords:
	------------------
	* Deleter `discord.Member`
	* assign_role_trigger `str`
	"""
	logging_signature:str = "Assignrole.delete"
	Deleter:discord.Member = kwargs["Deleter"]
	assign_role_trigger:str = kwargs["assign_role_trigger"]

	cls.BASE.PhaazeDB.insertQuery(
		table="discord_log",
		content={
			"guild_id": Settings.server_id,
			"event_value": TRACK_OPTIONS[logging_signature],
			"initiator_id": str(Deleter.id),
			"content": f"{Deleter.name} deleted a assign role with trigger='{assign_role_trigger}'"
		}
	)

	if not (TRACK_OPTIONS[logging_signature] & Settings.track_value): return # track option not active, skip message to discord server

	TargetChannel:discord.TextChannel = getDiscordChannelFromString(cls, Deleter.guild, Settings.track_channel, required_type="text")
	if not TargetChannel: return # no channel found

	Emb:discord.Embed = discord.Embed(
		description = f"{Deleter.name} deleted a assignrole",
		timestamp = datetime.datetime.now(),
		color = EVENT_COLOR_NEGATIVE
	)
	Emb.set_thumbnail(url=Deleter.avatar_url or Deleter.default_avatar_url)
	Emb.set_author(name=f"Log Event - [{logging_signature}]")
	Emb.add_field(name="Role trigger:", value=assign_role_trigger, inline=False)

	try:
		await TargetChannel.send(embed=Emb)
	except Exception as E:
		cls.BASE.Logger.warning(f"Can't log message: {E} {traceback.format_exc()}")

# Config.edit : 10000000000000000000 : 524288
async def loggingOnConfigEdit(cls:"PhaazebotDiscord", Settings:DiscordServerSettings, **kwargs:dict) -> None:
	"""
	Logs the event when someone makes any changes to configs via web.
	If track option `Config.edit` is active, it will send a message to discord

	Required keywords:
	------------------
	* Editor `discord.Member`
	* changes `dict`
	"""
	logging_signature:str = "Config.edit"
	Editor:discord.Member = kwargs["Editor"]
	changes:dict = kwargs["changes"]

	cls.BASE.PhaazeDB.insertQuery(
		table="discord_log",
		content={
			"guild_id": Settings.server_id,
			"event_value": TRACK_OPTIONS[logging_signature],
			"initiator_id": str(Editor.id),
			"content": f"{Editor.name} made changes to the server settings: {str(changes)}"
		}
	)

	if not (TRACK_OPTIONS[logging_signature] & Settings.track_value): return # track option not active, skip message to discord server

	TargetChannel:discord.TextChannel = getDiscordChannelFromString(cls, Editor.guild, Settings.track_channel, required_type="text")
	if not TargetChannel: return # no channel found

	Emb:discord.Embed = discord.Embed(
		description = f"{Editor.name} made changes to the server settings",
		timestamp = datetime.datetime.now(),
		color = EVENT_COLOR_WARNING
	)
	Emb.set_thumbnail(url=Editor.avatar_url or Editor.default_avatar_url)
	Emb.set_author(name=f"Log Event - [{logging_signature}]")

	try:
		await TargetChannel.send(embed=Emb)
	except Exception as E:
		cls.BASE.Logger.warning(f"Can't log message: {E} {traceback.format_exc()}")
