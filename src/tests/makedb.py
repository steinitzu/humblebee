import os, sqlite3
import logging

#import tvdb_api

import tvunfucker

from tvunfucker import logger
from tvunfucker import chainwrapper, parser, tvdbwrapper
from tvunfucker.texceptions import ShowNotFoundError, EpisodeNotFoundError, SeasonNotFoundError

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
            log.debug('gonna lookup the ep %s', ep)
            webep = None
            webep = tvdbwrapper.lookup(ep)
            #TODO: catch the right exceptions
        except ShowNotFoundError  as e:
            #raise
            log.error(e.message)
            unparsed.append(ep)
        except SeasonNotFoundError as e:
            #raise
            log.error(e.message)
            unparsed.append(ep)
        except EpisodeNotFoundError as e:
            #raise
            log.error(e.message)
            unparsed.append(ep)  
        else:
            log.debug(ep)
            ep['tvdb_ep'] = webep
            source[ep['path']] = ep
            if webep:
                log.debug('adding ep to db %s', ep)
                try:
                    source.add_episode_to_db(ep)
                except sqlite3.IntegrityError:
                    log.error(
                        'episode already exists in db: %s. Ignoring.',
                        ep['path']
                        )
                """
                except sqlite3.OperationalError as e:
                    log.info('db_file: %s', source.
                """
                        
                    
                    

    log.info('\n***UNPARSED EPISODES***\n')
    log.info('count: %d\n' % len(unparsed))
    log.info('\n'.join([e['path'] for e in unparsed])) #TODO: Exception here, expects string


run_this_shit(source)
