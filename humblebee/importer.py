#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging, os, time, shelve
from glob import glob
from datetime import datetime

from send2trash import send2trash

from .dbguy import TVDatabase
from .renaming import Renamer, SymlinkRenamer, make_unknown_dir
from .parser import reverse_parse_episode
from .texceptions import SeasonNotFoundError
from .texceptions import EpisodeNotFoundError
from .texceptions import IncompleteEpisodeError
from .texceptions import ShowNotFoundError
from .texceptions import InvalidDirectoryError
from .texceptions import RARError
from .tvdbwrapper import lookup
from .util import split_root_dir
from .util import normpath
from .util import bytestring_path
from .util import soft_unlink
from .util import syspath
from .util import safe_make_dirs
from .util import make_symlink
from .util import samefile
from .dirscanner import get_episodes
from .dirscanner import is_rar
from .dirscanner import get_file_from_single_ep_dir
from .unrarman import unrar_file
from .quality import quality_battle
from .quality import MediaInfoError
from .util import get_prog_home_dir
from . import appconfig as cfg

log = logging.getLogger('humblebee')

class Importer(object):

    lookup_error = (
        ShowNotFoundError,
        SeasonNotFoundError,
        EpisodeNotFoundError,
        IncompleteEpisodeError
        )
    
    def __init__(self, rootdir, destdir, **kwargs):
        self.db = TVDatabase(rootdir)
        self.rootdir = self.db.directory

        self._cleardb = cfg.get('database', 'clear', bool)
        self._update = cfg.get('database', 'update', bool)
        self._brute = cfg.get('importer', 'brute', bool)
        self._unrar = cfg.get('importer', 'unrar', bool)
        self._forcerename = cfg.get('importer', 'force-rename', bool)
        self._rename = cfg.get('importer', 'rename-files', bool)
        self._symlinks = cfg.get('importer', 'symlinks', bool)

        ns = cfg.get('importer', 'naming-scheme')
        if cfg.get('importer', 'symlinks', bool):
            self.renamer = SymlinkRenamer(self.rootdir, destdir, ns)
        elif cfg.get('importer', 'rename-files', bool):
            self.renamer = Renamer(self.rootdir, destdir, ns)   
        else:
            self.renamer = None


        if self._cleardb:
            soft_unlink(self._last_stat_path())
        self.last_stat = shelve.open(self._last_stat_path())

        self.failed_lookup = []
        self.added_to_db = []
        self.success_lookup = []
        self.extracted_rar = []
        self.failed_rar = []

    def do_import(self):
        if self.db.db_file_exists():
            if self._cleardb:
                self.db.create_database(force=True)
        else:
            self._cleardb = True #no existing db means "first" import
            self.db.create_database()
        def get_ep_by_id(id_):
            w = 'WHERE id = ?'
            p = (id_,)
            return self.db.get_episodes(w, p).next()
        log.info('Cleaning up')
        c = self.dust_database()
        for ep in get_episodes(self.rootdir):
            if self.should_import(ep):
                res = self.import_episode(ep)
                if res and self.renamer:
                    ep = get_ep_by_id(res)
                    self.renamer.move_episode(ep, force=self._forcerename)
            self.last_stat[ep.path('db')] = round(os.path.getmtime(ep.path()),2)
            self.last_stat.sync()
        if self._symlinks:
            make_unknown_dir(self.db, self.renamer.destdir)
        log.info('Cleaning up')
        cc = self.dust_database()
        c = c+cc
        log.info('Deleted %s zombie eps from database', c)
        log.info('Failed lookup count: %s', len(self.failed_lookup))
        log.info('Added to db count: %s', len(self.added_to_db))
        log.info('Succesful lookup count: %s', len(self.success_lookup))
        log.info('extracted rar count: %s', len(self.extracted_rar))
        log.info('failed rar count: %s', len(self.failed_rar))
        self.write_stats()

    def import_episode(self, ep):
        """
        Import a single episode.
        Lookup info, unrar, compare with existing ep, upsert to db.
        Actions performed depend on cfg options.
        Returns ep id or None
        """
        def upsert(epi):
            idd = self.db.upsert_episode(epi)
            self.added_to_db.append(epi)
            return idd            
        try:
            ep = self.fill_episode(ep)
        except self.lookup_error as e:
            self.failed_lookup.append(ep)
            self.db.add_unparsed_child(ep.path('rel'))
            return
        else:
            self.success_lookup.append(ep)
        if self._unrar and is_rar(ep.path()):
            ep = self.unrar_episode(ep)
        idindb = self.db.episode_exists(ep)
        if idindb and self._brute:
            return upsert(ep)
        elif idindb:
            better = self.get_better(ep)
            if better is ep:
                return upsert(better)
            else:
                return
        else:
            return upsert(ep)
            

    def get_better(self, ep):
        """
        Check if given `ep` is better quality than 
        one with same id in db.
        Returns True or False accordingly.
        """
        oldep = self.db.get_episodes('WHERE id=?', params=(ep['id'],)).next()
        if samefile(oldep.path(), ep.path()):
            return
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
            return ep
        if is_rar(ep.path()) or is_rar(oldep.path()):
            #can't battle rars
            return
        #let's fight
        try:
            return quality_battle(ep, oldep, self.db.directory)
        except MediaInfoError as e:
            log.warning(e.message)
            return
        

    def should_import(self, ep):
        """
        Decide if given episode should be scraped 
        or not.
        """
        if self._cleardb:
            return True #always scrape when clearing        
        p = ep.path('db')
        newmt = round(os.path.getmtime(ep.path()), 2)
        if self.last_stat.has_key(p):
            log.debug('"%s" was scraped last run.', p)
            oldmt = round(self.last_stat[p],2)
            if newmt > oldmt:
                log.debug('"%s" changed since last run.', p)
                log.debug('newmt: %s, oldmt: %s', newmt,oldmt)
                return True
            elif self._update:
                return False #no change, update, no scrape
            else:
                return True
        else:
            return True #not been scraped before, do it

    def fill_episode(self, ep):
        """
        Fill the given `ep` with info from tvdb and return it.
        Raises `lookup_error` if not possible.
        """
        if not ep.is_fully_parsed():
            ep = reverse_parse_episode(
                ep.path(), self.rootdir
                )
        try:
            return  lookup(ep)
        except self.lookup_error as e:
            log.debug(e.message)
            ep = reverse_parse_episode(ep.path(), self.rootdir)
            return lookup(ep)

    def unrar_episode(self, ep, out_dir=None):
        """
        unrar_episode(Episode)
        Errors are swallowed.
        """
        p = ep.path()
        if not os.path.isdir(p):
            raise InvalidDirectoryError(
                'Episode path must be a directory. "%s" is not.' % p
                )
        log.info('Extracting "%s" from rar files.', p)
        try:            
            unrar_file(p, out_dir=out_dir)
        except RARError as e:
            log.debug('RARError: %s', e.message)
            self.failed_rar.append(ep)
            return ep            
        #get new path to episode        
        ep['file_path'] = get_file_from_single_ep_dir(p)
        delr = cfg.get('importer', 'delete-rar', bool)
        if delr:
            self.trash_rars_in_dir(p)
        self.extracted_rar.append(ep)
        return ep

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
            
    def _last_stat_path(self):
        return normpath(os.path.join(
            self.rootdir,
            cfg.get('database', 'resume-data-filename')
            ))

    def dust_database(self):
        """
        Remove entries from database for non-existing paths.
        Run after import.
        """
        c = 0
        for ep in self.db.get_episodes():
            if not os.path.exists(ep.path()):
                c+=1
                self.db.delete_episode(ep['id'])
        return c

    def write_stats(self):
        """
        Write some stats for this import.
        """
        statdir = os.path.join(
            get_prog_home_dir('humblebee'),
            'stats'
            )
        safe_make_dirs(statdir)
        sfile = os.path.join(
            statdir, 
            str(int(time.time()))
            )
        f = open(sfile, 'w')
        f.write(
            '\nimport at: %s\n----------------\n' % (
                str(datetime.now()))
            )
        
        f.write(
            '\nsuccess lookup count: %s\n----------------\n' % len(self.success_lookup)
            )
        f.write('\n'.join([e.path() for e in self.success_lookup]))
        f.write(
            '\nfailed lookup count: %s\n----------------\n' % len(self.failed_lookup)
            )
        f.write('\n'.join([e.path() for e in self.failed_lookup]))
        f.write(
            '\nadded to db count: %s\n----------------\n' % len(self.added_to_db)
            )
        f.write('\n'.join([e.path() for e in self.added_to_db]))
        f.write(
            '\nextracted from rar files count: %s\n----------------\n' % len(self.extracted_rar)
            )
        f.write('\n'.join([e.path() for e in self.extracted_rar]))
        f.write(
            '\nfailed rar files count: %s\n----------------\n' % len(self.failed_rar)
            )
        f.write('\n'.join([e.path() for e in self.failed_rar]))
        f.close()
                
