from tvunfucker import cfg
from tvunfucker.bingapi.bingapi import Bing
from tvunfucker import logger

import logging

log = logging.getLogger('tvunfucker')

log.setLevel(logging.DEBUG)

b = Bing(cfg.get('bing', 'api-key'))

res = b.search('site:imdb.com shitcakefart')

log.debug(res)

