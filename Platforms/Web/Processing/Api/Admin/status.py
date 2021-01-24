from typing import TYPE_CHECKING, Dict, Any, List
if TYPE_CHECKING:
	from phaazebot import Phaazebot
	from Platforms.Web.main_web import PhaazebotWeb

import json
import time
import discord
from aiohttp.web import Response
from Utils.Classes.authwebuser import AuthWebUser
from Utils.Classes.extendedrequest import ExtendedRequest
from Platforms.Web.index import PhaazeWebIndex
from Platforms.Web.utils import authWebUser

@PhaazeWebIndex.view("/api/admin/status")
async def apiAdminStatus(cls:"PhaazebotWeb", WebRequest:ExtendedRequest) -> Response:
	"""
	Default url: /api/admin/status
	"""
	WebAuth:AuthWebUser = await authWebUser(cls, WebRequest)
	if not WebAuth.found:
		return await cls.Tree.Account.accountlogin.accountLogin(WebRequest)
	if not WebAuth.User.checkRoles(["admin", "superadmin"]):
		return await cls.Tree.errors.notAllowed(WebRequest, msg="Admin rights required")

	BASE:"Phaazebot" = cls.BASE
	status:Dict[str, Any] = dict()

	status["version"] = BASE.version
	status["uptime"] = time.time() - BASE.start_time

	status["modules"] = dict()
	for module in vars(BASE.Active):
		status["modules"][module] = bool(getattr(BASE.Active, module, False))

	# if discord is active, add discord to status
	if BASE.Active.discord and BASE.IsReady.discord:
		status["discord"] = getDiscordStatus(BASE)
	else:
		status["discord"] = None

	return cls.response(
		body=json.dumps(dict(result=status, status=200)),
		status=200,
		content_type='application/json'
	)

def getDiscordStatus(BASE:"Phaazebot") -> Dict[str, Any]:
	discord_data:Dict[str, Any] = dict(
		unique_guilds=len(BASE.Discord.guilds),
		unique_users=getUniqueDiscordMember(BASE.Discord.guilds),
		bot_id=str(BASE.Discord.user.id),
		bot_name=str(BASE.Discord.user.name),
		bot_discriminator=str(BASE.Discord.user.discriminator),
		bot_avatar_url=str(BASE.Discord.user.avatar_url)
	)
	return discord_data

def getUniqueDiscordMember(guilds:List[discord.Guild]) -> int:
	unique_member:List[int] = []

	for guild in guilds:
		for member in guild.members:
			if member.id not in unique_member: unique_member.append(member.id)

	return len(unique_member)
