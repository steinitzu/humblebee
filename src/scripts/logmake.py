import logging, os

log = logging.getLogger('scriptlog')
hndlr = logging.StreamHandler()
formatter = logging.Formatter('%(levelname)s %(asctime)s %(module)s.%(funcName)s: %(message)s')
hndlr.setFormatter(formatter)
log.addHandler(hndlr)

fhandler = logging.FileHandler(
    os.path.join(os.path.dirname(__file__), 'script.log')
    )
fhandler.setFormatter(formatter)
log.addHandler(fhandler)
