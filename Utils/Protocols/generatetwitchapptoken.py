#
# This protocol will generate
# discord_user table.
#
# To be exact the on_server field.
# Only guilds, phaaze currenty is on are checked.
# This protocol is suppost to try if a member is on server and update db.
#

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

Phaaze:Phaazebot = Phaazebot()
DB:DBConn = DBConn(
	host = Phaaze.Config.get("phaazedb_host", "localhost"),
	port = Phaaze.Config.get("phaazedb_port", "3306"),
	user = Phaaze.Config.get("phaazedb_user", "phaaze"),
	passwd = Phaaze.Config.get("phaazedb_password", ""),
	database = Phaaze.Config.get("phaazedb_database", "phaaze")
)

MIN_LIFETIME:datetime.timedelta = datetime.timedelta(days=3) # renew token if only 3 days are left

def generateNewToken() -> None:
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
		)
	)

	token:str = response.get("access_token", "ERROR")
	print("New Token generated: " + token)

def checkToken(db_entry:dict) -> None:

	token_info:dict = json.loads( db_entry["value"] )

	Now:datetime.datetime = datetime.datetime.now()
	ExpiresAt:datetime.datetime = datetime.datetime.fromisoformat( token_info.get("expires_at", "2000-01-01") )

	if (ExpiresAt - MIN_LIFETIME) < Now:
		print("Current token is about to expire -> renewing")
		return generateNewToken()

	print("Current token still valid")
	print("Valid until: " + str(ExpiresAt))
	print("Renew scheduled: " + str( ExpiresAt - MIN_LIFETIME ))

def main() -> None:

	# get current entry for twitch_client_credentials
	res:list = DB.selectQuery("SELECT * FROM `setting` WHERE `key` = 'twitch_client_credentials'")
	if not res:
		return generateNewToken()

	else:
		return checkToken(res[0])

if __name__ == '__main__':
	print("Starting Protocol...")

	main()

	print("Protocol finished")
