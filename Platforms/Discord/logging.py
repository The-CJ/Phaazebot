from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from .main_discord import PhaazebotDiscord

import discord
from Utils.Classes.discordserversettings import DiscordServerSettings

async def loggingOnMemberJoin(cls:"PhaazebotDiscord", Settings:DiscordServerSettings, NewMember:discord.Member) -> None:

	if Settings.track_channel and ("Member.join" in Settings.track_options):
		pass








	pass
