"""
This protocol will try to complete all entrys from the databases
discord_twitch_alert table.

To be exact the discord_guild_id field.
Because its not really needed for the alerts, but of stat listing etc.
This protocol is suppost to try finding the GuildID based on the ChannelID

CLI Args:
---------
* `a` or `automated` [disable print]
* `d` or `detailed` [additional information printed]

CLI KWArgs:
---------
* `config` [alternate path to config file]
"""

import os
import sys
base_dir:str = f"{os.path.dirname(os.path.abspath(__file__))}/../.."
sys.path.insert(0, base_dir)

import discord
from typing import List
from Utils.Classes.dbconn import DBConn
from main import Phaazebot
from Utils.config import ConfigParser
from Utils.cli import CliArgs

Conf:ConfigParser = None
for config_source_path in [ (CliArgs.get("config") or ""), f"{base_dir}/Config/config.phzcf", f"{base_dir}/Config/config.json" ]:
	if not config_source_path: continue
	try:
		Conf = ConfigParser(config_source_path)
		break
	except: pass

Phaaze:Phaazebot = Phaazebot(PreConfig = Conf)
DBC:DBConn = DBConn(
	host = Phaaze.Config.get("phaazedb_host", "localhost"),
	port = Phaaze.Config.get("phaazedb_port", "3306"),
	user = Phaaze.Config.get("phaazedb_user", "phaaze"),
	passwd = Phaaze.Config.get("phaazedb_password", ""),
	database = Phaaze.Config.get("phaazedb_database", "phaaze")
)

class CompleteDiscordTwitchAlert(discord.Client):
	def __init__(self):
		super().__init__()
		self.detailed:bool = False
		self.log_func:callable = print
		self.empty_entrys:List[dict] = []

	def log(self, txt:str) -> None:
		if bool(self.log_func):
			txt = f"({self.__class__.__name__}) {txt}"
			self.log_func(txt)

	def main(self) -> None:

		self.empty_entrys = self.getIncompleteEntrys()
		if not self.empty_entrys:
			self.log("Aborting discord connection, no entrys need to be completet")
			return
		else:
			self.log("Starting discord connection...")
			self.run(Phaaze.Access.discord_token)
			# after self.run, the code will continue in self.on_ready
			self.log("Discord disconnected")

	def getIncompleteEntrys(self) -> List[dict]:

		self.log("Selecting emptys with missing guild_id field on table discord_twitch_alert...")
		empty_entrys:List[dict] = DBC.selectQuery("""
			SELECT `discord_twitch_alert`.*
			FROM `discord_twitch_alert`
			WHERE `discord_twitch_alert`.`discord_guild_id` IS NULL
				OR `discord_twitch_alert`.`discord_guild_id` IN ('', '-', ' ')"""
		)

		if not empty_entrys:
			self.log("No empty entrys found!")
			return []

		self.log(f"Found {len(empty_entrys)} entrys with missing guild_id")
		return empty_entrys

	async def on_ready(self) -> None:
		self.log("Discord Connectet, running checks, this may take a while...")

		for entry in self.empty_entrys:

			channel_id:str = str(entry.get("discord_channel_id", ""))
			if not channel_id:
				if self.detailed: self.log(f"    Missing discord channel id: entry = {str(entry)}")
				continue

			FoundChannel:discord.TextChannel = self.get_channel(int(channel_id))
			if not FoundChannel:
				if self.detailed: self.log(f"    Could not find a channel for {channel_id=}")
				continue

			guild_id:int = FoundChannel.guild.id
			if not guild_id:
				if self.detailed: self.log(f"    Could not find a guild_id for {channel_id=}")

			if self.detailed: self.log(f"    Found {guild_id=} for {channel_id=}, updating DB...")
			DBC.updateQuery(
				table = "discord_twitch_alert",
				content = {"discord_guild_id":guild_id},
				where = "`discord_twitch_alert`.`discord_channel_id` = %s",
				where_values = (channel_id,)
			)

		await self.logout() # logout after finished

if __name__ == '__main__':
	# get cli args
	automated:bool = any( [CliArgs.get("a"), CliArgs.get("automated")] )
	detailed:bool = any( [CliArgs.get("d"), CliArgs.get("detailed")] )

	Protocol:CompleteDiscordTwitchAlert = CompleteDiscordTwitchAlert()

	if automated:
		Protocol.log_func = None

	if detailed:
		Protocol.detailed = detailed

	Protocol.log("Starting Protocol...")
	Protocol.main()
	Protocol.log("Protocol finished")
