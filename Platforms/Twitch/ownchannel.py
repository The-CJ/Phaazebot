from typing import TYPE_CHECKING, List
if TYPE_CHECKING:
	from Platforms.Twitch.main_twitch import PhaazebotTwitch

import twitch_irc
import Platforms.Twitch.const as TwitchConst
from Utils.Classes.twitchcommandcontext import TwitchCommandContext
from Utils.Classes.twitchpermission import TwitchPermission

async def clientNameChannel(cls:"PhaazebotTwitch", Message:twitch_irc.Message) -> None:

	Context:TwitchCommandContext = TwitchCommandContext(cls, Message)
	cmd_str = str(Context.part(0)).lower()

	if cmd_str.startswith("!join"):
		return joinUserChannel(cls, Message, Context)

	if cmd_str.startswith("!leave"):
		return leaveUserChannel(cls, Message, Context)
async def leaveUserChannel(cls:"PhaazebotTwitch", Message:twitch_irc.Message, Context:TwitchCommandContext) -> None:

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

		res:List[dict] = cls.BASE.PhaazeDB.selectQuery(alternative_sql, alternative_target)

	else:
		check_sql:str = """
			SELECT `twitch_channel`.`channel_id` AS `channel_id`
			FROM `twitch_channel`
			WHERE `twitch_channel`.`managed` = 1
				AND `twitch_channel`.`channel_id` = %s"""

		res:List[dict] = cls.BASE.PhaazeDB.selectQuery(check_sql, Message.user_id)

	if not res:
		return_content:str = f"@{Message.display_name} > Phaaze can't leave your channel, if i never was in it LUL"
		if alternative_target: return_content = f"@{Message.display_name} > Not possible, your query did not yield a managed channel to leave"
		return await Message.Channel.sendMessage(cls, return_content)

	# at this point we do have a managed channel in twitch_channel table, so we update it
	execute_id:str = res[0]["channel_id"]
	cls.BASE.PhaazeDB.updateQuery(
		"twitch_channel",
		{"managed": 0},
		"`twitch_channel`.`channel_id` = %s",
		(execute_id,)
	)

	return_content:str = f"@{Message.display_name} > Phaaze successful left your channel :c"
	if alternative_target: return_content = f"@{Message.display_name} > Phaaze successful left {alternative_target}'s channel"
	return await Message.Channel.sendMessage(cls, return_content)
