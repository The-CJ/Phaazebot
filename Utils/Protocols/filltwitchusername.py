#
# This protocol will try to complete all entrys from the databases
# twitch_user_name table.
#
# To be exact it tryes to get a username entry for every twitch id,
# somewhere in the database.
# twitch_user, discord_twitch_alert, twitch_channel, etc...
#

import os
import sys
sys.path.insert(0, f"{os.path.dirname(__file__)}/../../")

import asyncio
from Utils.Classes.dbconn import DBConn
from Utils.Classes.twitchuser import TwitchUser
from Utils.config import ConfigParser
from main import Phaazebot
from Platforms.Twitch.api import getTwitchUsers

Configs:ConfigParser = ConfigParser()
PER_ITER:int = 50

async def main(empty_entrys:list) -> None:
	Phaaze:Phaazebot = Phaazebot(Config=Configs)

	id_list:list = [i["user_id"] for i in empty_entrys]
	user_list:list = list()

	print("Gathering all found ID's")
	while len(id_list) > 0:
		take_50:list = id_list[:PER_ITER]
		print(f"    Gather another {len(take_50)} ID's")
		id_list = id_list[PER_ITER:]

		find_50:list = await getTwitchUsers(Phaaze, take_50)
		user_list += find_50
		await asyncio.sleep(3)

	return await fillDB(user_list)

async def fillDB(twitch_users:list) -> None:
	global DBC

	if not twitch_users:
		print("Got no user result from Twitch, aborting")
		exit(0)

	print(f"Recived entrys for {len(twitch_users)} Userinfos")

	sql:str = "REPLACE INTO `twitch_user_name` (`user_id`, `user_name`, `user_display_name`) VALUES " + ", ".join("(%s, %s, %s)" for x in twitch_users if x)
	sql_values:tuple = ()

	User:TwitchUser
	for User in twitch_users:

		sql_values += (User.user_id, User.name, User.display_name)
		print(f"    Update entry, ID={User.user_id} (display)name='{User.display_name}'")

	DBC.query(sql, sql_values)
	print("Protocol complete!")

if __name__ == '__main__':

	Loop:asyncio.AbstractEventLoop = asyncio.new_event_loop()
	asyncio.set_event_loop(Loop)

	# gather data from DB
	print("Connecting to Database...")
	DBC:DBConn = DBConn(
		host = Configs.get("phaazedb_host", "localhost"),
		port = Configs.get("phaazedb_port", "3306"),
		user = Configs.get("phaazedb_user", "phaaze"),
		passwd = Configs.get("phaazedb_password", ""),
		database = Configs.get("phaazedb_database", "phaaze")
	)
	empty_entrys:list = DBC.selectQuery("""
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
		print("No empty entrys found!")
		print("Protocol not startet.")
		exit(0)

	print(f"Found {len(empty_entrys)} ID's with missing names")
	print("Starting Protocol...")

	Loop.run_until_complete( main(empty_entrys) )
