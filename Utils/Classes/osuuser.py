from datetime import datetime
from Utils.Classes.undefined import UNDEFINED
from Utils.Classes.contentclass import ContentClass

class OsuUser(ContentClass):
	"""
	Represents a osu! user with all its stats in a specific game mode
	"""
	def __repr__(self):
		return f"<{self.__class__.__name__} name='{self.username}' mode='{self.mode}'>"

	def __init__(self, data:dict, mode:str="0"):
		self.mode_number:str = mode
		self.user_id:str = self.asString(data.get("user_id", UNDEFINED))
		self.username:str = self.asString(data.get("username", UNDEFINED))

		self.JoinDate:datetime = self.asDatetime(data.get("join_date", "1970-01-01 00:00:00"))

		self.count300:str = self.asString(data.get("count300", UNDEFINED))
		self.count100:str = self.asString(data.get("count100", UNDEFINED))
		self.count50:str = self.asString(data.get("count50", UNDEFINED))

		self.playcount:str = self.asString(data.get("playcount", UNDEFINED))

		self.ranked_score:str = self.asString(data.get("ranked_score", UNDEFINED))
		self.total_score:str = self.asString(data.get("total_score", UNDEFINED))

		self.pp_rank:str = self.asString(data.get("pp_rank", UNDEFINED))
		self.pp_country_rank:str = self.asString(data.get("pp_country_rank", UNDEFINED))
		self.level:str = self.asString(data.get("level", UNDEFINED))
		self.pp_raw:str = self.asString(data.get("pp_raw", UNDEFINED))
		self.accuracy:str = self.asString(data.get("accuracy", UNDEFINED))

		self.count_rank_ssh:str = self.asString(data.get("count_rank_ssh", UNDEFINED))
		self.count_rank_ss:str = self.asString(data.get("count_rank_ss", UNDEFINED))
		self.count_rank_sh:str = self.asString(data.get("count_rank_sh", UNDEFINED))
		self.count_rank_s:str = self.asString(data.get("count_rank_s", UNDEFINED))
		self.count_rank_a:str = self.asString(data.get("count_rank_a", UNDEFINED))

		self.country:str = self.asString(data.get("country", UNDEFINED))

		self.total_seconds_played:str = self.asString(data.get("total_seconds_played", UNDEFINED))

	@property
	def mode(self) -> str:
		if self.mode_number == "0": return "osu!"
		elif self.mode_number == "1": return "osu!taiko"
		elif self.mode_number == "2": return "osu!ctb"
		elif self.mode_number == "3": return "osu!mania"
		else: return "Unknown"

	def toJSON(self, count_objects:bool=True, ranks:bool=True) -> dict:
		""" Returns a json save dict representation of all values for API, storage, etc... """

		j:dict = dict()

		j["mode"] = self.asString(self.mode)
		j["user_id"] = self.asString(self.user_id)
		j["username"] = self.asString(self.username)
		j["join_date"] = self.asString(self.JoinDate)
		j["playcount"] = self.asString(self.playcount)
		j["country"] = self.asString(self.country)
		j["ranked_score"] = self.asString(self.ranked_score)
		j["total_score"] = self.asString(self.total_score)
		j["pp_rank"] = self.asString(self.pp_rank)
		j["pp_country_rank"] = self.asString(self.pp_country_rank)
		j["level"] = self.asString(self.level)
		j["pp_raw"] = self.asString(self.pp_raw)
		j["accuracy"] = self.asString(self.accuracy)
		j["total_seconds_played"] = self.asString(self.total_seconds_played)

		if count_objects:
			j["count300"] = self.asString(self.count300)
			j["count100"] = self.asString(self.count100)
			j["count50"] = self.asString(self.count50)

		if ranks:
			j["count_rank_ssh"] = self.asString(self.count_rank_ssh)
			j["count_rank_ss"] = self.asString(self.count_rank_ss)
			j["count_rank_sh"] = self.asString(self.count_rank_sh)
			j["count_rank_s"] = self.asString(self.count_rank_s)
			j["count_rank_a"] = self.asString(self.count_rank_a)

		return j
