# contains all pre compiled regex that may be needed, is NOT included in BASE

import re

is_link = re.compile(r"^(?P<method>https?://)?(?P<domain>\S+\.\S+)(?P<address>\/?\.?(\S+)?)*$")
contains_link = re.compile(r"(?P<method>https?://)?(?P<domain>\S+\.\S+)(?P<address>\/?\.?(\S+)?)*")

is_email = re.compile(r"^(?P<account>[a-zA-Z0-9_.+-])+@(?P<provider>[a-zA-Z0-9-]+\.[a-zA-Z0-9-.])+$")
contains_email = re.compile(r"(?P<account>[a-zA-Z0-9_.+-])+@(?P<provider>[a-zA-Z0-9-]+\.[a-zA-Z0-9-.])+")

class Osu(object):
	maplink = re.compile(r"(?P<method>https?://)?osu\.ppy\.sh/(?P<way>b|beatmapsets)/(?P<id1>\d+)(?P<mode>#\w+)?(/(?P<id2>\d+))?")
	userlink = re.compile(r"(?P<method>https?://)?osu\.ppy\.sh/(?P<way>u|users)/(?P<id>\d+)")

