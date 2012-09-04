import os
import logging

import tvdb_api

import tvunfucker

from tvunfucker import logger
from tvunfucker import chainwrapper, parser

log = logging.getLogger('tvunfucker')

source_dir = os.path.join(os.path.dirname(__file__), 'testdata/testfs')
source = chainwrapper.EpisodeSource(source_dir)

db_file = os.path.join(source_dir, '.tvunfucker.sqlite')
os.unlink(db_file)

source = chainwrapper.EpisodeSource(os.path.dirname(db_file))
source.initialize_database()


def run_this_shit(source):
    unparsed = []
    for ep in chainwrapper.get_parsed_episodes(source.source_dir):
        webep = None
        #print ep['path']
        try:
            log.debug('gonna lookup the ep')
            webep = chainwrapper.tvdb_lookup(ep)
        except tvdb_api.tvdb_shownotfound as e:
            raise
            log.error(e.message)
            unparsed.append(ep)
        except tvdb_api.tvdb_seasonnotfound as e:
            raise
            log.error(e.message)
            unparsed.append(ep)
        except tvdb_api.tvdb_episodenotfound as e:
            raise
            log.error(e.message)
            unparsed.append(ep)  
        else:
            log.debug(ep)
            ep['tvdb_ep'] = webep
            source[ep['path']] = ep
            if webep:
                source.add_episode_to_db(ep)

    log.info('\n***UNPARSED EPISODES***\n')
    log.info('count: %d\n' % len(unparsed))
    log.info('\n'.join([e for e in unparsed])) #TODO: Exception here, expects string


run_this_shit(source)
