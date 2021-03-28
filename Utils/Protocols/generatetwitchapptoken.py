"""
This protocol generate a new twitch token
it only renews the token if needed

CLI Args:
---------
* `f` or `force` [force renew]
* `a` or `automated` [disable print]

CLI KWArgs:
---------
* `config` [alternate path to config file]

"""
from typing import Optional
import os
import sys
base_dir:str = f"{os.path.dirname(os.path.abspath(__file__))}/../.."
sys.path.insert(0, base_dir)

import json
import requests
import datetime
import urllib.parse
from main import Phaazebot
from Platforms.Twitch import api as twitch_api
from Utils.config import ConfigParser
from Utils.Classes.dbconn import DBConn
from Utils.cli import CliArgs

Conf:Optional[ConfigParser] = None
for config_source_path in [(CliArgs.get("config") or ""), f"{base_dir}/Config/config.phzcf", f"{base_dir}/Config/config.json"]:
	if not config_source_path: continue
	try:
		Conf = ConfigParser(config_source_path)
		break
	except: pass

Phaaze:Phaazebot = Phaazebot(PreConfig=Conf)
DB:DBConn = DBConn(
	host=Phaaze.Config.get("phaazedb_host", "localhost"),
	port=Phaaze.Config.get("phaazedb_port", "3306"),
	user=Phaaze.Config.get("phaazedb_user", "phaaze"),
	passwd=Phaaze.Config.get("phaazedb_password", ""),
	database=Phaaze.Config.get("phaazedb_database", "phaaze")
)

MIN_LIFETIME:datetime.timedelta = datetime.timedelta(days=3) # renew token if only 3 days are left

class GenerateTwitchCredentials(object):
	def __init__(self):
		self.force:bool = False
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
		req["client_id"] = Phaaze.Access.twitch_client_id
		req["client_secret"] = Phaaze.Access.twitch_client_secret
		req["grant_type"] = "client_credentials"

		target_url:str = twitch_api.AUTH_URL + "oauth2/token?" + urllib.parse.urlencode(req)
		response:dict = (requests.request("POST", target_url)).json()

		# get more info's
		lifeseconds:int = response.get("expires_in", 0)
		Now:datetime.datetime = datetime.datetime.now()
		LifeTime:datetime.timedelta = datetime.timedelta(seconds=lifeseconds)

		# add some data to help us
		response["created_at"] = str(Now)
		response["expires_at"] = str(Now + LifeTime)

		DB.insertQuery(
			update_on_duplicate=True,
			table="setting",
			content=dict(
				key="twitch_client_credentials",
				value=json.dumps(response)
			)
		)

		new_token:str = response.get("access_token", "ERROR")
		self.log("New Token generated: " + new_token)
		return new_token

	def checkToken(self, db_entry:dict) -> str:

		token_info:dict = json.loads(db_entry["value"])

		Now:datetime.datetime = datetime.datetime.now()
		ExpiresAt:datetime.datetime = datetime.datetime.fromisoformat(token_info.get("expires_at", "2000-01-01"))

		if (ExpiresAt - MIN_LIFETIME) < Now:
			self.log("Current twitch_client_credentials are about to expire -> renewing...")
			return self.generateNewToken()

		if self.force:
			self.log("Forcing new token...")
			return self.generateNewToken()

		self.log("Current token still valid")
		self.log("Valid until: " + str(ExpiresAt))
		self.log("Renew scheduled: " + str(ExpiresAt - MIN_LIFETIME))
		return token_info.get("access_token", "ERROR")


if __name__ == '__main__':
	# get cli args
	force_renew:bool = any([CliArgs.get("f"), CliArgs.get("force")])
	automated:bool = any([CliArgs.get("a"), CliArgs.get("automated")])

	Protocol:GenerateTwitchCredentials = GenerateTwitchCredentials()

	if force_renew:
		Protocol.force = True

	if automated:
		Protocol.log_func = None

	Protocol.log("Starting Protocol...")
	Protocol.main()
	Protocol.log("Protocol finished")
