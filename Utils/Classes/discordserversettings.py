from Utils.Classes.undefined import Undefined

class DiscordServerSettings(object):
	"""
		Contains and represents all possible discord server settings
	"""
	def __init__(self, infos:dict = {}):

		self.autorole:str = infos.get("autorole", Undefined())
		self.ban_links:bool = infos.get("ban_links", Undefined())
		self.ban_links_role:list = infos.get("ban_links_role", Undefined())
		self.ban_links_whitelist:list = infos.get("ban_links_whitelist", Undefined())
		self.blacklist:list = infos.get("blacklist", Undefined())
		self.blacklist_punishment:str = infos.get("blacklist_punishment", Undefined())
		self.disable_chan_custom:list = infos.get("disable_chan_custom", Undefined())
		self.disable_chan_level:list = infos.get("disable_chan_level", Undefined())
		self.disable_chan_normal:list = infos.get("disable_chan_normal", Undefined())
		self.disable_chan_quotes:list = infos.get("disable_chan_quotes", Undefined())
		self.enable_chan_ai:list = infos.get("enable_chan_ai", Undefined())
		self.enable_chan_game:list = infos.get("enable_chan_game", Undefined())
		self.enable_chan_nsfw:list = infos.get("enable_chan_nsfw", Undefined())
		self.leave_chan:str = infos.get("leave_chan", Undefined())
		self.leave_msg:str = infos.get("leave_msg", Undefined())
		self.level_announce_channel:str = infos.get("level_announce_channel", Undefined())
		self.level_custom_message:str = infos.get("level_custom_message", Undefined())
		self.owner_disable_custom:bool = infos.get("owner_disable_custom", Undefined())
		self.owner_disable_level:bool = infos.get("owner_disable_level", Undefined())
		self.owner_disable_mod:bool = infos.get("owner_disable_mod", Undefined())
		self.owner_disable_normal:bool = infos.get("owner_disable_normal", Undefined())
		self.server_id:str = infos.get("server_id", Undefined())
		self.track_channel:str = infos.get("track_channel", Undefined())
		self.track_options:list = infos.get("track_options", Undefined())
		self.welcome_chan:str = infos.get("welcome_chan", Undefined())
		self.welcome_msg:str = infos.get("welcome_msg", Undefined())
		self.welcome_msg_priv:str = infos.get("welcome_msg_priv", Undefined())
