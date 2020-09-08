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
	"""
	Creator:discord.Member = kwargs.get("Creator", None)
	quote_content:str = kwargs.get("quote_content", False)

	if not Creator: raise AttributeError("missing `Creator`")
	if not quote_content: raise AttributeError("missing `quote_content`")

	cls.BASE.PhaazeDB.insertQuery(
		table="discord_log",
		content={
			"guild_id": Settings.server_id,
			"event_value": TRACK_OPTIONS["Quote.create"],
			"initiator_id": str(Creator.id),
			"content": f"New Quote Created: {quote_content}"
		}
	)

	if not (TRACK_OPTIONS["Quote.create"] & Settings.track_value): return # track option not active, skip message to discord server

	TargetChannel:discord.TextChannel = getDiscordChannelFromString(cls, Creator.guild, Settings.track_channel, required_type="text")
	if not TargetChannel: return # no channel found

	Emb:discord.Embed = discord.Embed(
		description = f"{Creator.name} created a new quote.",
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
