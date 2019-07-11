import re

# contains all pre compiled regex that maybe needed

IsLink:"re.Pattern" = re.compile(r"^(?P<method>https?://)?(?P<domain>\S+\.\S+)(?P<address>\/?\.?(\S+)?)*$")
ContainsLink:"re.Pattern" = re.compile(r"(?P<method>https?://)?(?P<domain>\S+\.\S+)(?P<address>\/?\.?(\S+)?)*")

IsEmail:"re.Pattern" = re.compile(r"^(?P<account>[a-zA-Z0-9_.+-])+@(?P<provider>[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)$")
ContainsEmail:"re.Pattern" = re.compile(r"(?P<account>[a-zA-Z0-9_.+-])+@(?P<provider>[a-zA-Z0-9-]+\.[a-zA-Z0-9-.])+")

class Discord(object):
	CommandFunctionString:"re.Pattern" = re.compile(r"\<\{(?P<function>.+)\}\>")
	CommandVariableString:"re.Pattern" = re.compile(r"\[(?P<name>.+)\]")

class Osu(object):
	Maplink:"re.Pattern" = re.compile(r"(?P<method>https?://)?osu\.ppy\.sh/(?P<way>b|beatmapsets)/(?P<id1>\d+)(?P<mode>#\w+)?(/(?P<id2>\d+))?")
	Userlink:"re.Pattern" = re.compile(r"(?P<method>https?://)?osu\.ppy\.sh/(?P<way>u|users)/(?P<id>\d+)")
