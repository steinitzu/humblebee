import logging

log = logging.getLogger('scriptlog')
hndlr = logging.StreamHandler()
formatter = logging.Formatter('%(levelname)s %(asctime)s %(module)s.%(funcName)s: %(message)s')
hndlr.setFormatter(formatter)
log.addHandler(hndlr)
