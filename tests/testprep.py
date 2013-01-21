"""
Import log from here in all test modules
"""

import logging, os
from tempfile import gettempdir

from humblebee import logger

log = logging.getLogger('humblebee')
log.setLevel(logging.DEBUG)
logger.set_filehandler(os.path.join(gettempdir(), 'hbtestlog.log'))
