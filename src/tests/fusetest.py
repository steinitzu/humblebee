import os
import logging

import fuse

from tvunfucker import localdbapi, logger, thefuse, chainwrapper

log = logging.getLogger('tvunfucker')
log.setLevel(logging.DEBUG)

_currentdir = os.path.dirname(__file__)


_dbfile =  os.path.join(_currentdir, 'testdata/testfs/.tvunfucker.sqlite')


db = localdbapi.Database(_dbfile)
print db.get_rows("SELECT * FROM series;")
print db.get_row("SELECT * FROM series WHERE id = 73255;")

source = chainwrapper.EpisodeSource(os.path.dirname(_dbfile))


fs = thefuse.FileSystem(source)

mtpt = os.path.join(_currentdir, 'mount')
fuse = fuse.FUSE(fs, mtpt, foreground=True)
