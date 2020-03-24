from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from .main_discord import PhaazebotDiscord

import sys
import discord
from Utils.Classes.discordserversettings import DiscordServerSettings
from Platforms.Discord.utils import getDiscordSeverSettings, getDiscordChannelFromString
from Platforms.Discord.formater import responseFormater
from Utils.regex import ContainsLink

async def eventOnMemberJoin(cls:"PhaazebotDiscord", Member:discord.Member) -> None:

	Settings:DiscordServerSettings = await getDiscordSeverSettings(cls, Member.guild.id)
	link_in_name:bool = bool( ContainsLink.match(Member.name) )

	# TODO: Logging for new member

	# send welcome message
	if Settings.welcome_chan and Settings.welcome_msg and (not link_in_name):

		WelcomeChan:discord.TextChannel = getDiscordChannelFromString(cls, Member.guild, Settings.welcome_chan, required_type="text")
		if WelcomeChan:
			welcome_msg_vars:dict = {
				"user-name": Member.name,
				"user-mention": Member.mention,
				"server-name": Member.guild.name,
				"member-count": str(Member.guild.member_count)
			}
			finished_message:str = await responseFormater(cls, Settings.welcome_msg, var_dict=welcome_msg_vars, enable_special=True, DiscordGuild=Member.guild)
			try:
				await WelcomeChan.send(finished_message)
			except Exception as E:
				cls.BASE.Logger.warning(f"Can't send welcome message: {E} {sys.exc_info()[0]}")

	# set member active, if there was a known entry
	cls.BASE.PhaazeDB.updateQuery(
		table = "discord_user",
		content = {"on_server":1},
		where = "guild_id = %s AND member_id = %s",
		where_values = ( str(Member.guild.id), str(Member.id) )
	)

async def eventOnMemberRemove(cls:"PhaazebotDiscord", Member:discord.Member) -> None:

	Settings:DiscordServerSettings = await getDiscordSeverSettings(cls, Member.guild.id)
	link_in_name:bool = bool( ContainsLink.match(Member.name) )

	# TODO: logging for member leave

	# send welcome message
	if Settings.leave_chan and Settings.leave_msg and (not link_in_name):

		LeaveChan:discord.TextChannel = getDiscordChannelFromString(cls, Member.guild, Settings.leave_chan, required_type="text")
		if LeaveChan:
			welcome_msg_vars:dict = {
				"user-name": Member.name,
				"user-mention": Member.mention,
				"server-name": Member.guild.name,
				"member-count": str(Member.guild.member_count)
			}
			finished_message:str = await responseFormater(cls, Settings.leave_msg, var_dict=welcome_msg_vars, enable_special=True, DiscordGuild=Member.guild)
			try:
				await LeaveChan.send(finished_message)
			except Exception as E:
				cls.BASE.Logger.warning(f"Can't send leave message: {E} {sys.exc_info()[0]}")

	# set member inactive
	cls.BASE.PhaazeDB.updateQuery(
		table = "discord_user",
		content = {"on_server":0},
		where = "guild_id = %s AND member_id = %s",
		where_values = ( str(Member.guild.id), str(Member.id) )
	)
