"""
This protocol generate a new twitch token
it only renews the token if needed

CLI Args:
---------
* `f` or `force` [force renew]
* `a` or `automated` [disable print]
"""

import os
import sys
sys.path.insert(0, f"{os.path.dirname(__file__)}/../../")

import json
import requests
import datetime
import urllib.parse
from main import Phaazebot
from Platforms.Twitch import api as twitch_api
from Utils.Classes.dbconn import DBConn
from Utils.cli import CliArgs

Phaaze:Phaazebot = Phaazebot()
DB:DBConn = DBConn(
	host = Phaaze.Config.get("phaazedb_host", "localhost"),
	port = Phaaze.Config.get("phaazedb_port", "3306"),
	user = Phaaze.Config.get("phaazedb_user", "phaaze"),
	passwd = Phaaze.Config.get("phaazedb_password", ""),
	database = Phaaze.Config.get("phaazedb_database", "phaaze")
)

MIN_LIFETIME:datetime.timedelta = datetime.timedelta(days=3) # renew token if only 3 days are left

class GenerateTwitchCredentials(object):
	def __init__(self):
		self.force:str = False
		self.log_func:callable = print

	def log(self, txt:str) -> None:
		if bool(self.log_func):
			txt = f"({self.__class__.__name__}) {txt}"
			self.log_func(txt)

	def main(self) -> str:
		# get current entry for twitch_client_credentials
		res:list = DB.selectQuery("SELECT * FROM `setting` WHERE `key` = 'twitch_client_credentials'")
		if not res:
			self.log("No Token entry found -> creating...")
			return self.generateNewToken()

		else:
			return self.checkToken(res[0])

	def generateNewToken(self) -> str:
		req:dict = dict()
		req["client_id"] = Phaaze.Access.TWITCH_CLIENT_ID
		req["client_secret"] = Phaaze.Access.TWITCH_CLIENT_SECRET
		req["grant_type"] = "client_credentials"

		target_url:str = twitch_api.AUTH_URL + "oauth2/token?" + urllib.parse.urlencode(req)
		response:dict = ( requests.request("POST", target_url) ).json()

		# get more infos
		lifeseconds:int = response.get("expires_in", 0)
		Now:datetime.datetime = datetime.datetime.now()
		LifeTime:datetime.timedelta = datetime.timedelta(seconds=lifeseconds)

		# add some data to help us
		response["created_at"] = str( Now )
		response["expires_at"] = str( Now + LifeTime )

		DB.insertQuery(
			table = "setting",
			content = dict(
				key = "twitch_client_credentials",
				value = json.dumps(response)
			),
			replace = True
		)

		new_token:str = response.get("access_token", "ERROR")
		self.log("New Token generated: " + new_token)
		return new_token

	def checkToken(self, db_entry:dict) -> str:

		token_info:dict = json.loads( db_entry["value"] )

		Now:datetime.datetime = datetime.datetime.now()
		ExpiresAt:datetime.datetime = datetime.datetime.fromisoformat( token_info.get("expires_at", "2000-01-01") )

		if (ExpiresAt - MIN_LIFETIME) < Now:
			self.log("Current twitch_client_credentials are about to expire -> renewing...")
			return self.generateNewToken()

		if self.force:
			self.log("Forcing new token...")
			return self.generateNewToken()

		self.log("Current token still valid")
		self.log("Valid until: " + str(ExpiresAt))
		self.log("Renew scheduled: " + str( ExpiresAt - MIN_LIFETIME ))
		return token_info.get("access_token", "ERROR")

if __name__ == '__main__':
	# get cli args
	force_renew:bool = any( [CliArgs.get("f"), CliArgs.get("force")] )
	automated:bool = any( [CliArgs.get("a"), CliArgs.get("automated")] )

	Protocol:GenerateTwitchCredentials = GenerateTwitchCredentials()

	if force_renew:
		Protocol.force = True

	if automated:
		Protocol.log_func = None

	Protocol.log("Starting Protocol...")
	Protocol.main()
	Protocol.log("Protocol finished")