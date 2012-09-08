import os
import logging

import fuse

from tvunfucker import localdbapi, logger, thefuse

log = logging.getLogger('tvunfucker')
log.setLevel(logging.DEBUG)

_currentdir = os.path.dirname(__file__)


_dbfile =  os.path.join(_currentdir, 'testdata/testfs/.tvunfucker.sqlite')


db = localdbapi.Database(_dbfile)
print db.get_rows("SELECT * FROM series;")
print db.get_row("SELECT * FROM series WHERE id = 73255;")


fs = thefuse.FileSystem(_dbfile)

mtpt = os.path.join(_currentdir, 'testmount')
fuse = fuse.FUSE(fs, mtpt, foreground=True)
