from typing import TYPE_CHECKING, Any
if TYPE_CHECKING:
	from main import Phaazebot

import twitch_irc
import traceback

class PhaazebotTwitch(twitch_irc.Client):
	def __init__(self, BASE:"Phaazebot", *args:list, **kwargs:dict):
		super().__init__(*args, **kwargs)
		self.BASE:"Phaazebot" = BASE

	def __bool__(self):
		return self.BASE.IsReady.twitch

	async def onReady(self) -> None:
		"""
		Called when Phaaze is first connected, or sometimes when reconnected
		"""
		self.BASE.Logger.info("Twitch connected")
		self.BASE.IsReady.twitch = True

		await self.joinChannel(self.nickname)

	async def onMessage(self, Message:twitch_irc.Message) -> None:
		"""
		Called everytime a message is new message is received
		"""

		if not self.BASE.IsReady.twitch: return
		if Message.Author.name == self.nickname: return

		if str(Message.Author.id) in self.BASE.Vars.twitch_debug_user_id:
			await self.debugCall(Message)

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
		# we check again... just to be sure
		if not str(Message.Author.id) in self.BASE.Vars.twitch_debug_user_id:
			return

		corotine:bool = False
		command:str = None

		if Message.content.startswith("###"):
			command = Message.content.replace("###", '', 1)
			corotine = False

		elif Message.content.startswith("!!!"):
			command = Message.content.replace("!!!", '', 1)
			corotine = True
		else:
			return

		try:
			res:Any = eval(command)
			if corotine: res = await res
			return await self.sendMessage(Message.Channel, str(res))

		except Exception as Fail:
			tb = traceback.format_exc()
			re:str = f"Exception: {str(Fail)} : {str(tb)}"
			return await self.sendMessage(Message.Channel, re[:199])
