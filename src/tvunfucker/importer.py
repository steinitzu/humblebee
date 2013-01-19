#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging, os
from glob import glob

from send2trash import send2trash

from .dbguy import TVDatabase
from .renaming import Renamer, SymlinkRenamer
from .parser import reverse_parse_episode
from .texceptions import SeasonNotFoundError
from .texceptions import EpisodeNotFoundError
from .texceptions import IncompleteEpisodeError
from .texceptions import ShowNotFoundError
from .texceptions import InvalidDirectoryError
from .tvdbwrapper import lookup
from .util import split_root_dir
from .util import normpath
from .util import bytestring_path
from .util import syspath
from .util import safe_make_dirs
from .util import make_symlink
from .dirscanner import get_episodes
from .dirscanner import is_rar
from .dirscanner import get_file_from_single_ep_dir
from .unrarman import unrar_file
from .quality import quality_battle
from . import appconfig as cfg

log = logging.getLogger('tvunfucker')

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
            self.last_stat = {}
        else:
            self.last_stat = self._read_laststat()

        self.failed_lookup = []
        self.added_to_db = []
        self.success_lookup = []

    def do_import(self):
        if self.db.db_file_exists():
            if self._cleardb:
                self.db.create_database(force=True)
        else:
            self.db.create_database()
        def get_ep_by_id(id_):
            w = 'WHERE id = ?'
            p = (id_,)
            return self.db.get_episodes(w, p).next()
        for ep in get_episodes(self.rootdir):
            self.last_stat[ep.path()] = os.path.getmtime(ep.path())
            if self.should_import(ep):
                res = self.import_episode(ep)
                if res and self.renamer:
                    ep = get_ep_by_id(res)
                    self.renamer.move_episode(ep, force=self._forcerename)
        if self._symlinks:
            self._make_unknown_dir()
        self._write_laststat(self.last_stat)
        log.info('Failed lookup count: %s', len(self.failed_lookup))
        log.info('Added to db count: %s', len(self.added_to_db))
        log.info('Succesful lookup count: %s', len(self.success_lookup))

    def import_episode(self, ep):
        """
        Import a single episode.
        Lookup info, unrar, compare with existing ep, upsert to db.
        Actions performed depend on cfg options.
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
        if self._unrar:
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
        return quality_battle(ep, oldep, self.db.directory)
        

    def should_import(self, ep):
        """
        Decide if given episode should be scraped 
        or not.
        """
        if self._cleardb:
            return True #always scrape when clearing        
        p = ep.path()
        newmt = round(os.path.getmtime(p), 2)
        #newmt = float(str(os.path.getmtime(p)))
        if self.last_stat.has_key(p):
            log.debug('"%s" was scraped last run.', p)
            if newmt > round(self.last_stat[p],2):
                log.debug('"%s" changed since last run.', p)
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

    def _make_unknown_dir(self):
        """
        When symlinks, make a virtual dir based on 
        unparsed_episode table.
        """
        pj = os.path.join
        root = normpath(
            pj(self.renamer.destdir, '_unknown')
            )
        safe_make_dirs(root)        
        q = 'SELECT * FROM unparsed_episode'
        for row in self.db.execute_query(q):
            path = row['child_path']
            rpath = pj(self.rootdir, path)
            vpath = pj(root, path)
            if os.path.isdir(rpath):
                safe_make_dirs(vpath)
            else:
                make_symlink(rpath, vpath)

    def _read_laststat(self):
        p = self._last_stat_path()
        try:
            f = open(p, 'r')
        except IOError as e:
            if e.errno == 2:
                return {} #means no last run
            else:
                raise
        stats = {}
        lines = f.readlines()
        f.close()
        for line in lines:
            bs = bytestring_path
            #path should always be relative to root
            path,mtime = line.strip('\n').split(';')
            path = normpath(os.path.join(bs(self.rootdir), bs(path)))
            stats[path] = round(float(mtime),2)
        return stats

    def _write_laststat(self, stats):
        p = self._last_stat_path()
        try:
            f = open(p, 'w')
        except IOError as e:
            raise
        s = ''
        for fn, mtime in stats.iteritems():
            fn = split_root_dir(fn, self.rootdir)[1]
            s+='%s;%s\n' % (fn,round(mtime,2))
        s = s[:-1] #strip last newline
        f.write(s)
        f.close()
            
    def _last_stat_path(self):
        return syspath(os.path.join(
            self.rootdir,
            cfg.get('database', 'resume-data-filename')
            ))
