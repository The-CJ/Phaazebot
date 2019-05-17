import logging
from Utils import CLI_Args
try: from systemd.journal import JournalHandler
except ImportError:	pass

LOG = logging.getLogger('PhaazeOS')
LOG.setLevel(logging.DEBUG)

class ColoredLogger(logging.Formatter):
	default_color = "\033[00m"
	colors = dict(
		DEBUG = "\033[90m",
		INFO = "\033[36m",
		WARNING = "\033[93m",
		ERROR = "\033[33m",
		CRITICAL = "\033[31m",
	)

	def formatMessage(self, record):
		rln = record.levelname
		record.levelname = f"{ColoredLogger.colors.get(rln, ColoredLogger.default_color)}{rln}{ColoredLogger.default_color}"
		r = self._style.format(record)
		return r

SHF = ColoredLogger("\033[00m[%(levelname)s] %(message)s\033[00m")

if CLI_Args.get('logging', 'console') == "systemd" and 'systemd' in sys.modules:
	JH = JournalHandler()
	JH.setFormatter(SHF)
	LOG.addHandler(JH)
else:
	SH = logging.StreamHandler()
	SH.setFormatter(SHF)
	LOG.addHandler(SH)

active_debugs = [a.lower() for a in CLI_Args.get("debug", "").split(",")]

# ["web", "api:fail"]
# web:error
# api
# api:success

def DEBUG(message, require="all"):
	show = False
	for ad in active_debugs:
		if ad == "all": show = True; break
		if require == ad: show = True; break
		if require.split(":")[0] == ad: show = True; break

	if show: LOG.debug(message)

def INFO(m):
	LOG.info(m)

def WARNING(m):
	LOG.warning(m)

def ERROR(m):
	LOG.error(m)

def CRITICAL(m):
	LOG.critical(m)
