#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging, os
from glob import glob

from send2trash import send2trash

from .dbguy import TVDatabase
from .dirscanner import get_episodes, get_file_from_single_ep_dir, is_rar
from .parser import reverse_parse_episode
from .texceptions import IncompleteEpisodeError
from .texceptions import ShowNotFoundError, SeasonNotFoundError, EpisodeNotFoundError
from .texceptions import InvalidDirectoryError
from .tvdbwrapper import lookup
from .quality import quality_battle
from .unrarman import unrar_file
from . import appconfig as cfg
from . import __pkgname__

log = logging.getLogger(__pkgname__)

class Importer(object):    

    scrape_errors = (
        ShowNotFoundError,
        SeasonNotFoundError,
        EpisodeNotFoundError,
        IncompleteEpisodeError
        )

    def __init__(self, directory, **kwargs):
        #TODO: take options from cfg and do update and reset functions
        """
        the kwargs must be the command line options thingies, right..?
        """        
        self.db = TVDatabase(directory)
        self.directory = self.db.directory
        #Episodes which weren't found on the web
        self._not_found = []
        self.scraped_count = 0 #deprecate
        self.success_count = 0

    def start_import(self):
        if self.db.db_file_exists():
            if cfg.get('database', 'reset', bool):
                os.unlink(self.db.dbfile)
                self.db.create_database(
                    force=True
                    )
        else:
            self.db.create_database()
        self.wrap()

    def episodes(self):
        """
        Yield Episodes in directory.
        Episodes returned from here are result of ez_parse_episode.
        """
        for ep in get_episodes(self.directory):            
            yield ep

    def _scrape_episode(self, episode):
        """
        scrape_episode(Episode) -> Episode
        Fully parse it, look it up, fill it with info and return.
        Ideally results in an Episode with full info, ready for the database.
        Can raise ShowNotFoundError, SeasonNotFoundError 
        or EpisodeNotFoundError
        """
        #TODO: be smarter (all eps in same dir
        #should be the same series, right, unless 
        #there's a mix thing like incoming)
        if not episode.is_fully_parsed():
            episode = reverse_parse_episode(
                episode.path(), self.directory)
        scrapedep = lookup(episode)
        return scrapedep            

    def _fallback_scrape_episode(self, path):
        """
        hard_scrape_path(path) -> Episode
        Do a reverse_parse and scrape given path.
        """
        ep = reverse_parse_episode(path, self.directory)
        return self._scrape_episode(ep)


    def fill_episode(self, ep):
        """
        fill_episode(Episode) -> Episode
        Parses and looks up given episode info and returns.
        May raise exceptions in self.scrape_errors.
        """
        try:
            ep = self._scrape_episode(ep)
        except self.scrape_errors as e:
            log.debug(
                'Failed lookup for episode %s.\nMessage:%s', 
                ep.path(),
                e.message
                )
            ep = self._fallback_scrape_episode(ep.path())
        return ep

    def full_path(self, path):
        """
        full_path(path) -> db.directory + path
        Gets full path concatenated with source directory.
        convenience function.
        """
        return os.path.join(self.db.directory, path)

    def _wrap_single(self, ep):
        """
        _wrap_single(Episode)
        Wrapper method to handle single episode, from filename to db.
        """
        fileindb = self.db.path_exists(ep.path('rel'))
        update = cfg.get('database', 'update', bool)
        if fileindb and update:
            #don't need to scrape cause we ain't gunna do nuthin'
            log.debug(
                '"%s" already in database and update option set, skipping',
                ep.path()
                )
            return
        try:
            ep = self.fill_episode(ep)
        except self.scrape_errors as e:
            self._not_found.append(ep)
            self.db.add_unparsed_child(
                ep.path('rel')
                )
            return
        if fileindb:
            return self.db.upsert_episode(ep) #we update it

        idindb = self.db.episode_exists(ep)
        if idindb:
            oldep = self.db.get_episodes(
                'WHERE id = ?', params=(ep['id'],)).next()
            log.info(
                'Found duplicates. Original: "%s". Contender: "%s".',
                oldep.path(),
                ep.path()
                ) 
            if not os.path.exists(oldep.path()):
                log.info(
                    'Original: "%s" does not exist anymore".'\
                    +' Replacing with contender: "%s".', 
                    oldep.path(), 
                    ep.path()
                    )
                return self.db.upsert_episode(ep)
            #can't be having same episode twice, thems ids be primary keys, yo
            if is_rar(ep.path()) or is_rar(oldep.path()):
                return #there be rars, just leave it alone
            better = quality_battle(ep, oldep, self.db.directory) 
            if better: 
                bpath = better.path()
            else: 
                bpath = None
            log.info(
                'Quality battle between "%s" and "%s". "%s" wins.',
                ep.path(), oldep.path(), bpath
                )
            if not better: 
                #neither is better, it ain't no thang, do nuthin'
                return 
            elif better is oldep:
                return
            else:
                log.info('Replacing "%s" with "%s" in db.', 
                         oldep.path(), ep.path())                
                return self.db.upsert_episode(ep)
        else:
            return self.db.upsert_episode(ep)                                         

    def trash_rars_in_dir(self, directory):
        """
        trash_rars_in_dir(directory)
        Send rar files in given directory to trash.
        """
        log.info('Sending rar files in "%s" to trash.', directory)
        rnfiles = glob(
            os.path.join(directory, '*.r[0-9][0-9]'))
        rarfiles = glob(
            os.path.join(directory, '*.rar'))
        for f in rnfiles+rarfiles:
            send2trash(f)

    def unrar_episode(self, ep, out_dir=None):
        """
        unrar_episode(Episode)
        """
        p = ep.path()
        if not os.path.isdir(p):
            raise InvalidDirectoryError(
                'Episode path must be a directory. "%s" is not.' % p
                )
        log.info('Extracting "%s" from rar files.', p)
        unrar_file(p, out_dir=out_dir)
        #get new path to episode
        
        ep['file_path'] = get_file_from_single_ep_dir(p)
        delr = cfg.get('importer', 'delete-rar', bool)
        if delr:
            self.trash_rars_in_dir(p)
        return ep
        
    def wrap(self):
        for ep in self.episodes():
            if cfg.get('importer', 'unrar', bool) and is_rar(ep.path()):
                ep = self.unrar_episode(ep)
            res = self._wrap_single(ep)
            if isinstance(res, int):
                self.success_count+=1
        log.warning(
            '%s episodes were scraped and added to the database.', 
            self.success_count
            )
        log.warning(
            '%s "episodes" were not fully parsed or not found the tvdb', 
            len(self._not_found)
            )
        

class DifficultEpisodeHandler(object):
    """
    Handler of difficult episodes which can't be scraped with ordinary methods.
    """
    pass
