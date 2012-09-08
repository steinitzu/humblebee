import logging
from collections import defaultdict
import os
from stat import S_IFDIR, S_IFLNK, S_IFREG
from time import time

from fuse import FUSE, FuseOSError, Operations, LoggingMixIn



log = logging.getLogger('tvunfucker')

class FileSystem(LoggingMixIn, Operations):

    def __init__(self, db):
        #files will be taken straight from db, no stupid shit
        pass


    def chmod(self, path, mode):
        return 0


    def chown(self, path, uid, gid):
        return 0

    def create(self, path, mode):

        raise NotImplementedError('Create is not implemented')

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
        log.debug(path)
        now = time()
        return {
            'st_mode':(S_IFDIR | 0755),
            'st_ctime' : now,
            'st_mtime' : now,
            'st_atime' : now,
            'st_nlink' : 2
            }





    
        
    

