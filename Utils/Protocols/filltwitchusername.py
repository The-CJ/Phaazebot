"""
This protocol will try to complete all entry's from the databases
twitch_user_name table.

To be exact it tries to get a username entry for every twitch id,
somewhere in the database.
twitch_user, discord_twitch_alert, twitch_channel, etc...

CLI Args:
---------
* `a` or `automated` [disable print]
* `d` or `detailed` [additional information printed]

CLI KWArgs:
---------
* `config` [alternate path to config file]
"""
from typing import Optional
import os
import sys
base_dir:str = f"{os.path.dirname(os.path.abspath(__file__))}/../.."
sys.path.insert(0, base_dir)

import asyncio
from typing import List
from Utils.Classes.dbconn import DBConn
from Utils.Classes.twitchuser import TwitchUser
from main import Phaazebot
from Platforms.Twitch.api import getTwitchUsers
from Utils.config import ConfigParser
from Utils.cli import CliArgs
from Utils.startuptastk import loadInTwitchClientCredentials

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

PER_ITER:int = 50

class FillTwitchUserNames(object):
	def __init__(self):
		self.detailed:bool = False
		self.log_func:callable = print
		self.loop:asyncio.AbstractEventLoop = asyncio.new_event_loop()

	def log(self, txt:str) -> None:
		if bool(self.log_func):
			txt = f"({self.__class__.__name__}) {txt}"
			self.log_func(txt)

	def main(self) -> None:
		self.log("This Protocol required Twitch access, running loadInTwitchClientCredentials() from startuptastks")
		loadInTwitchClientCredentials(Phaaze)
		self.loop.run_until_complete(self.asyncMain())

	async def asyncMain(self) -> None:

		empty_entrys:List[str] = await self.gatherMissingDBEntrys()
		user_list:List[TwitchUser] = []
		self.log("Gathering information for missing names, this may take a while...")

		while len(empty_entrys) > 0:
			take_50:List[str] = empty_entrys[:PER_ITER]
			if self.detailed: self.log(f"Running checks for {len(take_50)} entry^'s")
			if self.detailed: self.log("    "+str(take_50))
			empty_entrys = empty_entrys[PER_ITER:] # 'shift' 50 to left

			find_50:List[TwitchUser] = await getTwitchUsers(Phaaze, take_50)
			if self.detailed: self.log(f"Received information's for {len(find_50)} twitch user")
			if self.detailed: self.log("    "+str(find_50))

			user_list += find_50 # add to results
			if empty_entrys: await asyncio.sleep(3) # we wait because twitch likes timing out everyone

		return await self.insertDataInDB(user_list)

	async def gatherMissingDBEntrys(self) -> List[str]:

		self.log("Selecting missing or empty twitch usernames from all tables...")
		empty_entrys:list = DB.selectQuery("""
			WITH `collection` AS (
				SELECT DISTINCT `twitch_user`.`user_id`
				FROM `twitch_user`

				UNION DISTINCT
				SELECT DISTINCT `twitch_channel`.`channel_id`
				FROM `twitch_channel`

				UNION DISTINCT
				SELECT DISTINCT `discord_twitch_alert`.`twitch_channel_id`
				FROM `discord_twitch_alert`
			)
			SELECT `collection`.`user_id`
			FROM `collection`
			LEFT JOIN `twitch_user_name`
				ON `collection`.`user_id` = `twitch_user_name`.`user_id`
			WHERE `twitch_user_name`.`user_display_name` IS NULL
				OR `twitch_user_name`.`user_name` IS NULL"""
		)

		if not empty_entrys:
			self.log("No empty entry's found!")
			return []

		self.log(f"Found {len(empty_entrys)} ID's with missing names")
		return [str(i["user_id"]) for i in empty_entrys]

	async def insertDataInDB(self, twitch_users:List[TwitchUser]) -> None:
		if not twitch_users:
			self.log("Can't insert new data in DB, results are empty")
			return

		self.log(f"Inserting received entry's for {len(twitch_users)} Twitch-Userinfo")

		sql:str = "INSERT INTO `twitch_user_name` (`user_id`, `user_name`, `user_display_name`) VALUES " + ", ".join("(%s, %s, %s)" for x in twitch_users if x)
		sql_values:tuple = ()

		for User in twitch_users:
			sql_values += (User.user_id, User.login, User.display_name)
			if self.detailed: self.log(f"    Update entry, ID={User.user_id} (display)name='{User.display_name}'")

		sql += " ON DUPLICATE KEY UPDATE `user_name` = VALUES(`user_name`), `user_display_name` = VALUES(`user_display_name`)"
		
		DB.query(sql, sql_values)


if __name__ == '__main__':
	# get cli args
	automated:bool = any([CliArgs.get("a"), CliArgs.get("automated")])
	detailed:bool = any([CliArgs.get("d"), CliArgs.get("detailed")])

	Protocol:FillTwitchUserNames = FillTwitchUserNames()

	if automated:
		Protocol.log_func = None

	if detailed:
		Protocol.detailed = detailed

	Protocol.log("Starting Protocol...")
	Protocol.main()
	Protocol.log("Protocol finished")
