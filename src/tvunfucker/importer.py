import logging, os

from .dbguy import TVDatabase
from .dirscanner import get_episodes
from .parser import ez_parse_episode, reverse_parse_episode
from .texceptions import InitExistingDatabaseError, IncompleteEpisodeError
from .texceptions import ShowNotFoundError, SeasonNotFoundError, EpisodeNotFoundError
from .tvdbwrapper import lookup
from . import appconfig as cfg
from . import __pkgname__

log = logging.getLogger(__pkgname__)

class Importer(object):    

    def __init__(self, directory, **kwargs):
        #TODO: take options from cfg and do update and reset functions
        """
        the kwargs must be the command line options thingies, right..?
        """        
        self.db = TVDatabase(directory)
        self.directory = directory
        #Episodes which weren't found on the web
        self._not_found = []
        self.scraped_count = 0

    def start_import(self):
        if self.db.db_file_exists():
            if cfg.get('database', 'reset', bool):
                os.unlink(self.db.dbfile)
                self.db.create_database(
                    force=True
                    )
        self.wrap()

    def episodes(self):
        """
        Yield Episodes in directory.
        Episodes returned from here are result of ez_parse_episode.
        """
        for epath in get_episodes(self.directory):            
            yield ez_parse_episode(epath)

    def scrape_episode(self, episode):
        """
        scrape_episode(Episode) -> Episode
        Fully parse it, look it up, fill it with info and return.
        Ideally results in an Episode with full info, ready for the database.
        Can raise ShowNotFoundError, SeasonNotFoundError or EpisodeNotFoundError
        """
        #TODO: be smarter (all eps in same dir should be the same series, right, unless there's a mix thing like incoming)
        if not episode.is_fully_parsed():
            episode = reverse_parse_episode(episode['file_path'], self.directory)
        scrapedep = lookup(episode)
        return scrapedep            

    def hard_scrape_path(self, path):
        """
        hard_scrape_path(path) -> Episode
        Do a reverse_parse and scrape given path.
        """
        ep = reverse_parse_episode(path, self.directory)
        return self.scrape_episode(ep)

    def wrap(self):
        excpt = (ShowNotFoundError, SeasonNotFoundError, EpisodeNotFoundError, IncompleteEpisodeError)
        for ep in self.episodes():
            upd = cfg.get('database', 'update', bool)
            exists = self.db.path_exists(ep['file_path'])
            if upd and exists: 
                log.debug(
                    'ep at %s exists in database, ignoring.', 
                    ep['file_path']
                    )
                #we're only supposed to update and current ep is in db
                continue                
            try:
                ep = self.scrape_episode(ep)
            except excpt as e:
                log.info(
                    'Suppressed lookup error for episode %s.\nMessage:%s' % (
                        ep, e.message)
                    )
                #try harder
                try: 
                    ep = self.hard_scrape_path(ep['file_path'])
                except excpt as e:                    
                    #i give up
                    self._not_found.append(ep)
                    self.db.add_unparsed_child(
                        os.path.relpath(
                            ep['file_path'],
                            self.db.directory
                            ))
            else:
                self.db.upsert_episode(ep)
                self.scraped_count+=1
        log.warning(
            '%s episodes were scraped and added to the database.', self.scraped_count
            )
        log.warning(
            '%s "episodes" were not fully parsed or not found the tvdb', len(self._not_found)
            )



class DifficultEpisodeHandler(object):
    """
    Handler of difficult episodes which can't be scraped with ordinary methods.
    """
    pass
