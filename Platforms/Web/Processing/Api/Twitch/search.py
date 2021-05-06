from typing import TYPE_CHECKING, List, Union
if TYPE_CHECKING:
	from Platforms.Twitch.main_twitch import PhaazebotTwitch
	from Platforms.Web.main_web import PhaazebotWeb

import json
import discord
from aiohttp.web import Response
from Utils.Classes.webrequestcontent import WebRequestContent
from Utils.Classes.extendedrequest import ExtendedRequest
from Utils.Classes.twitchuser import TwitchUser
from Platforms.Web.Processing.Api.errors import apiNotAllowed, apiMissingData, apiNotFound
from Platforms.Web.index import PhaazeWebIndex
from Platforms.Twitch.api import getTwitchUsers


SEARCH_OPTIONS:List[str] = ["channel", "user"]

@PhaazeWebIndex.view("/api/twitch/search")
async def apiDiscordSearch(cls:"PhaazebotWeb", WebRequest:ExtendedRequest) -> Response:
	"""
	Default url: /api/twitch/search
	"""
	PhaazeTwitch:"PhaazebotTwitch" = cls.BASE.Twitch
	if not PhaazeTwitch: return await cls.Tree.errors.notAllowed(cls, WebRequest, msg="Twitch module is not active")

	Data:WebRequestContent = WebRequestContent(WebRequest)
	await Data.load()

	search:str = Data.getStr("search", "", len_max=128)
	term:str = Data.getStr("term", "", len_max=512)

	if search not in SEARCH_OPTIONS:
		return await apiMissingData(cls, WebRequest, msg="missing or invalid 'search', allowed: " + ", ".join(SEARCH_OPTIONS))

	if not term:
		return await apiMissingData(cls, WebRequest, msg="invalid or missing 'term'")

	if search == "channel":
		return await searchChannel(cls, WebRequest, Data)

	if search == "user":
		return await searchUser(cls, WebRequest, Data)

async def searchChannel(cls:"PhaazebotWeb", WebRequest:ExtendedRequest, Data:WebRequestContent) -> Response:

	search_term:str = Data.getStr("term", "", len_max=128)

	res:List[TwitchUser] = await getTwitchUsers(cls.BASE, item=search_term, item_type="login")
	if not res:
		return await apiNotFound(cls, WebRequest)
	else:
		SearchUser:TwitchUser = res.pop(0)
		data: dict = {
			"id":str(SearchUser.user_id),
			"display_name":str(SearchUser.display_name),
			"login":str(SearchUser.login),
		}

		return cls.response(
			text=json.dumps(
				dict(result=data, status=200)
			),
			content_type="application/json",
			status=200
		)

async def searchUser(cls:"PhaazebotWeb", WebRequest:ExtendedRequest, Data:WebRequestContent) -> Response:
	...
