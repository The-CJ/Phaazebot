from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from .main_discord import PhaazebotDiscord

import discord
from Utils.Classes.discordserversettings import DiscordServerSettings
from .utils import getDiscordSeverSettings
from .blacklist import checkBlacklist
from .commands import checkCommands
from .levels import checkLevel

async def openChannel(cls:"PhaazebotDiscord", Message:discord.Message) -> None:

	# get server settings
	ServerSettings:DiscordServerSettings = await getDiscordSeverSettings(cls, Message)

	# only run blacklist module if links are banned or at least on entry on the blacklist
	if ServerSettings.blacklist_ban_links or ServerSettings.blacklist_blacklistwords:
		executed_punishment = await checkBlacklist(cls, Message, ServerSettings)
		if executed_punishment:
			cls.BASE.Logger.debug(f"(Discord) executed blacklist punishment guild_id={Message.guild.id} punish={ServerSettings.blacklist_punishment}", require="discord:blacklist")
			return

	executed_command:bool = await checkCommands(cls, Message, ServerSettings)

	# only execute if its a new message and its not a command
	#   we need to check this, since on_message_edit calls on_message
	#   so edited messages trigger commands, but not level additions
	if not Message.edited_at and not executed_command:
		await checkLevel(cls, Message, ServerSettings)
