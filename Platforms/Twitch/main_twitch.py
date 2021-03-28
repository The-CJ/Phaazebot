from typing import TYPE_CHECKING, Any
if TYPE_CHECKING:
	from phaazebot import Phaazebot

import twitch_irc
import asyncio
import traceback
from Platforms.Twitch.openchannel import openChannel
from Utils.cli import CliArgs

class PhaazebotTwitch(twitch_irc.Client):
	def __init__(self, BASE:"Phaazebot", *args, **kwargs):
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
		await self.joinAllChannels()

	async def onMessage(self, Message:twitch_irc.Message) -> None:
		"""
		Called everytime a message is new message is received
		"""

		if not self.BASE.IsReady.twitch: return
		if Message.Author.name == self.nickname: return

		if str(Message.Author.id) in self.BASE.Vars.twitch_debug_user_id:
			await self.debugCall(Message)

		return await openChannel(self, Message)

	async def onError(self, Ex:Exception):
		"""
		Default error function, called everytime something went wrong
		"""
		tb = traceback.format_exc()
		self.BASE.Logger.error(f'(Twitch) Ignoring exception {Ex}\n{tb}')

	async def joinAllChannels(self) -> None:
		"""
		Join all channels we know in the database that have a managed=true
		"""

		if CliArgs.get("no-twitch-join", ""):
			return self.BASE.Logger.warning(f"`no-twitch-join` active, skipping channel join.")

		twitch_res:list = self.BASE.PhaazeDB.selectQuery("""
			SELECT
				`twitch_channel`.`channel_id` AS `channel_id`,
				`twitch_user_name`.`user_name` AS `channel_name`
			FROM `twitch_channel`
			LEFT JOIN `twitch_user_name`
				ON `twitch_user_name`.`user_id` = `twitch_channel`.`channel_id`
			WHERE `twitch_channel`.`managed` = 1""")

		if not twitch_res: return
		self.BASE.Logger.info(f"Twitch Joining {len(twitch_res)} channels...")

		# we could just spam all JOIN commands in one go, the twitch_irc lib would handle all ratelimit's
		# but we don't

		for entry in twitch_res:
			channel_name:str = entry.get("channel_name", None)
			if not channel_name: continue
			self.BASE.Logger.debug(f"Joining twitch channel: {channel_name}", require="twitch:join")
			await self.joinChannel(channel_name)
			await asyncio.sleep(19/30) # save request limit

		self.BASE.Logger.info(f"Twitch joined all {len(twitch_res)} channels!")

	# debug
	async def debugCall(self, Message:twitch_irc.Message):
		"""
		string evaluation on user input,
		only for the user associated with self.BASE.Vars.twitch_debug_user_id
		starting a message with ### or !!! will execute everything after this
		### is a normal call
		!!! a coroutine
		"""
		# we check again... just to be sure
		if not str(Message.Author.id) in self.BASE.Vars.twitch_debug_user_id:
			return

		coroutine:bool
		command:str

		if Message.content.startswith("###"):
			command = Message.content.replace("###", '', 1)
			coroutine = False

		elif Message.content.startswith("!!!"):
			command = Message.content.replace("!!!", '', 1)
			coroutine = True
		else:
			return

		try:
			res:Any = eval(command)
			if coroutine: res = await res
			return await self.sendMessage(Message.Channel, str(res))

		except Exception as Fail:
			tb = str(traceback.format_exc()).replace("\n",' ').replace("\r", '')
			re:str = f"Exception: {str(Fail)} : {tb}"
			return await self.sendMessage(Message.Channel, re[:499])

	async def onUnknown(self, raw:str) -> None:
		self.BASE.Logger.error(f"Twitch IRC Unknown Data: {raw}")
