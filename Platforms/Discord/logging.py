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

async def loggingOnMemberJoin(cls:"PhaazebotDiscord", Settings:DiscordServerSettings, NewMember:discord.Member, **kwargs:dict) -> None:
	"""
	Sends logging message on member join event to Settings.track_channel.
	Requires track option `Member.join` active

	Optional keywords:
	------------------
	* link_in_name `bool` : (Default: False)
	"""
	link_in_name:bool = kwargs.get("link_in_name", False)

	if not ("Member.join" in Settings.track_options): return # track option not active

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

async def loggingOnMemberRemove(cls:"PhaazebotDiscord", Settings:DiscordServerSettings, OldMember:discord.Member, **kwargs:dict) -> None:
	"""
	Sends logging message on member remove event to Settings.track_channel.
	Requires track option `Member.remove` active

	Optional keywords:
	------------------
	* link_in_name `bool` : (Default: False)
	"""
	link_in_name:bool = kwargs.get("link_in_name", False)

	if not ("Member.remove" in Settings.track_options): return # track option not active

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
