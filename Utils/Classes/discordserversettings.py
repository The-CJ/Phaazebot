from Utils.Classes.undefined import Undefined
from Utils.Classes.dbcontentclass import DBContentClass

class DiscordServerSettings(DBContentClass):
	"""
		Contains and represents all possible discord server settings
	"""
	def __init__(self, infos:dict = {}):

		self.__found = False
		if infos:
			self.__found = True

		self.autorole_id:str = infos.get("autorole_id", Undefined())
		self.ban_links:bool = bool( infos.get("ban_links", Undefined()) )
		self.ban_links_role:list = self.fromJsonField( infos.get("ban_links_role", Undefined()) )
		self.ban_links_whitelist:list = self.fromJsonField( infos.get("ban_links_whitelist", Undefined()) )
		self.blacklist_words:list = self.fromJsonField( infos.get("blacklist_words", Undefined()) )
		self.blacklist_punishment:str = infos.get("blacklist_punishment", Undefined())
		self.currency_name:str = infos.get("currency_name", Undefined())
		self.currency_name_multi:str = infos.get("currency_name_multi", Undefined())
		self.disable_chan_level:list = self.fromJsonField( infos.get("disable_chan_level", Undefined()) )
		self.disable_chan_normal:list = self.fromJsonField( infos.get("disable_chan_normal", Undefined()) )
		self.disable_chan_quotes:list = self.fromJsonField( infos.get("disable_chan_quotes", Undefined()) )
		self.enable_chan_ai:list = self.fromJsonField( infos.get("enable_chan_ai", Undefined()) )
		self.enable_chan_game:list = self.fromJsonField( infos.get("enable_chan_game", Undefined()) )
		self.enable_chan_nsfw:list = self.fromJsonField( infos.get("enable_chan_nsfw", Undefined()) )
		self.leave_chan:str = infos.get("leave_chan", Undefined())
		self.leave_msg:str = infos.get("leave_msg", Undefined())
		self.level_announce_channel:str = infos.get("level_announce_channel", Undefined())
		self.level_custom_message:str = infos.get("level_custom_msg", Undefined())
		self.owner_disable_level:bool = bool( infos.get("owner_disable_level", Undefined()) )
		self.owner_disable_normal:bool = bool( infos.get("owner_disable_normal", Undefined()) )
		self.owner_disable_regular:bool = bool( infos.get("owner_disable_regular", Undefined()) )
		self.owner_disable_mod:bool = bool( infos.get("owner_disable_mod", Undefined()) )
		self.server_id:str = infos.get("guild_id", Undefined())
		self.track_channel:str = infos.get("track_channel", Undefined())
		self.track_options:list = self.fromJsonField( infos.get("track_options", Undefined()) )
		self.welcome_chan:str = infos.get("welcome_chan", Undefined())
		self.welcome_msg:str = infos.get("welcome_msg", Undefined())
		self.welcome_msg_priv:str = infos.get("welcome_msg_priv", Undefined())

	def __bool__(self):
		return self.__found

	def __repr__(self):
		if self.__found:
			return f"<{self.__class__.__name__} guild_id='{self.server_id}'>"
		else:
			return f"<{self.__class__.__name__} Empty configs>"
