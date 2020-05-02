"""
This protocol will try to complete all entrys from the databases
discord_twitch_alert table.

To be exact the discord_guild_id field.
Because its not really needed for the alerts, but of stat listing etc.
This protocol is suppost to try finding the GuildID based on the ChannelID

CLI Args:
---------
* `a` or `automated` [disable log]
"""

import os
import sys
sys.path.insert(0, f"{os.path.dirname(__file__)}/../../")

import discord
from Utils.Classes.dbconn import DBConn
from main import Phaazebot
from Utils.cli import CliArgs

automated:bool = any( [CliArgs.get("a"), CliArgs.get("automated")] )

Phaaze:Phaazebot = Phaazebot()
DBC:DBConn = DBConn(
	host = Phaaze.Config.get("phaazedb_host", "localhost"),
	port = Phaaze.Config.get("phaazedb_port", "3306"),
	user = Phaaze.Config.get("phaazedb_user", "phaaze"),
	passwd = Phaaze.Config.get("phaazedb_password", ""),
	database = Phaaze.Config.get("phaazedb_database", "phaaze")
)

def log(x) -> None:
	if not automated: print(x)

def getIncompleteEntrys() -> list:
	sql:str = """
		SELECT *
		FROM `discord_twitch_alert`
		WHERE `discord_twitch_alert`.`discord_guild_id` IS NULL
			OR `discord_twitch_alert`.`discord_guild_id` IN ('', '-', ' ')"""

	empty_entrys:list = DBC.selectQuery(sql)

	if not empty_entrys:
		log("No empty entrys found!")
		log("Protocol finished.")
		exit(0)

	log(f"Found {len(empty_entrys)} entrys with missing guild_id")
	return empty_entrys

def main() -> None:
	entrys_todo:list = getIncompleteEntrys()
	token:str = Phaaze.Config.get("discord_token","")
	PDC:PhaazeDiscordConnection = PhaazeDiscordConnection(entrys_todo)
	PDC.run(token)

class PhaazeDiscordConnection(discord.Client):
	""" Discord connection for running the protocol """
	def __init__(self, empty_entrys:list):
		super().__init__()
		self.empty_entrys = empty_entrys

	async def on_ready(self) -> None:
		global DBC
		log("Discord Connectet, running checks...")
		for entry in self.empty_entrys:

			channel_id:str = entry.get("discord_channel_id", "")
			if not channel_id:
				log(f"A entry is missing a discord channel id: {str(entry)}")
				continue

			log(f"Trying to find guild_id for channel_id: {channel_id}")
			FoundChannel:discord.TextChannel = self.get_channel(int(channel_id))

			if not FoundChannel:
				log(f"    Could not find a channel for ID: {channel_id}")
				continue

			guild_id:int = FoundChannel.guild.id
			if not guild_id:
				log(f"    Could not find a guild_id for a found channel")

			log(f"    Found guild_id {guild_id} for channel_id {channel_id}")
			log("    Updateing DB...")
			DBC.updateQuery(
				table = "discord_twitch_alert",
				content = {"discord_guild_id":guild_id},
				where = "`discord_twitch_alert`.`discord_channel_id` = %s",
				where_values = (channel_id,)
			)

			log("    Updated!")

		log("Protocol complete, logging out")
		await self.logout()

if __name__ == '__main__':

	log("Starting Protocol...")

	main()

	log("Protocol finished")
