from typing import TYPE_CHECKING, Iterator, Optional
if TYPE_CHECKING:
	from Platforms.Discord.main_discord import PhaazebotDiscord

import discord
import re
# noinspection PyPep8Naming
import Platforms.Discord.const as DiscordConst
from Utils.regex import ContainsLink
from Utils.Classes.discordserversettings import DiscordServerSettings
from Utils.Classes.discorduserstats import DiscordUserStats
from Utils.Classes.discordpermission import DiscordPermission

async def checkPunish(cls:"PhaazebotDiscord", Message:discord.Message, ServerSettings:DiscordServerSettings, DiscordUser:DiscordUserStats) -> bool:

	PhaazePermissions:discord.Permissions = Message.channel.permissions_for(Message.guild.me)

	# if the user has manage_messages or is a regular or higher, skip checks
	if not PhaazePermissions.manage_messages: return False
	if DiscordPermission(Message, DiscordUser).rank >= DiscordConst.REQUIRE_REGULAR: return False

	# if this is True after all checks => punish
	punish:bool = False
	reason:Optional[str] = None

	# links
	if ServerSettings.blacklist_ban_links:
		punish = await checkLinks(cls, Message, ServerSettings)
		reason = "links"

	if ServerSettings.blacklist_blacklistwords and not punish:
		punish = await checkBlacklist(cls, Message, ServerSettings)
		reason = "blacklist"

	if punish:
		await executePunish(cls, Message, ServerSettings, reason=reason)
		return True

	else:
		return False

# checks
async def checkLinks(_cls:"PhaazebotDiscord", Message:discord.Message, ServerSettings:DiscordServerSettings) -> bool:

	# check if user has a role that is allowed to post links
	if any([True if role.id in ServerSettings.blacklist_whitelistroles else False for role in Message.author.roles]): return False

	found_links:Iterator = re.finditer(ContainsLink, Message.content)

	if not found_links: return False

	# check all found link, by default, every link is punished
	for found_link in found_links:
		allowed = False

		# check all whitelisted link regex
		for allowed_link in ServerSettings.blacklist_whitelistlinks:
			# link is whitelisted, allow it, break allowed_link search
			if re.search(allowed_link, found_link.group(0)):
				allowed = True
				break

		# link is not in whitelist
		if not allowed:
			return True

	# all links could be found in the whitelist
	return False

async def checkBlacklist(_cls:"PhaazebotDiscord", Message:discord.Message, ServerSettings:DiscordServerSettings) -> bool:
	message_text = Message.content.lower()

	for re_pattern in ServerSettings.blacklist_blacklistwords:
		try:
			if re.search(re_pattern, message_text):
				return True
		except:
			pass

	return False

async def checkEmotes(_cls:"PhaazebotDiscord", _Message:discord.Message, _ServerSettings:DiscordServerSettings) -> bool:
	pass

async def checkCaps(_cls:"PhaazebotDiscord", _Message:discord.Message, _ServerSettings:DiscordServerSettings) -> bool:
	pass

async def checkCopyPast(_cls:"PhaazebotDiscord", _Message:discord.Message, _ServerSettings:DiscordServerSettings) -> bool:
	pass

async def checkUnicode(_cls:"PhaazebotDiscord", _Message:discord.Message, _ServerSettings:DiscordServerSettings) -> bool:
	pass

# finals and utils
async def executePunish(_cls:"PhaazebotDiscord", Message:discord.Message, ServerSettings:DiscordServerSettings, reason:str = None) -> None:
	ServerSettings.blacklist_punishment = checkPunishmentString(ServerSettings.blacklist_punishment)
	try:
		reason_str:Optional[str] = None

		if ServerSettings.blacklist_punishment == "delete":
			await Message.delete()

		elif ServerSettings.blacklist_punishment == "kick":
			if reason:
				reason_str = f"Triggered by '{reason}' - Message: {Message.content}"

			await Message.delete()
			await Message.guild.kick(Message.author, reason=reason_str)

		elif ServerSettings.blacklist_punishment == "ban":
			if reason:
				reason_str = f"Triggered by '{reason}' - Message: {Message.content}"

			await Message.guild.ban(Message.author, reason=reason_str, delete_message_days=1)

	except:
		raise

def checkPunishmentString(p:str) -> str:
	p = p.lower()
	if p in ["delete","kick","ban"]:
		return p
	else:
		return "delete"
