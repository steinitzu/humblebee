import tvunfucker
from tvunfucker import tvdbwrapper, logger

import logging
from tvunfucker.texceptions import *

log = logging.getLogger('tvunfucker')

cor_sers = (
    'House M.D.',
    'House', 'friends', 'the daily', 'The king of queens', 'Scrubs', 'Lost')

for s in cor_sers:
    try:
        log.info(tvdbwrapper.get_series(s))
    except ShowNotFoundError as e:
        log.error(e)

#TODO: write this test
tvdbwrapper.lookup(lol)
