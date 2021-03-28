from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from phaazebot import Phaazebot

import json

def initStartupTasks(cls:"Phaazebot") -> None:
	"""
	This function is called on startup from phaaze,
	its called before phaaze starts the mainframe

	(its probably, mainly used to load in values from the db)
	"""

	loadInTwitchClientCredentials(cls)

	cls.Logger.info("Startup tasks finished")

def loadInTwitchClientCredentials(cls:"Phaazebot") -> None:
	res:list = cls.PhaazeDB.selectQuery("SELECT * FROM `setting` WHERE `key` = 'twitch_client_credentials'")

	if not res:
		cls.Logger.critical("Can't find `twitch_client_credentials` in DB")
		exit(1)

	res:dict = json.loads(res[0]["value"])
	cls.Access.twitch_client_credential_token = res.get("access_token", "[NOT FOUND]")
	cls.Logger.debug("Loaded twitch_client_credentials token", require="startup")
