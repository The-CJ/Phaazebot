#
# This protocol will try to complete all entrys from the databases
# discord_twitch_alert table.
#
# To be exact the discord_guild_id field.
# Because its not really needed for the alerts, but of stat listing etc.
# This protocol is suppost to try finding the GuildID based on the ChannelID
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
	def __init__(self, empty_entrys:list):
		super().__init__()
		self.empty_entrys = empty_entrys

	async def on_ready(self) -> None:
		global DBC
		print("Discord Connectet, running checks...")
		for entry in self.empty_entrys:

			channel_id:str = entry.get("discord_channel_id", "")
			if not channel_id:
				print(f"A entry is missing a discord channel id: {str(entry)}")
				continue

			print(f"Trying to find guild_id for channel_id: {channel_id}")
			FoundChannel:discord.TextChannel = self.get_channel(int(channel_id))

			if not FoundChannel:
				print(f"    Could not find a channel for ID: {channel_id}")
				continue

			guild_id:int = FoundChannel.guild.id
			if not guild_id:
				print(f"    Could not find a guild_id for a found channel")

			print(f"    Found guild_id {guild_id} for channel_id {channel_id}")
			print("    Updateing DB...")
			DBC.updateQuery(
				table = "discord_twitch_alert",
				content = {"discord_guild_id":guild_id},
				where = "`discord_twitch_alert`.`discord_channel_id` = %s",
				where_values = (channel_id,)
			)

			print("    Updated!")

		print("Protocol complete, logging out")
		await self.logout()


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
		SELECT *
		FROM `discord_twitch_alert`
		WHERE `discord_twitch_alert`.`discord_guild_id` IS NULL
			OR `discord_twitch_alert`.`discord_guild_id` IN ('', '-', ' ')"""
	)

	if not empty_entrys:
		print("No empty entrys found!")
		print("Protocol not startet.")
		exit(0)

	print(f"Found {len(empty_entrys)} entrys with missing guild_id")
	print("Starting Protocol...")

	PDC:PhaazeDiscordConnection = PhaazeDiscordConnection(empty_entrys)

	token:str = Configs.get("discord_token","")
	print("Connecting to Discord...")
	Loop.run_until_complete( PDC.start(token) )
