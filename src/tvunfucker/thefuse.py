import logging
from collections import defaultdict
import os
from stat import S_IFDIR, S_IFLNK, S_IFREG
from time import time
from errno import ENOENT
from time import mktime

from fuse import FUSE, FuseOSError, Operations, LoggingMixIn



log = logging.getLogger('tvunfucker')

class FileSystem(LoggingMixIn, Operations):

    def __init__(self, db):
        #files will be taken straight from db, no stupid shit
        self.db = db
        pass

    def _split_path(self, path):
        ret = {
            'series' : None,
            'season' : None,
            'episode' : None
            }
        if path == '/':
            return ret
        pathpcs = path.strip('/').split('/')
        lenp = len(pathpcs)
        if lenp == 1: #series
            ret['series'] = pathpcs[0]
            return ret
        elif lenp == 2: #season
            ret['series'] = pathpcs[0]
            ret['season'] = int(pathpcs[1][1:])
            return ret
        elif lenp == 3: #episode
            return ret #TODO: Do it later

    def _datetime_to_timestamp(self, dt):
        return mktime(dt.timetuple())

    def chmod(self, path, mode):
        return 0


    def chown(self, path, uid, gid):
        return 0

    def readdir(self, path, fh):

        defret = ['.','..']

        if path == '/':
            rows = self.db.get_series_plural()
            return defret + [row['title'] for row in rows]
        pathparts = self._split_path(path)
        if pathparts['series']:
            series = self.db.get_series_plural(
                title=pathparts['series']
                )[0]
            rows = self.db.get_seasons(
                series_id=series['id']
                )
            if not pathparts['season']:
                return defret + [
                    's'+str(row['season_number']) for row in rows
                    ]
            season = self.db.get_seasons(
                series_id=series['id'],
                season_number=pathparts['season']
                )[0]
            episodes = self.db.get_episodes(
                season_id = season['id']
                )
            #hack
            epfrm = '%(series)s-s%(season)se%(epnum)s-%(title)s%(ext)s'
            ret = defret[:]
            for ep in episodes:
                data = {
                    'title' : ep['title'].replace(' ', '.'),
                    'season' : str(season['season_number']),
                    'epnum' : str(ep['ep_number']),
                    'series' : pathparts['series'],
                    'ext' : os.path.splitext(ep['file_path'])[1]
                    }
                ret.append(epfrm % data)
            return ret


    def getattr(self, path, fh=None):
        """
           struct stat {
               dev_t     st_dev;     /* ID of device containing file */
               ino_t     st_ino;     /* inode number */
               mode_t    st_mode;    /* protection */
               nlink_t   st_nlink;   /* number of hard links */
               uid_t     st_uid;     /* user ID of owner */
               gid_t     st_gid;     /* group ID of owner */
               dev_t     st_rdev;    /* device ID (if special file) */
               off_t     st_size;    /* total size, in bytes */
               blksize_t st_blksize; /* blocksize for file system I/O */
               blkcnt_t  st_blocks;  /* number of 512B blocks allocated */
               time_t    st_atime;   /* time of last access */
               time_t    st_mtime;   /* time of last modification */
               time_t    st_ctime;   /* time of last status change */
           };
        """
        now = time()
        dirmode = {
                'st_mode':(S_IFDIR | 0755),
                'st_ctime' : now,
                'st_mtime' : now,
                'st_atime' : now,
                'st_nlink' : 2
                }

        if path == '/': #root
            return dirmode
        
        if path == '/_unparsed':
            #show some pile of unparseable shit
            raise FuseOSError(ENOENT)        

        pathparts = self._split_path(path)
        if pathparts['series']:
            rows = self.db.get_series_plural(
                title=pathparts['series']
                )
            if not rows:
                raise FuseOSError(ENOENT)
            series = rows[0]
            if not pathparts['season']:
                dirmode['st_ctime'] = self._datetime_to_timestamp(
                    series['created_time']
                    )
                dirmode['st_mtime'] = self._datetime_to_timestamp(
                    series['modified_time']
                    )
                return dirmode
            elif not pathparts['episode']:
                rows = self.db.get_seasons(
                    series_id=series['id'],
                    season_number=pathparts['season']
                    )
                if not rows:
                    raise FuseOSError(ENOENT)
                season = rows[0]
                dirmode['st_ctime'] = self._datetime_to_timestamp(
                    season['created_time']
                    )
                dirmode['st_mtime'] = self._datetime_to_timestamp(
                    season['modified_time']
                    )
                return dirmode
            elif pathparts['episode']:
                raise FuseOSError(ENOENT) #episodes not ready yet                

        else:
            raise FuseOSError(ENOENT)




    
        
    

