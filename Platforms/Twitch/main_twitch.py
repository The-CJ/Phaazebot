from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from main import Phaazebot

import twitch_irc
import traceback

class PhaazebotTwitch(twitch_irc.Client):
	def __init__(self, BASE:"Phaazebot"):
		super().__init__()
		self.BASE:"Phaazebot" = BASE

	def __bool__(self):
		return self.BASE.IsReady.twitch

	async def onReady(self) -> None:
		"""
		Called when Phaaze is first connected, or sometimes when reconnected
		"""

	async def onMessage(self, Message:twitch_irc.Message) -> None:
		"""
		Called everytime a message is new message is received
		"""

		if not self.BASE.IsReady.twitch: return
		if Message.Author.name == self.nickname: return

	# errors
	async def onError(self, Ex:Exception):
		"""
		Default error funtion, called everytime someting went wrong
		"""
		tb = traceback.format_exc()
		self.BASE.Logger.error(f'(Twitch) Ignoring exception {Ex}\n{tb}')

	# debug
	async def debugCall(self, Message:twitch_irc.Message):
		"""
		string evaluation on user input,
		only for the user assosiated with self.BASE.Vars.twitch_debug_user_id
		starting a message with ### or !!! will execute everything after this
		### is a normal call
		!!! a corotine
		"""
		pass

PhaazebotTwitch().onerr
