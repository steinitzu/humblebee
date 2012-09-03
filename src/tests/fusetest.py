import os
import logging

import llfuse

from tvunfucker import localdbapi, logger, thefuse

log = logging.getLogger('tvunfucker')
log.setLevel(logging.DEBUG)

_currentdir = os.path.dirname(__file__)


_dbfile =  os.path.join(_currentdir, 'testdata/testfs/.tvunfucker.sqlite')


db = localdbapi.Database(_dbfile)
print db.get_rows("SELECT * FROM series;")
print db.get_row("SELECT * FROM series WHERE id = 73255;")


fs = thefuse.VirtualLinker(_dbfile)


llfuse.init(
    fs,
    os.path.join(_currentdir, 'testmount'),
    [  b'fsname=llfuse_xmp', b"nonempty" ]
    
    #[ b'fsname=testtvfs', b'noempty']
    )


try:
    llfuse.main(single=True)
except:
    llfuse.close(unmount=False)
llfuse.close()
