import os, sqlite3
import logging

#import tvdb_api

import tvunfucker

from tvunfucker import logger
from tvunfucker import chainwrapper, parser, tvdbwrapper
from tvunfucker.texceptions import ShowNotFoundError, EpisodeNotFoundError, SeasonNotFoundError



log = logging.getLogger('tvunfucker')
log.setLevel(logging.DEBUG)

source_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'testdata/testfs'))
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
            log.info('looking up file at %s', ep['path'])
            webep = None
            webep = tvdbwrapper.lookup(ep)
            #TODO: catch the right exceptions
        except (ShowNotFoundError, SeasonNotFoundError, EpisodeNotFoundError) as e:
            #raise
            log.error(e.message)
            log.debug('unparsed episode')
            ep['path'] = os.path.relpath(ep['path'], source_dir)
            source.add_unparsed_child(ep['path'])
            unparsed.append(ep)
        else:
            log.debug(ep)
            ep['tvdb_ep'] = webep
            #TODO: ugly hack, tackle this when eps are spawned
            ep['path'] = os.path.relpath(ep['path'], source_dir)
            source[ep['path']] = ep
            log.info('Adding episode at: %s', ep['path'])
            if webep:
                log.debug('adding ep to db %s', ep)
                try:
                    source.add_episode_to_db(ep)
                except sqlite3.IntegrityError:
                    log.error(
                        'episode already exists in db: %s. Ignoring.',
                        ep['path']
                        )

    log.info('\n***UNPARSED EPISODES***\n')
    log.info('count: %d\n' % len(unparsed))
    log.info('\n'.join([e['path'] for e in unparsed])) #TODO: Exception here, expects string


run_this_shit(source)
