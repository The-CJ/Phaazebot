from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from .main_discord import PhaazebotDiscord

import discord
from Utils.Classes.discordserversettings import DiscordServerSettings
from Platforms.Discord.utils import getDiscordSeverSettings, getDiscordChannelFromString
from Platforms.Discord.formater import formater
from Utils.regex import ContainsLink

async def eventOnMemberJoin(cls:"PhaazebotDiscord", Member:discord.Member) -> None:

	Settings:DiscordServerSettings = await getDiscordSeverSettings(cls, Member.guild.id)
	link_in_name:bool = bool( ContainsLink.match(Member.name) )

	# TODO: Logging for new member

	# send welcome message
	if Settings.welcome_chan and Settings.welcome_msg and (not link_in_name):

		WelcomeChan:discord.TextChannel = getDiscordChannelFromString(cls, Member.guild, Settings.welcome_chan, required_type="text")
		if WelcomeChan:
			pass

	# set member active, if there was a known entry
	cls.BASE.PhaazeDB.updateQuery(
		table = "discord_user",
		content = {"on_server":1},
		where = "guild_id = %s AND member_id = %s",
		where_values = ( str(Member.guild.id), str(Member.id) )
	)

async def eventOnMemberRemove(cls:"PhaazebotDiscord", Member:discord.Member) -> None:

	# TODO: logging for member leave

	# set member active, if there was a known entry
	cls.BASE.PhaazeDB.updateQuery(
		table = "discord_user",
		content = {"on_server":0},
		where = "guild_id = %s AND member_id = %s",
		where_values = ( str(Member.guild.id), str(Member.id) )
	)
