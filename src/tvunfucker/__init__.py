#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

from . import cfg
from .util import get_prog_home_dir


__pkgname__ = 'tvunfucker'

_globconffile = os.path.join(os.path.dirname(__file__), 'default.cfg')

appconfig = cfg.ThreeTierConfigParser(
    __pkgname__, 
    global_config_path=_globconffile
    )

lf = appconfig.get('logging', 'filename')
if lf is None or lf == 'None':
    appconfig.set(
        'logging', 
        'filename',
        os.path.join(get_prog_home_dir(__pkgname__), __pkgname__+'.log'),
        parser='runtime'
        )

import logger #init the loggers

