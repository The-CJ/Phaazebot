from typing import TYPE_CHECKING, Tuple
if TYPE_CHECKING:
	from Platforms.Discord.main_discord import PhaazebotDiscord

import re
import discord
from tabulate import tabulate
from Utils.Classes.discordcommand import DiscordCommand
from Utils.Classes.discordcommandcontext import DiscordCommandContext
from Utils.stringutils import prettifyNumbers
from Utils.regex import Osu as ReOsu
from Platforms.Osu.api import getOsuUser
from Utils.Classes.osuuser import OsuUser

async def osuStats(cls:"PhaazebotDiscord", _Command:DiscordCommand, CommandContext:DiscordCommandContext) -> dict:

	search_mode:str = "0"
	if "--taiko" in CommandContext.parts:
		CommandContext.parts.remove("--taiko")
		search_mode = "1"
	elif "--ctb" in CommandContext.parts:
		CommandContext.parts.remove("--ctb")
		search_mode = "2"
	elif "--mania" in CommandContext.parts:
		CommandContext.parts.remove("--mania")
		search_mode = "3"

	content:str = " ".join(CommandContext.parts[1:])

	if not content:
		return {"content": ":warning: Please specify a query string to search a user"}

	search_by, is_id = extractUserInfo(content)
	User:OsuUser = await getOsuUser(cls.BASE, search=search_by, mode=search_mode, is_id=is_id)

	if not User:
		return {"content": ":warning: The given User could not found!"}

	emb_description:str = f":globe_with_meridians: #{prettifyNumbers(User.pp_rank, 0)}  |  :flag_{User.country.lower()}: #{prettifyNumbers(User.pp_country_rank, 0)}\n"
	emb_description += f":part_alternation_mark: {prettifyNumbers(User.pp_raw, 2)} pp\n"
	emb_description += f":dart: {prettifyNumbers(User.accuracy, 2)}% Accuracy\n"
	emb_description += f":military_medal: Level: {prettifyNumbers(User.level, 2)}\n"
	emb_description += f":timer: Playcount: {prettifyNumbers(User.playcount, 0)}\n"
	emb_description += f":chart_with_upwards_trend: Ranked Score: {prettifyNumbers(User.ranked_score, 0)}\n"
	emb_description += f":card_box: Total Score: {prettifyNumbers(User.total_score, 0)}\n"
	emb_description += f":id: {User.user_id}"

	Emb:discord.Embed = discord.Embed(
		title=User.username,
		color=0xFF69B4,
		description=emb_description,
		url=f"https://osu.ppy.sh/users/{User.user_id}"
	)

	rank_table:list = [
		["A", prettifyNumbers(User.count_rank_a)],
		["S", prettifyNumbers(User.count_rank_s)],
		["SX", prettifyNumbers(User.count_rank_sh)],
		["SS", prettifyNumbers(User.count_rank_ss)],
		["SSX", prettifyNumbers(User.count_rank_ssh)]
	]

	Emb.add_field(name="Ranks:", value=f"```{tabulate(rank_table, tablefmt='plain')}```")

	Emb.set_thumbnail(url=f"https://a.ppy.sh/{User.user_id}")
	Emb.set_footer(text="Provided by osu!", icon_url=cls.BASE.Vars.logo_osu)
	Emb.set_author(name=f"Stats for: {User.mode}")

	return {"embed": Emb}

def extractUserInfo(search_str:str) -> Tuple[str, bool]:
	Hit:re.Match = re.match(ReOsu.Userlink, search_str)
	if Hit: # it is a link, with a id
		return Hit.group("id"), True

	if search_str.isdigit():
		return search_str, True

	return search_str, False
