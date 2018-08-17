import logging, sys, re
from systemd.journal import JournalHandler

option_re = re.compile(r'^--(.+?)=(.*)$')
all_args = dict()
for arg in sys.argv[1:]:
	d = option_re.match(arg)
	if d != None:
		all_args[d.group(1)] = d.group(2)

LOG = logging.getLogger('PhaazeOS')
LOG.setLevel(logging.DEBUG)

SHF = logging.Formatter("[%(levelname)s] %(message)s")

if all_args.get('logging', 'console') == "systemd":
	JH = JournalHandler()
	JH.setFormatter(SHF)
	LOG.addHandler(JH)
else:
	SH = logging.StreamHandler()
	SH.setFormatter(SHF)
	LOG.addHandler(SH)

def DEBUG(m):
	LOG.debug(m)

def INFO(m):
	LOG.info(m)

def WARNING(m):
	LOG.warning(m)

def ERROR(m):
	LOG.error(m)

def CRITICAL(m):
	LOG.critical(m)
