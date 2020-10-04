from typing import TYPE_CHECKING, List
if TYPE_CHECKING:
	from .main_discord import PhaazebotDiscord

import discord
from Utils.Classes.discordserversettings import DiscordServerSettings
from Utils.Classes.discorduserstats import DiscordUserStats
from Platforms.Discord.db import getDiscordSeverSettings, getDiscordServerUsers
from Platforms.Discord.blacklist import checkBlacklist
from Platforms.Discord.commands import checkCommands
from Platforms.Discord.levels import checkLevel

async def openChannel(cls:"PhaazebotDiscord", Message:discord.Message) -> None:

	# Base: get server settings
	ServerSettings:DiscordServerSettings = await getDiscordSeverSettings(cls, Message)

	# Base: get user entry
	DiscordUser:DiscordUserStats = None
	user_res:List[DiscordUserStats] = await getDiscordServerUsers(cls, Message.guild.id, member_id=Message.author.id)
	if user_res: DiscordUser = user_res.pop(0)

	# Blacklist: only run blacklist module if links are banned or at least on entry on the blacklist
	if ServerSettings.blacklist_ban_links or ServerSettings.blacklist_blacklistwords:
		executed_punishment:bool = await checkBlacklist(cls, Message, ServerSettings, DiscordUser)
		if executed_punishment:
			cls.BASE.Logger.debug(f"(Discord) executed blacklist punishment guild_id={Message.guild.id} punish={ServerSettings.blacklist_punishment}", require="discord:blacklist")
			return

	# Commands: check if message triggered a command
	executed_command:bool = await checkCommands(cls, Message, ServerSettings, DiscordUser)

	# Level: only execute if its a new message and its not a command
	#   we need to check this, since on_message_edit calls on_message
	#   so edited messages trigger commands, but not level additions
	if not Message.edited_at and not executed_command:
		await checkLevel(cls, Message, ServerSettings, DiscordUser)
