from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from .main_discord import PhaazebotDiscord
	from Platforms.Twitch.main_events import StatusEntry

import discord
from Utils.Classes.twitchstream import TwitchStream
from Utils.Classes.twitchgame import TwitchGame
from Utils.Classes.twitchuser import TwitchUser
# from Utils.Classes.discordserversettings import DiscordServerSettings

async def discordHandleLive(cls:"PhaazebotDiscord", event_list:list) -> None:
	"""
		With a list status entrys from twitch, we format and send all live announcements to all discord channels
	"""

	if not cls: return #Discord Client not ready or off

	Event:StatusEntry
	event_channel_list:str = ",".join(Event.channel_id for Event in event_list)

	res:list = cls.BASE.PhaazeDB.selectQuery(f"""
		SELECT
			`twitch_channel_id`,
			`discord_channel_id`,
			`custom_msg`
		FROM `discord_twitch_alert`
		WHERE `discord_twitch_alert`.`twitch_channel_id` IN ({event_channel_list})"""
	)

	for db_entry in res:

		Event = getStreamFromDBResult(event_list, db_entry["twitch_channel_id"])
		if not Event: continue # should never happen

		# we only care about live alerts,
		# there should be no other types, but we go save here
		if Event.Stream.stream_type != "live": continue

async def discordHandleGameChange(cls:"PhaazebotDiscord", status_list:list) -> None:
	print(status_list)

async def discordHandleOffline(cls:"PhaazebotDiscord", status_list:list) -> None:
	print(status_list)

def getStreamFromDBResult(events, channel_id) -> "StatusEntry":
	Ev:StatusEntry
	for Ev in events:
		if str(Ev.channel_id) == str(channel_id): return Ev
	return None
