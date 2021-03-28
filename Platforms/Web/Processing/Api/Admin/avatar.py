from typing import TYPE_CHECKING, Coroutine
if TYPE_CHECKING:
	from Platforms.Web.main_web import PhaazebotWeb
	from Platforms.Discord.main_discord import PhaazebotDiscord

import json
import asyncio
from aiohttp.web_request import FileField
from aiohttp.web import Response
from Utils.Classes.webrequestcontent import WebRequestContent
from Utils.Classes.authwebuser import AuthWebUser
from Utils.Classes.extendedrequest import ExtendedRequest
from Platforms.Web.index import PhaazeWebIndex
from Platforms.Web.utils import authWebUser

@PhaazeWebIndex.view("/api/admin/avatar")
async def apiAdminAvatar(cls:"PhaazebotWeb", WebRequest:ExtendedRequest) -> Response:
	"""
	Default url: /api/admin/avatar
	"""
	WebAuth:AuthWebUser = await authWebUser(cls, WebRequest)
	if not WebAuth.found:
		return await cls.Tree.Api.errors.apiMissingAuthorisation(WebRequest)
	if not WebAuth.User.checkRoles(["admin", "superadmin"]):
		return await cls.Tree.Api.errors.apiNotAllowed(WebRequest, msg="Admin rights required")

	Data:WebRequestContent = WebRequestContent(WebRequest, force_method="unpackPost")
	await Data.load()

	platform:str = Data.getStr("platform", None)

	if platform == "discord":
		return await apiAdminAvatarDiscord(cls, WebRequest, Data)

	else: return await cls.Tree.Api.errors.apiMissingValidMethod(cls, WebRequest, msg=f"'{platform}' is not a known platform")

async def apiAdminAvatarDiscord(cls:"PhaazebotWeb", WebRequest:ExtendedRequest, Data:WebRequestContent) -> Response:
	"""
	Default url: /api/admin/avatar?platform=discord
	"""
	DISCORD_TIMEOUT:int = 120
	PhaazeDiscord:"PhaazebotDiscord" = cls.BASE.Discord
	if not PhaazeDiscord: return await cls.Tree.Api.errors.apiNotAllowed(cls, WebRequest, msg="Discord module is not active")

	AvatarData:FileField = Data.get("file", None)
	if not AvatarData or type(AvatarData) is not FileField:
		return await cls.Tree.Api.errors.apiMissingData(cls, WebRequest, msg="missing or invalid `file`")

	avatar_as_bytes:bytes = AvatarData.file.read()
	change_coro:Coroutine = PhaazeDiscord.user.edit(avatar=avatar_as_bytes)

	WaitForDiscord:asyncio.Event = asyncio.Event()

	AvatarChangeTask:asyncio.Future = asyncio.ensure_future(change_coro, loop=PhaazeDiscord.BASE.DiscordLoop)
	AvatarChangeTask.add_done_callback(lambda x: WaitForDiscord.set())
	# NOTE (for my later self), calling `await asyncio.wait_for` here, will snap the processing to somewhere in aiohttp, that listens to new request,
	# only after... something happens, this coro will continue since its marked with call_soon
	# So it the server is somewhat busy, everything should go smoothly
	try: await asyncio.wait_for(WaitForDiscord.wait(), DISCORD_TIMEOUT)
	except: pass

	if not AvatarChangeTask.done():
		AvatarChangeTask.cancel()
		return await cls.Tree.Api.errors.apiTimeout(cls, WebRequest, time=DISCORD_TIMEOUT)

	try:
		AvatarChangeTask.result() # if everything is ok, return value should be none
		return cls.response(
			text=json.dumps(dict(msg="Avatar change successfully", status=200)),
			content_type="application/json",
			status=200
		)
	except Exception as E:
		return cls.response(
			text=json.dumps(dict(msg="Avatar change failed", exception=str(E), status=400)),
			content_type="application/json",
			status=400
		)
