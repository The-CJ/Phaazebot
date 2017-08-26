#BASE.moduls.logging_

import discord, json, datetime

def log_server(server, method):

	with open("STUFF/LOGS/server_logs.txt", "a", encoding="UTF-8") as save:
		save.write("{0} | {1}:{2} - {3}\n".format(
													datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
													"Joined" if method == "add" else "Leaved",
													server.id,
													server.name))
		save.close()

def log_member(member, method):

	with open("STUFF/LOGS/member_logs.txt", "a", encoding="UTF-8") as save:
		save.write("{0} | {1} - {2} | {3}:{4} - {5}\n".format(
													datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
													member.id,
													member.name,
													"Joined" if method == "add" else "Leaved",
													member.server.id,
													member.server.name))
		save.close()
