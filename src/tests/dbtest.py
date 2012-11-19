import logging, os

from tvunfucker import chainwrapper, logger

log = logging.getLogger('tvunfucker')

_src_dir = os.path.join(
    os.path.dirname(__file__),
    'testdata',
    'testfs'
    )

esource = chainwrapper.EpisodeSource(_src_dir)


a = esource.get_series(73141)
log.debug(a)
log.debug('type of a: %s', type(a))
log.debug(a['id'])

seasons = esource.get_seasons(column='series_id', value=73141)

for s in seasons:
    print s



    
