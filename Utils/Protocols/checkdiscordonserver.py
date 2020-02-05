#
# This protocol will try to check all entrys in the databases
# discord_user table.
#
# To be exact the on_server field.
# Only guilds, phaaze currenty is on are checked.
# This protocol is suppost to try if a member is on server and update db.
#

import os
import sys
sys.path.insert(0, f"{os.path.dirname(__file__)}/../../")

import discord
import asyncio
from Utils.Classes.dbconn import DBConn
from Utils.config import ConfigParser

Configs:ConfigParser = ConfigParser()

class PhaazeDiscordConnection(discord.Client):
	""" Discord connection for running the protocol """
	def __init__(self):
		super().__init__()

	async def on_ready(self) -> None:
		print("Discord Connectet!")

		# gather data from DB
		DBC:DBConn = DBConn(
			host = Configs.get("phaazedb_host", "localhost"),
			port = Configs.get("phaazedb_port", "3306"),
			user = Configs.get("phaazedb_user", "phaaze"),
			passwd = Configs.get("phaazedb_password", ""),
			database = Configs.get("phaazedb_database", "phaaze")
		)

		print("Connecting to Database...")
		print(f"Requesting memberlist of {len(self.guilds)} guilds")

		guild_id_list:str = ", ".join([str(g.id) for g in self.guilds])
		check_entrys:list = DBC.selectQuery(f"""
			SELECT `id`, `guild_id`, `member_id`
			FROM `discord_user`
			WHERE `discord_user`.`guild_id` IN ({guild_id_list})"""
		)

		print(f"Found {len(check_entrys)} checkable entrys, running checks")

		on_server:list = list()
		not_on_server:list = list()

		for entry in check_entrys:

			entry_id:int = entry.get("id", 0)
			guild_id:str = entry.get("guild_id", "0")
			member_id:str = entry.get("member_id", "0")

			guild_id:int = int(guild_id) if guild_id.isdigit() else 0
			member_id:int = int(member_id) if member_id.isdigit() else 0

			if not (entry_id and member_id and guild_id):
				print(f"    Invalid entry: {str(entry)}")
				continue

			Guild:discord.Guild = self.get_guild(guild_id)
			if not Guild:
				print(f"    Could not find a Guild for entry: {str(entry)}")
				continue

			Member:discord.Member = Guild.get_member(member_id)
			# if member is not none, its on server
			if Member:
				on_server.append(entry_id)
			else:
				not_on_server.append(entry_id)

		print("Analytics complete")
		print(f"{len(not_on_server)} entrys found that are not on server")
		print(f"{len(on_server)} entrys found that are on server")

		print("Updating DB")

		# ensure no empty list
		on_server.append(0)
		not_on_server.append(0)

		# build sql
		on_server_str:str = ", ".join([str(i) for i in on_server])
		not_on_server_str:str = ", ".join([str(i) for i in not_on_server])

		DBC.query(f"""
			UPDATE `discord_user`
			SET `on_server` = CASE
				WHEN `id` IN ({on_server_str}) THEN 1
				WHEN `id` IN ({not_on_server_str}) THEN 0
				ELSE `on_server` END"""
		)

		print("Protocol complete, logging out")
		await self.logout()

if __name__ == '__main__':

	Loop:asyncio.AbstractEventLoop = asyncio.new_event_loop()
	asyncio.set_event_loop(Loop)

	print("Starting Protocol...")

	PDC:PhaazeDiscordConnection = PhaazeDiscordConnection()

	token:str = Configs.get("discord_token","")
	print("Connecting to Discord...")
	Loop.run_until_complete( PDC.start(token) )
