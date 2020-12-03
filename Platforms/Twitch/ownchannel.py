from typing import TYPE_CHECKING, List
if TYPE_CHECKING:
	from Platforms.Twitch.main_twitch import PhaazebotTwitch

import twitch_irc
import Platforms.Twitch.const as TwitchConst
from Platforms.Twitch.api import getTwitchUsers
from Utils.Classes.twitchcommandcontext import TwitchCommandContext
from Utils.Classes.twitchpermission import TwitchPermission
from Utils.Classes.twitchuser import TwitchUser

async def clientNameChannel(cls:"PhaazebotTwitch", Message:twitch_irc.Message) -> None:
	"""
	special handling for messages in the bot's own twitch channel
	"""

	Context:TwitchCommandContext = TwitchCommandContext(cls, Message)
	cmd_str = str(Context.part(0)).lower()

	if cmd_str.startswith("!join"):
		return await joinUserChannel(cls, Message, Context)

	if cmd_str.startswith("!leave"):
		return await leaveUserChannel(cls, Message, Context)

async def joinUserChannel(cls:"PhaazebotTwitch", Message:twitch_irc.Message, Context:TwitchCommandContext) -> None:
	"""
	allowed user and admin to like phaaze to a channel
	"""
	alternative_target:str = ""

	UserPerm:TwitchPermission = TwitchPermission(Message, None)
	if UserPerm.rank >= TwitchConst.REQUIRE_ADMIN:
		# admin or higher have the permission to remove phaaze from any channel without the owner consent
		if len(Context.parts) >= 2:
			alternative_target = Context.part(1)

	if alternative_target:
		alternative_sql:str = """
			SELECT COUNT(*) AS `I`
			FROM `twitch_user_name`
			LEFT JOIN `twitch_channel`
				ON `twitch_channel`.`channel_id` = `twitch_user_name`.`user_id`
			WHERE `twitch_channel`.`managed` = 1
				AND `twitch_user_name`.`user_name` = %s"""

		res:List[dict] = cls.BASE.PhaazeDB.selectQuery(alternative_sql, (alternative_target,))

	else:
		check_sql:str = """
			SELECT COUNT(*) AS `I`
			FROM `twitch_channel`
			WHERE `twitch_channel`.`managed` = 1
				AND `twitch_channel`.`channel_id` = %s"""

		res:List[dict] = cls.BASE.PhaazeDB.selectQuery(check_sql, (Message.user_id,))

	if res[0]['I']:
		return_content:str = f"@{Message.display_name} > Phaaze already is in your channel"
		if alternative_target: return_content = f"@{Message.display_name} > Phaaze already is in {alternative_target}'s channel"
		return await Message.Channel.sendMessage(cls, return_content)

	# after this point, we have a user or a admin input how want to add phaaze
	if alternative_target:
		user_search:List[TwitchUser] = await getTwitchUsers(cls, alternative_target, item_type="login", limit=1)
		if not user_search:
			return_content:str = f"@{Message.display_name} > Phaaze could not find a user named {alternative_target} in the Twitch-API"
			return await Message.Channel.sendMessage(cls, return_content)
		else:
			NewEntry:TwitchUser = user_search.pop(0)

			# insert ot update managed status
			cls.BASE.PhaazeDB.insertQuery(
				update_on_duplicate = True,
				table = "twitch_channel",
				content = {
					"channel_id": NewEntry.user_id,
					"managed": 1
				},
			)

			# insert ot update to name table
			cls.BASE.PhaazeDB.insertQuery(
				update_on_duplicate = True,
				table = "twitch_user_name",
				content = {
					"user_id": NewEntry.user_id,
					"user_name": NewEntry.name,
					"user_display_name": NewEntry.display_name
				},
			)

	else:
		# insert ot update managed status
		cls.BASE.PhaazeDB.insertQuery(
			update_on_duplicate = True,
			table = "twitch_channel",
			content = {
				"channel_id": Message.user_id,
				"managed": 1
			},
		)

		# insert ot update to name table
		cls.BASE.PhaazeDB.insertQuery(
			update_on_duplicate = True,
			table = "twitch_user_name",
			content = {
				"user_id": Message.user_id,
				"user_name": Message.user_name,
				"user_display_name": Message.display_name
			},
		)

	if alternative_target:
		await cls.joinChannel(alternative_target)
		return_content:str = f"@{Message.display_name} > Phaaze successful joined {alternative_target}'s channel"
	else:
		await cls.joinChannel(Message.user_name)
		return_content:str = f"@{Message.display_name} > Phaaze successful joined your channel"

	return await Message.Channel.sendMessage(cls, return_content)

async def leaveUserChannel(cls:"PhaazebotTwitch", Message:twitch_irc.Message, Context:TwitchCommandContext) -> None:
	"""
	allowed each user to bring phaaze to leave there channel, also allowed global mods+ to remive phaaze as well
	"""

	alternative_target:str = ""

	UserPerm:TwitchPermission = TwitchPermission(Message, None)
	if UserPerm.rank >= TwitchConst.REQUIRE_ADMIN:
		# admin or higher have the permission to remove phaaze from any channel without the owner consent
		if len(Context.parts) >= 2:
			alternative_target = Context.part(1)

	if alternative_target:
		alternative_sql:str = """
			SELECT `twitch_channel`.`channel_id` AS `channel_id`
			FROM `twitch_user_name`
			LEFT JOIN `twitch_channel`
				ON `twitch_channel`.`channel_id` = `twitch_user_name`.`user_id`
			WHERE `twitch_channel`.`managed` = 1
				AND `twitch_user_name`.`user_name` = %s"""

		res:List[dict] = cls.BASE.PhaazeDB.selectQuery(alternative_sql, (alternative_target,))

	else:
		check_sql:str = """
			SELECT `twitch_channel`.`channel_id` AS `channel_id`
			FROM `twitch_channel`
			WHERE `twitch_channel`.`managed` = 1
				AND `twitch_channel`.`channel_id` = %s"""

		res:List[dict] = cls.BASE.PhaazeDB.selectQuery(check_sql, (Message.user_id,))

	if not res:
		return_content:str = f"@{Message.display_name} > Phaaze can't leave your channel, if i currently aren't in it LUL"
		if alternative_target: return_content = f"@{Message.display_name} > Not possible, your query did not yield a managed channel to leave"
		return await Message.Channel.sendMessage(cls, return_content)

	# at this point we do have a managed channel in twitch_channel table, so we update it
	execute_id:str = res[0]["channel_id"]
	cls.BASE.PhaazeDB.updateQuery(
		table = "twitch_channel",
		content = {"managed": 0},
		where = "`twitch_channel`.`channel_id` = %s",
		where_values = (execute_id,)
	)

	if alternative_target:
		await cls.partChannel(alternative_target)
		return_content:str = f"@{Message.display_name} > Phaaze successful left {alternative_target}'s channel"
	else:
		await cls.partChannel(Message.user_name)
		return_content:str = f"@{Message.display_name} > Phaaze successful left your channel :c"

	return await Message.Channel.sendMessage(cls, return_content)
