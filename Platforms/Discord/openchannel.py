from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from .main_discord import PhaazebotDiscord

import discord
from Utils.Classes.discordserversettings import DiscordServerSettings
from .utils import getDiscordSeverSettings
from .blacklist import checkBlacklist
from .commands import checkCommands

async def openChannel(cls:"PhaazebotDiscord", Message:discord.Message) -> None:

	# get server settings
	ServerSettings:DiscordServerSettings = await getDiscordSeverSettings(cls, Message)

	# only run blacklist module if links are banned or at least on entry on the blacklist
	if ServerSettings.ban_links or ServerSettings.blacklist or True: # NOTE: testing
		await checkBlacklist(cls, Message, ServerSettings)

	# only execute if its a new message
	# we need to check this, since on_message_edit calls on_message
	# so edited messages trigger commands, but not level additions
	if not Message.edited_at:
		cls.BASE.Logger.info(f"TODO: Check level stuff")

	await checkCommands(cls, Message, ServerSettings)
