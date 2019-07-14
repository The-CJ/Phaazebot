from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from .main_discord import PhaazebotDiscord

import discord
import re
from Utils.regex import ContainsLink
from Utils.Classes.discordserversettings import DiscordServerSettings
from Utils.Classes.discordpermission import DiscordPermission

async def checkBlacklist(cls:"PhaazebotDiscord", Message:discord.Message, ServerSettings:DiscordServerSettings) -> None:

	PhaazePermissions:discord.Permissions = Message.channel.permissions_for(Message.guild.me)

	# if not PhaazePermissions.manage_messages: return
	# if DiscordPermission(Message).rank >= 2: return

	# if this is True after all checks, punish
	punish:bool = False

	# links are not allowed
	if ServerSettings.ban_links or True: # NOTE: testing
		punish = await checkBanLinks(cls, Message, ServerSettings)

	print(punish)

async def checkBanLinks(cls:"PhaazebotDiscord", Message:discord.Message, ServerSettings:DiscordServerSettings) -> bool:

	# check if user has a role that is allowed to post links
	if any( [True if role.id in ServerSettings.ban_links_role else False for role in Message.author.roles] ): return False

	found_links:iter = re.finditer(ContainsLink, Message.content)

	if not found_links: return False

	# check all found link, by default, every link is punished
	for found_link in found_links:
		allowed = False

		# check all whitelisted link regex
		for allowed_link in ServerSettings.ban_links_whitelist:
			# link is whitelisted, allow it, break allowed_link search
			if re.search(allowed_link, found_link.group(0)):
				allowed = True
				break

		# link is not in whitelist
		if not allowed:
			return True

	# all links could be found in the whitelist
	return False
