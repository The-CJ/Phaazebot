import logging

LOG = logging.getLogger('PhaazeOS')
LOG.setLevel(logging.DEBUG)
SH = logging.StreamHandler()
SHF = logging.Formatter("[%(levelname)s] %(message)s")
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
