import logging

from .dbguy import TVDatabase
from .dirscanner import get_episodes
from .parser import ez_parse_episode, reverse_parse_episode
from .texceptions import InitExistingDatabaseError, IncompleteEpisodeError
from .texceptions import ShowNotFoundError, SeasonNotFoundError, EpisodeNotFoundError
from .tvdbwrapper import lookup

log = logging.getLogger('tvunfucker')

class Importer(object):    

    def __init__(self, directory, **kwargs):
        """
        the kwargs must be the command line options thingies, right..?
        """        
        self.config = self.make_config(**kwargs)
        self.db = TVDatabase(directory)
        self.directory = directory
        #Episodes which weren't found on the web
        self._not_found = []

    def make_config(self, **kwargs):
        """
        Make the config dict from kwargs.
        """
        config = {}
        config['reset_database'] = kwargs.get('reset_database', False)        

        return config

    def start_import(self):
        self.db.create_database(
            force=self.config['reset_database']
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
        if not not episode.is_fully_parsed():
            episode = reverse_parse_episode(episode['file_path'], self.directory)
        scrapedep = lookup(episode)
        return scrapedep            

    def wrap(self):
        for ep in self.episodes():
            try:
                ep = self.scrape_episode(ep)
            except (ShowNotFoundError, SeasonNotFoundError, EpisodeNotFoundError, IncompleteEpisodeError) as e:
                log.info(
                    'Suppressed lookup error for episode %s.\nMessage:%s' % (
                        ep, e.message)
                    )
                self._not_found.append(ep)
                self.db.add_unparsed_child(ep['file_path'])
                continue
            else:
                self.db.upsert_episode(ep)
