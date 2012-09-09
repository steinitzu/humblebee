import logging
from collections import defaultdict
import os
from stat import S_IFDIR, S_IFLNK, S_IFREG
from time import time
from errno import ENOENT

from fuse import FUSE, FuseOSError, Operations, LoggingMixIn



log = logging.getLogger('tvunfucker')

class FileSystem(LoggingMixIn, Operations):

    def __init__(self, db):
        #files will be taken straight from db, no stupid shit
        self.db = db
        pass


    def chmod(self, path, mode):
        return 0


    def chown(self, path, uid, gid):
        return 0

    def readdir(self, path, fh):
        now = time()
        dirmode = {
                'st_mode':(S_IFDIR | 0755),
                'st_ctime' : now,
                'st_mtime' : now,
                'st_atime' : now,
                'st_nlink' : 2
                }
        
        if path == '/':
            rows = self.db.get_series_plural('1', 1)
            ret = ['.', '..']
            for row in rows:
                ret.append(row['title'])
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
        iswhat = '' #season, series or episode        
        log.debug(path)
        pathpcs = path.strip('/').split('/')
        now = time()
        if path == '/': #root
            return {
                'st_mode':(S_IFDIR | 0755),
                'st_ctime' : now,
                'st_mtime' : now,
                'st_atime' : now,
                'st_nlink' : 2
                }                        
        elif len(pathpcs) ==  1: # series
            log.debug('Getting series: %s', pathpcs[0])            
            row = self.db.get_series_plural('title', pathpcs[0])
            if not row:
                raise FuseOSError(ENOENT)
            return {
                'st_mode' : (S_IFDIR | 0755),
                'st_ctime' : now,
                'st_mtime' : now,
                'st_atime' : now,
                'st_nlink' : 2
                }
        elif len(pathpcs) == 2:
            log.debug(
                'Getting season: %s of series: %s',
                pathpcs[0], pathpcs[1]
                )
            seasid = self.db.get_series_plural('title', pathpcs[0])[0]['id']
            row = self.db.get_seasons(
                #TODO: Need to make sure dirname is 's##'
                season_number=int(pathpcs[1][1:]), #first letter is 's', stripping it
                series_id=seasid
                )
            if not row:
                raise FuseOSError(ENOENT)
            return {
                'st_mode' : (S_IFDIR | 0755),
                'st_ctime' : now,
                'st_mtime' : now,
                'st_atime' : now,
                'st_nlink' : 2
                }

        elif len(pathpcs) == 3:
            #TODO: return the properties of the real ep file
            raise FuseOSError(ENOENT)
            
                
            
                
            
            """
            This is bullshit.
            I think I would actually create the directories
            on instantiation.
            I first make dirs for each series
            then subdirs for each season
            These are real dirs
            Just named based on text from db
            But then come the episodes
            Thse will be symlinks (or maybe not symlinks)
            maybe they are some kind of fake file thingy (probably symlink)
            when it's attributes are changed, it changes the database
            when filename is chantged, db is changed
            when it's moved, db is changed

            but it can only be moved into a a season directory

            Also, some kind of incremental scanning from the tvdb
            Also, option to submit user changes to tvdb

            make some kind of distinction between user and tvdb changes

            also there needs to be a virtual dir for unparsed eps
            just show them in origininal dir structure
            
            """
        elif path == '/_unparsed':
            #show some pile of unparseable shit
            raise FuseOSError(ENOENT)

        else:
            raise FuseOSError(ENOENT)




    
        
    

