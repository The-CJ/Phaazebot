from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from .main_discord import PhaazebotDiscord

import discord
import traceback
import datetime
from Utils.Classes.discordserversettings import DiscordServerSettings
from Platforms.Discord.utils import getDiscordChannelFromString

# there is only a small amount, because most things are handled by discord audit logs
TRACK_OPTIONS:list = [ "Member.join", "Member.remove" ]
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
