from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex

import json
from aiohttp.web import Response, Request
from Utils.Classes.webrequestcontent import WebRequestContent
from Utils.Classes.webuserinfo import WebUserInfo
from Utils.Classes.undefined import UNDEFINED
from Utils.dbutils import validateDBInput
from Utils.stringutils import password as password_function
from Platforms.Web.db import getWebUsers
from Platforms.Web.Processing.Api.errors import (
	apiMissingData,
	apiNotAllowed,
	apiUserNotFound
)

async def apiAdminUsersRemoverole(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
	Default url: /api/admin/users?operation=removerole
	"""
	pass
