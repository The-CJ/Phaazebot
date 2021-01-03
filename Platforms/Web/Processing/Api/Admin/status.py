from typing import TYPE_CHECKING, Dict, Any, List
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex
	from main import Phaazebot

import json
import time
import discord
from aiohttp.web import Response, Request
from Utils.Classes.authwebuser import AuthWebUser
from Platforms.Web.Processing.Api.errors import apiNotAllowed

async def apiAdminStatus(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
	Default url: /api/admin/status
	"""
	WebUser:AuthWebUser = await cls.getWebUserInfo(WebRequest)
	if not WebUser.checkRoles(["admin", "superadmin"]):
		return await apiNotAllowed(cls, WebRequest, msg="Admin rights required")

	BASE:"Phaazebot" = cls.Web.BASE
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
	discord:Dict[str, Any] = dict(
		unique_guilds = len(BASE.Discord.guilds),
		unique_users = getUniqueDiscordMember(BASE.Discord.guilds),
		bot_id = str( BASE.Discord.user.id ),
		bot_name = str( BASE.Discord.user.name ),
		bot_discriminator = str( BASE.Discord.user.discriminator ),
		bot_avatar_url = str( BASE.Discord.user.avatar_url )
	)
	return discord

def getUniqueDiscordMember(guilds:List[discord.Guild]) -> int:
	unique_member:List[int] = []

	for guild in guilds:
		for member in guild.members:
			if member.id not in unique_member: unique_member.append(member.id)

	return len(unique_member)
