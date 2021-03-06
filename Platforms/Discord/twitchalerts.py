from typing import TYPE_CHECKING, List, Optional
if TYPE_CHECKING:
	from Platforms.Discord.main_discord import PhaazebotDiscord
	from Platforms.Twitch.main_events import StatusEntry

import discord

TWITCH_COLOR:int = 0x6441A4
TWITCH_STREAM_URL:str = "https://twitch.tv/"

async def discordHandleLive(cls:"PhaazebotDiscord", event_list:List["StatusEntry"]) -> None:
	"""
	With a list status entry's from twitch,
	we format and send all live announcements to all discord channels
	"""

	if not cls: return # Discord Client not ready or off

	event_channel_list:str = ",".join(str(Event.channel_id) for Event in event_list)
	if not event_channel_list: event_channel_list = "0"

	res:List[dict] = cls.BASE.PhaazeDB.selectQuery(f"""
		SELECT
			`discord_twitch_alert`.`twitch_channel_id`,
			`discord_twitch_alert`.`discord_channel_id`,
			`discord_twitch_alert`.`custom_msg`
		FROM `discord_twitch_alert`
		WHERE `discord_twitch_alert`.`twitch_channel_id` IN ({event_channel_list})"""
	)

	for db_entry in res:

		Event:"StatusEntry" = getStreamFromDBResult(event_list, db_entry["twitch_channel_id"])
		if Event is None: continue # should never happen

		# we only care about live alerts,
		# there should be no other types, but we go save here
		if Event.Stream.stream_type != "live": continue

		# try to catch invalid twitch api results
		if not Event.User:
			cls.BASE.Logger.warning(f"Can't find Twitch User ID:{Event.channel_id}")
			continue

		if not Event.Game:
			cls.BASE.Logger.warning(f"Can't find Twitch Game ID:{Event.game_id}")
			continue

		stream_status:str = Event.Stream.title or "[N/A]"
		stream_url:str = TWITCH_STREAM_URL + (Event.User.login or "")
		stream_description:str = f":game_die: Playing: **{Event.Game.name}**"

		Emb:discord.Embed = discord.Embed(
			title=stream_status,
			url=stream_url,
			description=stream_description,
			color=TWITCH_COLOR
		)
		Emb.set_author(
			name=Event.User.display_name,
			url=stream_url,
			icon_url=Event.User.profile_image_url
		)
		Emb.set_footer(
			text="Provided by twitch.tv",
			icon_url=cls.BASE.Vars.logo_twitch
		)
		Emb.set_image(url=Event.User.profile_image_url)

		discord_chan_id:str = db_entry.get("discord_channel_id", "-1")
		discord_custom_msg:str = db_entry.get("custom_msg", None) or None

		try:
			Chan:discord.TextChannel = cls.get_channel(int(discord_chan_id))
			if not Chan: continue

			await Chan.send(content=discord_custom_msg, embed=Emb)

		except:
			cls.BASE.Logger.warning(f"Can't send Twitch Alert to Discord Channel ID: {discord_chan_id}")

async def discordHandleGameChange(cls:"PhaazebotDiscord", event_list:List["StatusEntry"]) -> None:
	"""
	With a list status entry's from twitch,
	we format and send all gamechange announcements to all discord channels
	"""

	if not cls: return # Discord Client not ready or off

	event_channel_list:str = ",".join(Event.channel_id for Event in event_list)
	if not event_channel_list: event_channel_list = "0"

	res:List[dict] = cls.BASE.PhaazeDB.selectQuery(f"""
		SELECT
			`discord_twitch_alert`.`twitch_channel_id`,
			`discord_twitch_alert`.`discord_channel_id`,
			`discord_twitch_alert`.`suppress_gamechange`
		FROM `discord_twitch_alert`
		WHERE `discord_twitch_alert`.`twitch_channel_id` IN ({event_channel_list})"""
	)

	for db_entry in res:

		Event:"StatusEntry" = getStreamFromDBResult(event_list, db_entry["twitch_channel_id"])
		if Event is None: continue # should never happen

		# ignore gamechange events for alert
		if db_entry.get("suppress_gamechange", 0): continue

		# we only care about live alerts,
		# there should be no other types, but we go save here
		if Event.Stream.stream_type != "live": continue

		# try to catch invalid twitch api results
		if not Event.User:
			cls.BASE.Logger.warning(f"Can't find Twitch User ID:{Event.channel_id}")
			continue

		if not Event.Game:
			cls.BASE.Logger.warning(f"Can't find Twitch Game ID:{Event.game_id}")
			continue

		stream_status:str = Event.Stream.title or "[N/A]"
		stream_url:str = TWITCH_STREAM_URL + (Event.User.login or "")
		stream_description:str = f":game_die: Now Playing: **{Event.Game.name}**"

		Emb:discord.Embed = discord.Embed(
			title=stream_status,
			url=stream_url,
			description=stream_description,
			color=TWITCH_COLOR
		)
		Emb.set_author(
			name=Event.User.display_name,
			url=stream_url,
			icon_url=Event.User.profile_image_url
		)
		Emb.set_footer(
			text="Provided by twitch.tv",
			icon_url=cls.BASE.Vars.logo_twitch
		)
		Emb.set_thumbnail(url=Event.User.profile_image_url)

		discord_chan_id:str = db_entry.get("discord_channel_id", "-1")

		try:
			Chan:discord.TextChannel = cls.get_channel(int(discord_chan_id))
			if not Chan: continue

			await Chan.send(embed=Emb)

		except:
			cls.BASE.Logger.warning(f"Can't send Twitch Alert to Discord Channel ID: {discord_chan_id}")

async def discordHandleOffline(_cls:"PhaazebotDiscord", _status_list:list) -> None:
	return # for now do nothing

def getStreamFromDBResult(events:List["StatusEntry"], channel_id:str) -> Optional["StatusEntry"]:
	for Ev in events:
		if str(Ev.channel_id) == str(channel_id): return Ev
	return None
