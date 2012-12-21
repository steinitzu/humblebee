from .dbguy import TVDatabase
from .dirscanner import get_episodes
from .texceptions import InitExistingDatabaseError
from .texceptions import ShowNotFoundError, SeasonNotFoundError, EpisodeNotFoundError
from .tvdbwrapper import lookup

class Importer(object):

    def __init__(self, directory, **kwargs):
        """
        the kwargs must be the command line options thingies, right..?
        """        
        self.config = self.make_config(**kwargs)
        self.db = TVDatabase(directory)
        self.directory = directory

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

    def episodes(self):
        """
        Yield Episodes in directory.
        """
        #get some Episode objects from ez_parse, yield them for further analyzing
        for epath in get_episodes(self.directory):            
            #todo: what to do here?
            pass
