#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from collections import defaultdict
import os
from stat import S_IFDIR, S_IFLNK, S_IFREG
from time import time
from errno import ENOENT


from fuse import FUSE, FuseOSError, Operations, LoggingMixIn

from util import zero_prefix_int, timestamp
from parser import ez_parse_episode as parse_file
import logger



log = logging.getLogger('tvunfucker')

class FileSystem(LoggingMixIn, Operations):

    filename_mask_ep = (
       ' %(series_title)s s%(season_number)se%(ep_number)s%(extra_ep_number)s %(title)s%(ext)s'
       )
    filename_mask_season = 's%(season_number)s'    
    
    def __init__(self, db):
        #files will be taken straight from db, no stupid shit
        self.db = db
        self.symlinks = {} #source : target
        self.files = {}
        for ep in self.db.get_episodes():
            self.files[self.make_filename(ep, 'episode')] = ep
        for series in self.db.get_series_plural():
            self.files[self.make_filename(series, 'series')] = series
        for season in self.db.get_seasons():
            self.files[self.make_filename(season, 'season')] = season            

    def make_filename(self, row, etype='episode'):
        mask = None
        row = dict(row)
        if etype == 'episode':
            mask = self.filename_mask_ep
            nums = ('season_number', 'ep_number', 'extra_ep_number')
            for num in nums:
                row[num]=zero_prefix_int(row[num])                
            row['ext'] = os.path.splitext(row['file_path'])[1]
            if not row['extra_ep_number']:
                row['extra_ep_number'] = ''
        elif etype == 'season' :
            mask = self.filename_mask_season
        elif etype == 'series':
            return row['title']
        return mask % row

    @logger.log_time
    def readdir(self, path, fh):
        log.debug('path: %s', path)

        defret = ['.', '..']
        pathpcs = self._split_path(path)

        if path == '/':
            rows = self.db.get_series_plural()
            return defret+[row['title'] for row in rows]
        elif len(pathpcs) == 1: #series
            rows = self.db.get_seasons(series_title=pathpcs[0])

            ret = defret

            for row in rows:
                row = dict(row)
                row['season_number'] = zero_prefix_int(row['season_number'])
                ret.append(self.filename_mask_season % row)
            return ret
        elif len(pathpcs) == 2: #season, get eps
            f = parse_file(path)            
            rows = self.db.get_episodes(
                season_number=f['season_num'],
                series_title=pathpcs[0]
                )
            ret = defret
            for row in rows:
                row = dict(row)
                nums = ('season_number', 'ep_number', 'extra_ep_number')
                for num in nums:
                    row[num]=zero_prefix_int(row[num])                
                row['ext'] = os.path.splitext(row['file_path'])[1]
                if not row['extra_ep_number']:
                    row['extra_ep_number'] = ''
                ret.append(self.filename_mask_ep % row)
            return ret

    def symlink(self, target, name):
        target = 1

    def readlink(self, path):
        data = self.get_metadata(path)
        #a keyerror here should NEVER happen, if it does, you made programming error derp
        realpath = data[0]['file_path']
        log.debug('Real path of %s = %s', path, realpath)
        return realpath        

    @logger.log_time
    def get_metadata(self, path):
        """
        Returns the episode from the given path, season or series info
        as a dict. See the db schema for column info.
        """
        pathpcs = self._split_path(path)        

        def check_rows(rows):
            if not rows:
                raise FuseOSError(ENOENT)
            elif len(rows) > 1:
                raise WTFException(
                    'filename %s has more than one candidate' % pathpcs[0]
                    )
            return rows[0]        

        if path == '/': #root
            return None

        elif path == '/_unparsed':
            raise FuseOSError(ENOENT)

        elif len(pathpcs) == 1: #series_dir
            rows = self.db.get_series_plural(
                title=pathpcs[0]
                )
            row = check_rows(rows)
            return row, 'series'
        elif len(pathpcs) == 2: #season dir
            f = parse_file(path)

            log.debug('Prased ep: %s', f)
            rows = self.db.get_seasons(
                series_title = pathpcs[0],
                season_number = f['season_num']
                )
            log.debug('Found seasons: %s', rows)
            return check_rows(rows), 'season'
        elif len(pathpcs) == 3: #episode file
            f = parse_file(path)
            log.debug('Prased ep: %s', f)
            rows = self.db.get_episodes(
                season_number=f['season_num'],
                series_title=pathpcs[0],
                ep_number=f['ep_num']
                )
            return check_rows(rows), 'episode'        
        

    def getattr(self, path, fh=None):
        log.debug('path: %s', path)

        now = time()

        dirmode = {
                'st_mode':(S_IFDIR | 0755),
                'st_ctime' : now,
                'st_mtime' : now,
                'st_atime' : now,
                'st_nlink' : 2
                }
        filemode = {
                'st_mode':(S_IFREG | 0755),
                'st_ctime' : now,
                'st_mtime' : now,
                'st_atime' : now,
                'st_nlink' : 2
                }

        symlinkmode = {
            'st_mode' : (S_IFLNK | 755),
            'st_ctime' : now,
            'st_mtime' : now,
            'st_atime' : now,
            'st_nlink' : 2
            }
            
        """
        pathpcs = self._split_path(path)

        def check_rows(rows):
            if not rows:
                raise FuseOSError(ENOENT)
            elif len(rows) > 1:
                raise WTFException(
                    'filename %s has more than one candidate' % pathpcs[0]
                    )
            return rows[0]
        """
            
        def make_ret(row, mode='dir'):
            l = None
            if mode == 'dir' : l = dirmode
            elif mode == 'file': l = filemode
            elif mode == 'symlink' : l = symlinkmode
            l.update({
                    'st_ctime':timestamp(row['created_time']),
                    'st_mtime':timestamp(row['modified_time'])
                    })
            return l
        """
        if path == '/': #root
            return dirmode

        elif path == '/_unparsed':
            raise FuseOSError(ENOENT)

        elif len(pathpcs) == 1: #series_dir
            rows = self.db.get_series_plural(
                title=pathpcs[0]
                )
            row = check_rows(rows)
            return make_ret(row)
        elif len(pathpcs) == 2: #season dir
            f = parse_file(path)

            log.debug('Prased ep: %s', f)
            rows = self.db.get_seasons(
                series_title = pathpcs[0],
                season_number = f['season_num']
                )
            log.debug('Found seasons: %s', rows)
            return make_ret(check_rows(rows))
        elif len(pathpcs) == 3: #episode file
            f = parse_file(path)
            log.debug('Prased ep: %s', f)
            rows = self.db.get_episodes(
                season_number=f['season_num'],
                series_title=pathpcs[0],
                ep_number=f['ep_num']
                )
            return make_ret(check_rows(rows), 'symlink')
        """
        if path == '/': return dirmode
        data = self.get_metadata(path)
        if data[1] == 'series' or data[1] == 'season':
            return make_ret(data[0], 'dir')
        elif data[1] == 'episode':
            return make_ret(data[0], 'symlink')
        raise FuseOSError(ENOENT)
        

    def chmod(self, path, mode):
        return 0

    def chown(self, path, mode):
        return 0

    def _split_path(self, path):
        return path.strip('/').split('/')

    

    

    
