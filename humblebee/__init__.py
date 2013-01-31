#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys, logging, traceback
from random import randint

from . import cfg
from .util import get_prog_home_dir


__pkgname__ = 'humblebee'

_globconffile = os.path.join(os.path.dirname(__file__), 'default.cfg')

appconfig = cfg.ThreeTierConfigParser(
    __pkgname__, 
    global_config_path=_globconffile
    )

quotes = [
    "Omar comin!",
    "I'm afraid I just blue myself.",
    "Screw you guys, I'm goin' home...",
    "I want to be the one person who doesn't die with dignity.",    
    "Shaka, when the walls fell.",
    'Resistance is futile.',
    'You wanna commit suicide? Tie your shoes and have a bite of rissole.',
    ]

def app_excepthook(etype, e, etraceback):
    log = logging.getLogger('humblebee')
    q = quotes[randint(0, len(quotes)-1)]
    log.fatal(q)
    log.fatal(
        ''.join(traceback.format_exception(etype, e, etraceback))
        )
    #raise it normally
    sys.__excepthook__(etype, e, etraceback)

sys.excepthook = app_excepthook    

lf = appconfig.get('logging', 'filename')
if lf is None or lf == 'None':
    appconfig.set(
        'logging', 
        'filename',
        os.path.join(get_prog_home_dir(__pkgname__), __pkgname__+'.log'),
        parser='runtime'
        )

import logger #init the loggers

