from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from .main_discord import PhaazebotDiscord

import discord
from Utils.Classes.discordserversettings import DiscordServerSettings
from Utils.Classes.discordpermission import DiscordPermission

async def checkBlacklist(cls:"PhaazebotDiscord", Message:discord.Message, ServerSettings:DiscordServerSettings) -> None:

	PhaazePermissions:discord.Permissions = Message.channel.permissions_for(Message.guild.me)

	if not PhaazePermissions.manage_messages: return
	if DiscordPermission(Message).rank >= 2: return

	# links are not allowed
	if ServerSettings.ban_links or True: # NOTE: testing
		await checkBanLinks(cls, Message, ServerSettings)


async def checkBanLinks(cls:"PhaazebotDiscord", Message:discord.Message, ServerSettings:DiscordServerSettings) -> None:

	# check if user has a role that is allowed to post links
	if any( [True if role.id in ServerSettings.ban_links_role else False for role in Message.author.roles] ): return
