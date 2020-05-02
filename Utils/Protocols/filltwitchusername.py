"""
This protocol will try to complete all entrys from the databases
twitch_user_name table.

To be exact it tryes to get a username entry for every twitch id,
somewhere in the database.
twitch_user, discord_twitch_alert, twitch_channel, etc...

CLI Args:
---------
* `a` or `automated` [disable print]
"""

import os
import sys
sys.path.insert(0, f"{os.path.dirname(__file__)}/../../")

import asyncio
from Utils.Classes.dbconn import DBConn
from Utils.Classes.twitchuser import TwitchUser
from main import Phaazebot
from Platforms.Twitch.api import getTwitchUsers
from Utils.cli import CliArgs

automated:bool = any( [CliArgs.get("a"), CliArgs.get("automated")] )

Phaaze:Phaazebot = Phaazebot()
PER_ITER:int = 50
DB:DBConn = DBConn(
	host = Phaaze.Config.get("phaazedb_host", "localhost"),
	port = Phaaze.Config.get("phaazedb_port", "3306"),
	user = Phaaze.Config.get("phaazedb_user", "phaaze"),
	passwd = Phaaze.Config.get("phaazedb_password", ""),
	database = Phaaze.Config.get("phaazedb_database", "phaaze")
)

def log(x) -> None:
	if not automated: print(x)

def gatherDBEntrys() -> list:
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
		log("No empty entrys found!")
		log("Protocol finished")
		exit(0)

	log(f"Found {len(empty_entrys)} ID's with missing names")
	return empty_entrys

async def main() -> None:

	empty_entrys:list = gatherDBEntrys()

	id_list:list = [i["user_id"] for i in empty_entrys]
	user_list:list = list()

	log("Gathering all found ID's")
	while len(id_list) > 0:
		take_50:list = id_list[:PER_ITER]
		log(f"    Gather another {len(take_50)} ID's")
		id_list = id_list[PER_ITER:]

		find_50:list = await getTwitchUsers(Phaaze, take_50)
		user_list += find_50
		await asyncio.sleep(3)

	return await fillDB(user_list)

async def fillDB(twitch_users:list) -> None:
	if not twitch_users:
		log("Got no user result from Twitch, aborting")
		exit(0)

	log(f"Recived entrys for {len(twitch_users)} Userinfos")

	sql:str = "REPLACE INTO `twitch_user_name` (`user_id`, `user_name`, `user_display_name`) VALUES " + ", ".join("(%s, %s, %s)" for x in twitch_users if x)
	sql_values:tuple = ()

	User:TwitchUser
	for User in twitch_users:

		sql_values += (User.user_id, User.name, User.display_name)
		log(f"    Update entry, ID={User.user_id} (display)name='{User.display_name}'")

	DB.query(sql, sql_values)
	log("Protocol complete!")

if __name__ == '__main__':

	log("Starting Protocol...")

	Loop:asyncio.AbstractEventLoop = asyncio.new_event_loop()
	asyncio.set_event_loop(Loop)
	Loop.run_until_complete( main() )

	log("Protocol finished")
