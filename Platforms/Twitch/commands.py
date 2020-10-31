from typing import TYPE_CHECKING, Awaitable, Dict
if TYPE_CHECKING:
	from Platforms.Twitch.main_twitch import PhaazebotTwitch

import twitch_irc
import asyncio
import Platforms.Twitch.const as TwitchConst
from Utils.Classes.twitchcommand import TwitchCommand
from Utils.Classes.twitchchannelsettings import TwitchChannelSettings
from Utils.Classes.twitchuserstats import TwitchUserStats
from Utils.Classes.twitchpermission import TwitchPermission
from Utils.Classes.twitchcommandcontext import TwitchCommandContext

class GTCCS():
	"""
	you know the point up now, "Global Twitch Command Cooldown Storage" it is
	after command is used, ID is saved in here.
	While its in there, its in a cool down state, and wont be triggered again
	after cooldown is gone, remove ID from here and unlock command
	"""
	def __init__(self):
		self.in_cooldown:Dict[str, bool] = {}

	def check(self, Command:TwitchCommand) -> bool:
		cmd_id:str = str(Command.command_id)
		if self.in_cooldown.get(cmd_id, None): return True
		else: return False

	def cooldown(self, Command:TwitchCommand) -> None:
		asyncio.ensure_future(self.cooldownCoro(Command))

	async def cooldownCoro(self, Command:TwitchCommand) -> None:
		cmd_id:str = str(Command.command_id)
		if self.in_cooldown.get(cmd_id, None): return

		# add
		self.in_cooldown[cmd_id] = True

		# wait
		await asyncio.sleep(Command.cooldown)

		# remove
		self.in_cooldown.pop(cmd_id, None)

GTCCS = GTCCS()
