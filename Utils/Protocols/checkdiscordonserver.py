"""
This protocol will try to check all entrys in the databases
discord_user table.

To be exact the on_server field.
Only guilds, phaaze currenty is on are checked.
This protocol is suppost to try if a member is on server and update db.
"""

import os
import sys
base_dir:str = f"{os.path.dirname(os.path.abspath(__file__))}/../.."
sys.path.insert(0, base_dir)

import discord
from typing import List
from main import Phaazebot
from Utils.Classes.dbconn import DBConn
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

class CheckDiscordOnServer(discord.Client):
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

		self.log("Starting discord connection...")
		self.run(Phaaze.Access.discord_token)
		# after self.run, the code will continue in self.on_ready
		self.log("Discord disconnected")

	async def on_ready(self) -> None:
		self.log("Discord Connectet, gathering DB entrys...")
		self.log(f"Requesting memberlist of {len(self.guilds)} guilds")


		guild_id_list:str = ", ".join([str(g.id) for g in self.guilds])
		if not guild_id_list: guild_id_list = "0"
		check_entrys:List[dict] = DBC.selectQuery(f"""
			SELECT `id`, `guild_id`, `member_id`
			FROM `discord_user`
			WHERE `discord_user`.`guild_id` IN ({guild_id_list})"""
		)

		self.log(f"Found {len(check_entrys)} checkable entrys, running checks, this may take a while...")
		if self.detailed: self.log("    "+str(check_entrys))

		on_server:List[int] = []
		not_on_server:List[int] = []

		for entry in check_entrys:

			entry_id:int = entry.get("id", 0)
			guild_id:str = entry.get("guild_id", "0")
			member_id:str = entry.get("member_id", "0")

			guild_id:int = int(guild_id) if guild_id.isdigit() else 0
			member_id:int = int(member_id) if member_id.isdigit() else 0

			if not (entry_id and member_id and guild_id):
				if self.detailed: self.log(f"    Invalid entry: {str(entry)}")
				continue

			Guild:discord.Guild = self.get_guild(guild_id)
			if not Guild:
				if self.detailed: self.log(f"    Could not find a Guild for entry: {str(entry)}")
				continue

			Member:discord.Member = Guild.get_member(member_id)
			# if member is not none, its on server
			if Member:
				on_server.append(entry_id)
			else:
				not_on_server.append(entry_id)

		self.log("Analytics complete")
		self.log(f"{len(not_on_server)} entrys found that are not on server")
		if self.detailed: self.log("    "+str(not_on_server))
		self.log(f"{len(on_server)} entrys found that are on server")
		if self.detailed: self.log("    "+str(on_server))

		# ensure no empty list
		on_server.append(0)
		not_on_server.append(0)

		# build sql
		on_server_str:str = ", ".join([str(i) for i in on_server])
		not_on_server_str:str = ", ".join([str(i) for i in not_on_server])

		self.log("Running DB Update...")
		DBC.query(f"""
			UPDATE `discord_user`
			SET `on_server` = CASE
				WHEN `id` IN ({on_server_str}) THEN 1
				WHEN `id` IN ({not_on_server_str}) THEN 0
				ELSE `on_server` END"""
		)

		await self.logout()

if __name__ == '__main__':
	automated:bool = any( [CliArgs.get("a"), CliArgs.get("automated")] )
	detailed:bool = any( [CliArgs.get("d"), CliArgs.get("detailed")] )

	Protocol:CheckDiscordOnServer = CheckDiscordOnServer()

	if automated:
		Protocol.log_func = None

	if detailed:
		Protocol.detailed = detailed

	Protocol.log("Starting Protocol...")
	Protocol.main()
	Protocol.log("Protocol finished")
