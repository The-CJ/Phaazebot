from typing import TYPE_CHECKING, Coroutine
if TYPE_CHECKING:
	from Platforms.Discord.main_discord import PhaazebotDiscord

import asyncio
import discord
import traceback
from Utils.Classes.discordserversettings import DiscordServerSettings
from Platforms.Discord.db import getDiscordSeverSettings
from Platforms.Discord.utils import getDiscordChannelFromString, getDiscordRoleFromString
from Platforms.Discord.formatter import responseFormatter
from Platforms.Discord.logging import loggingOnMemberJoin, loggingOnMemberRemove
from Utils.regex import ContainsLink

async def eventOnMemberJoin(cls:"PhaazebotDiscord", Member:discord.Member) -> None:
	"""
	Get's triggered everytime a new member joins a guild,
	the following action may be taken (in this order):

	* Send logging message
	* Send a welcome message to guild channel
	* Send a private welcome message to the new member
	* Give the new member a predefined role
	* (if the member was on this guild before) set member active in levels table
	"""

	Settings:DiscordServerSettings = await getDiscordSeverSettings(cls, Member.guild.id)
	link_in_name:bool = bool(ContainsLink.match(Member.name))

	# logging message
	log_coro:Coroutine = loggingOnMemberJoin(cls, Settings, NewMember=Member, link_in_name=link_in_name)
	asyncio.ensure_future(log_coro, loop=cls.BASE.DiscordLoop)

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
			finished_message:str = await responseFormatter(cls, Settings.welcome_msg, var_dict=welcome_msg_vars, enable_special=True, DiscordGuild=Member.guild)
			try:
				finished_message = finished_message[:1997]
				await WelcomeChan.send(finished_message)
			except Exception as E:
				cls.BASE.Logger.warning(f"Can't send welcome message: {E} {traceback.format_exc()}")

	# send private welcome message
	if Settings.welcome_msg_priv:

		welcome_msg_priv_vars:dict = {
			"user-name": Member.name,
			"server-name": Member.guild.name,
			"member-count": str(Member.guild.member_count)
		}
		finished_message:str = await responseFormatter(cls, Settings.welcome_msg_priv, var_dict=welcome_msg_priv_vars, enable_special=True, DiscordGuild=Member.guild)
		try:
			finished_message = finished_message[:1997]
			await Member.send(finished_message)
		except Exception as E:
			cls.BASE.Logger.warning(f"Can't send private welcome message: {E} {traceback.format_exc()}")

	# give member autorole
	if Settings.autorole_id:
		RoleToGive:discord.Role = getDiscordRoleFromString(cls, Member.guild, Settings.autorole_id)
		if RoleToGive and RoleToGive < Member.guild.me.top_role: # there is a role found and phaaze can give this role
			try:
				await Member.add_roles(RoleToGive)
			except Exception as E:
				cls.BASE.Logger.warning(f"Can't add role to member: {E} {traceback.format_exc()}")

	# set member active, if there was a known entry
	cls.BASE.PhaazeDB.updateQuery(
		table="discord_user",
		content={"on_server":1},
		where="guild_id = %s AND member_id = %s",
		where_values=(str(Member.guild.id), str(Member.id))
	)

async def eventOnMemberRemove(cls:"PhaazebotDiscord", Member:discord.Member) -> None:
	"""
	Get's triggered everytime a member leaves a guild
	the following action may be taken (in this order):
	* Send logging message
	* Send a leave message to guild channel
	* set member inactive in levels table
	"""

	Settings:DiscordServerSettings = await getDiscordSeverSettings(cls, Member.guild.id)
	link_in_name:bool = bool(ContainsLink.match(Member.name))

	# logging message
	log_coro:Coroutine = loggingOnMemberRemove(cls, Settings, OldMember=Member, link_in_name=link_in_name)
	asyncio.ensure_future(log_coro, loop=cls.BASE.DiscordLoop)

	# send leave message
	if Settings.leave_chan and Settings.leave_msg and (not link_in_name):

		LeaveChan:discord.TextChannel = getDiscordChannelFromString(cls, Member.guild, Settings.leave_chan, required_type="text")
		if LeaveChan:
			welcome_msg_vars:dict = {
				"user-name": Member.name,
				"user-mention": Member.mention,
				"server-name": Member.guild.name,
				"member-count": str(Member.guild.member_count)
			}
			finished_message:str = await responseFormatter(cls, Settings.leave_msg, var_dict=welcome_msg_vars, enable_special=True, DiscordGuild=Member.guild)
			try:
				finished_message = finished_message[:1997]
				await LeaveChan.send(finished_message)
			except Exception as E:
				cls.BASE.Logger.warning(f"Can't send leave message: {E} {traceback.format_exc()}")

	# set member inactive
	cls.BASE.PhaazeDB.updateQuery(
		table="discord_user",
		content={"on_server":0},
		where="guild_id = %s AND member_id = %s",
		where_values=(str(Member.guild.id), str(Member.id))
	)
