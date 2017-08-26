#BASE.moduls.Cleverbot_main

from __future__ import (absolute_import, division, print_function,
						unicode_literals)
from builtins import str
from builtins import object

import collections
import hashlib
import requests
from requests.compat import urlencode
from future.backports.html import parser

entity_parser = parser.HTMLParser()

class ai_clever(object):

	banned = []

class Phaaze_Clever:

	def __init__(self, api_key, name="CleverPhaaze"):
		self.url = "https://www.cleverbot.com/getreply"
		self.name = name
		self.key = api_key
		self.history = {}
		self.convo_id = ""
		self.cs = ""
		self.count = 0
		self.time_elapsed = 0
		self.time_taken = 0
		self.output = ""

	def ask(self, text):
		params = {
			"input": text,
			"key": self.key,
			"cs": self.cs,
			"conversation_id": self.convo_id,
			"wrapper": "PhaazeOS_cleverbot.py"
				}

		try:
			reply = self._send(params)
			self._process_reply(reply)
			return self.output

		except:
			self.cs = ""
			self.convo_id = ""
			self.history = {}
			return ":warning: Cleverbot talking nonsense right now, please try later again."


	def _send(self, params):
		try:
			r = requests.get(self.url, params=params)
		except requests.exceptions.RequestException as e:
			print(e)
		return r.json()


	def _process_reply(self, reply):
		self.cs = reply.get("cs", None)
		self.count = int(reply.get("interaction_count", None))
		self.output = reply.get("output", None)
		self.convo_id = reply.get("conversation_id", None)
		self.history = {key:value for key, value in reply.items() if key.startswith("interaction")}
		self.time_taken = int(reply.get("time_taken", None))
		self.time_elapsed = int(reply.get("time_elapsed", None))

async def discord(BASE, message):
	m = message.content.split(" ")
	if len(m) == 1:
		return
	else:
		_question = " ".join(f for f in m[1:])

	if await BASE.moduls.Utils.settings_check(BASE, message, "enable_ai"):

		key = BASE.access.Cleverbot_Token

		#check if there, if not, make new
		if not hasattr(ai_clever, "clever_"+message.server.id): setattr(ai_clever, "clever_"+message.server.id, Phaaze_Clever(key))
		conversation_class = getattr(ai_clever, "clever_"+message.server.id)

		awnser = conversation_class.ask(_question)

		return await BASE.phaaze.send_message(message.channel, " {0}".format(awnser))
