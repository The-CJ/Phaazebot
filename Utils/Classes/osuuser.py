import datetime
from Utils.Classes.undefined import Undefined

class OsuUser(object):
	"""
		Represents a osu! user with all its stats in a specific game mode
	"""
	def __repr__(self):
		return f"<{self.__class__.__name__} name='{self.username}' mode='{self.mode}'>"

	def __init__(self, data:dict, mode:str="0"):
		self.mode_number:str = mode
		self.user_id:str = data.get("user_id", Undefined())
		self.username:str = data.get("username", Undefined())

		self.JoinDate:datetime.datetime = datetime.datetime.fromisoformat( data.get("join_date", "1970-01-01 00:00:00") )

		self.count300:str = data.get("count300", Undefined())
		self.count100:str = data.get("count100", Undefined())
		self.count50:str = data.get("count50", Undefined())

		self.playcount:str = data.get("playcount", Undefined())

		self.ranked_score:str = data.get("ranked_score", Undefined())
		self.total_score:str = data.get("total_score", Undefined())

		self.pp_rank:str = data.get("pp_rank", Undefined())
		self.pp_country_rank:str = data.get("pp_country_rank", Undefined())
		self.level:str = data.get("level", Undefined())
		self.pp_raw:str = data.get("pp_raw", Undefined())
		self.accuracy:str = data.get("accuracy", Undefined())

		self.count_rank_ssh:str = data.get("count_rank_ssh", Undefined())
		self.count_rank_ss:str = data.get("count_rank_ss", Undefined())
		self.count_rank_sh:str = data.get("count_rank_sh", Undefined())
		self.count_rank_s:str = data.get("count_rank_s", Undefined())
		self.count_rank_a:str = data.get("count_rank_a", Undefined())

		self.country:str = data.get("country", Undefined())

		self.total_seconds_played:str = data.get("total_seconds_played", Undefined())

	@property
	def mode(self) -> str:
		if self.mode_number == "0": return "osu!"
		elif self.mode_number == "1": return "osu!taiko"
		elif self.mode_number == "2": return "osu!ctb"
		elif self.mode_number == "3": return "osu!mania"
		else: return "Unknown"
