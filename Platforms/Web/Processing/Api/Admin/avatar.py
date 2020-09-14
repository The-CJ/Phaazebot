from typing import TYPE_CHECKING, Coroutine
if TYPE_CHECKING:
	from Platforms.Discord.main_discord import PhaazebotDiscord
	from Platforms.Web.index import WebIndex

import asyncio
from aiohttp.web_request import FileField
from aiohttp.web import Response, Request
from Utils.Classes.webrequestcontent import WebRequestContent
from Utils.Classes.webuserinfo import WebUserInfo
from Platforms.Web.Processing.Api.errors import apiNotAllowed, apiMissingValidMethod, apiMissingData

async def apiAdminAvatar(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
	Default url: /api/admin/avatar
	"""
	WebUser:WebUserInfo = await cls.getWebUserInfo(WebRequest)
	if not WebUser.checkRoles(["admin", "superadmin"]): return await apiNotAllowed(cls, WebRequest, msg="Admin rights required")

	Data:WebRequestContent = WebRequestContent(WebRequest, force_method="unpackPost")
	await Data.load()

	platform:str = Data.getStr("platform", None)

	if platform == "discord":
		return await apiAdminAvatarDiscord(cls, WebRequest, Data)

	else: return await apiMissingValidMethod(cls, WebRequest, msg=f"'{platform}' is not a known platform")

async def apiAdminAvatarDiscord(cls:"WebIndex", WebRequest:Request, Data:WebRequestContent) -> Response:
	"""
	Default url: /api/admin/avatar?platform=discord
	"""
	PhaazeDiscord:"PhaazebotDiscord" = cls.Web.BASE.Discord
	if not PhaazeDiscord: return await apiNotAllowed(cls, WebRequest, msg="Discord module is not active")

	AvatarData:FileField = Data.get("file", None)
	if not AvatarData:
		return await apiMissingData(cls, WebRequest)

	avatar_as_bytes:bytes = AvatarData.file.read()
	change_coro:Coroutine = PhaazeDiscord.user.edit(avatar=avatar_as_bytes)

	WaitForDiscord:asyncio.Event = asyncio.Event()

	AvatarChangeTask:asyncio.Task = asyncio.ensure_future(change_coro, loop=PhaazeDiscord.BASE.DiscordLoop)
	AvatarChangeTask.add_done_callback(lambda x: WaitForDiscord.set())
	await WaitForDiscord.wait()

	# TODO: test error inputs
	print(AvatarChangeTask.result())
