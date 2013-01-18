#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from decimal import Decimal
from time import time

from . import appconfig as cfg
from . import __pkgname__

log = logging.getLogger(__pkgname__)

streamformatter = logging.Formatter(
    '%(levelname)s: %(message)s'
    )
fileformatter = logging.Formatter(
    '%(levelname)s %(asctime)s %(module)s.%(funcName)s: %(message)s'
    )
streamhandler =  logging.StreamHandler()
streamhandler.setFormatter(streamformatter)
filehandler = logging.FileHandler(cfg.get('logging', 'filename'), mode='a') #has a default
filehandler.setFormatter(fileformatter)

log.addHandler(filehandler)
log.addHandler(streamhandler)

level = cfg.get('logging', 'level')
log.setLevel(logging.__getattribute__(level.upper()))

def set_filehandler(filename):
    """
    remove existing `filehandler` and set a new one.
    `global filehandler` will become the new handler.
    """
    fh = logging.FileHandler(filename)
    fh.setFormatter(fileformatter)
    global filehandler
    log.removeHandler(filehandler)
    filehandler = fh
    log.addHandler(fh)




####################################


#decorator
def log_time(func):
    def caller(*args, **kwargs):
        starttime = Decimal(time())
        ret = func(*args, **kwargs)
        log.debug(
            '%s finished in %s seconds.' % (
            func.__name__, Decimal(time())-starttime)
            )
        return ret
    return caller
