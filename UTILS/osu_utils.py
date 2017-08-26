import asyncio, requests, subprocess, re, os
from UTILS import oppai as oppai


async def download_map(ID):
	link = "https://osu.ppy.sh/osu/" + ID
	h = requests.get(link)
	file = open("UTILS/OSU_MAPS/"+ID+".osu", "wb")
	file.write(bytes(h.text, "UTF-8"))
	file.close()
	return "UTILS/OSU_MAPS/"+ID+".osu"

async def get_pp(ID, c100=0, c50=0, misses=0, sv=1, acc=100.0, combo=0, mod_s=""):
	path = await download_map(ID)

	e = oppai.calc(path, c100=c100, c50=c50, misses=misses, sv=sv, acc=acc, combo=combo, mod_s=mod_s)
	os.remove("UTILS/OSU_MAPS/"+ID+".osu")

	return e
