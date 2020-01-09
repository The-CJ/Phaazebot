import datetime
from Utils.Classes.undefined import UNDEFINED

class OsuUser(object):
	"""
		Represents a osu! user with all its stats in a specific game mode
	"""
	def __repr__(self):
		return f"<{self.__class__.__name__} name='{self.username}' mode='{self.mode}'>"

	def __init__(self, data:dict, mode:str="0"):
		self.mode_number:str = mode
		self.user_id:str = data.get("user_id", UNDEFINED)
		self.username:str = data.get("username", UNDEFINED)

		self.JoinDate:datetime.datetime = datetime.datetime.fromisoformat( data.get("join_date", "1970-01-01 00:00:00") )

		self.count300:str = data.get("count300", UNDEFINED)
		self.count100:str = data.get("count100", UNDEFINED)
		self.count50:str = data.get("count50", UNDEFINED)

		self.playcount:str = data.get("playcount", UNDEFINED)

		self.ranked_score:str = data.get("ranked_score", UNDEFINED)
		self.total_score:str = data.get("total_score", UNDEFINED)

		self.pp_rank:str = data.get("pp_rank", UNDEFINED)
		self.pp_country_rank:str = data.get("pp_country_rank", UNDEFINED)
		self.level:str = data.get("level", UNDEFINED)
		self.pp_raw:str = data.get("pp_raw", UNDEFINED)
		self.accuracy:str = data.get("accuracy", UNDEFINED)

		self.count_rank_ssh:str = data.get("count_rank_ssh", UNDEFINED)
		self.count_rank_ss:str = data.get("count_rank_ss", UNDEFINED)
		self.count_rank_sh:str = data.get("count_rank_sh", UNDEFINED)
		self.count_rank_s:str = data.get("count_rank_s", UNDEFINED)
		self.count_rank_a:str = data.get("count_rank_a", UNDEFINED)

		self.country:str = data.get("country", UNDEFINED)

		self.total_seconds_played:str = data.get("total_seconds_played", UNDEFINED)

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

		j["mode"] = str(self.mode)
		j["user_id"] = str(self.user_id)
		j["username"] = str(self.username)
		j["join_date"] = str(self.JoinDate)
		j["playcount"] = str(self.playcount)
		j["country"] = str(self.country)
		j["ranked_score"] = str(self.ranked_score)
		j["total_score"] = str(self.total_score)
		j["pp_rank"] = str(self.pp_rank)
		j["pp_country_rank"] = str(self.pp_country_rank)
		j["level"] = str(self.level)
		j["pp_raw"] = str(self.pp_raw)
		j["accuracy"] = str(self.accuracy)
		j["total_seconds_played"] = str(self.total_seconds_played)

		if count_objects:
			j["count300"] = str(self.count300)
			j["count100"] = str(self.count100)
			j["count50"] = str(self.count50)

		if ranks:
			j["count_rank_ssh"] = str(self.count_rank_ssh)
			j["count_rank_ss"] = str(self.count_rank_ss)
			j["count_rank_sh"] = str(self.count_rank_sh)
			j["count_rank_s"] = str(self.count_rank_s)
			j["count_rank_a"] = str(self.count_rank_a)

		return j
