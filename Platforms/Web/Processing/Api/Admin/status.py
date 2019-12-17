from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex
	from main import Phaazebot

import json
import time
from aiohttp.web import Response, Request
from Utils.Classes.webuserinfo import WebUserInfo
from Platforms.Web.Processing.Api.errors import apiNotAllowed

async def apiAdminStatus(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
		Default url: /api/admin/status
	"""
	WebUser:WebUserInfo = await cls.getWebUserInfo(WebRequest)
	if not WebUser.checkRoles(["admin", "superadmin"]): return await apiNotAllowed(cls, WebRequest, msg="Admin rights required")

	BASE:"Phaazebot" = cls.Web.BASE

	status:dict = dict()

	status["version"] = BASE.version
	status["uptime"] = time.time() - BASE.start_time

	status["modules"] = dict()
	for module in vars(BASE.Active):
		status["modules"][module] = bool(getattr(BASE.Active, module, False))

	if BASE.Active.discord and BASE.IsReady.discord:
		status["discord"] = getDiscordStatus(BASE)
	else:
		status["discord"] = None

	return cls.response(
		body=json.dumps(dict(result=status, status=200)),
		status=200,
		content_type='application/json'
	)

def getDiscordStatus(BASE:"Phaazebot") -> dict:
	discord:dict = dict(
		unique_guilds = len(BASE.Discord.guilds),
		unique_users = getUniqueDiscordMember(BASE.Discord.guilds),
		bot_id = BASE.Discord.user.id,
		bot_name = BASE.Discord.user.name,
		bot_discriminator = BASE.Discord.user.discriminator,
		bot_avatar_url = str(BASE.Discord.user.avatar_url)
	)
	return discord

def getUniqueDiscordMember(guilds:list) -> int:
	unique_member:list = []

	for guild in guilds:
		for member in guild.members:
			if member.id not in unique_member: unique_member.append(member.id)

	return len(unique_member)
