#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging, os

from . import logger
from . import cfg

log = logging.getLogger('tvunfucker')
log.setLevel(logging.DEBUG)

tvdb_key = '29E8EC8DF23A5918'

__pkgname__ = 'tvunfucker'

_globconffile = os.path.join(os.path.dirname(__file__), 'default.cfg')

appconfig = cfg.ThreeTierConfigParser(
    __pkgname__, 
    global_config_path=_globconffile
    )
