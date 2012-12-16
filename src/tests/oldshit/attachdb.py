import os
import sqlite3
import logging

from tvunfucker import localdbapi

log = logging.getLogger('tvunfucker')
log.setLevel(logging.DEBUG)

dbfile = '/home/steini/projects/romdb/src/tests/testdata/testfs/.tvunfucker.sqlite'
db = localdbapi.Database(dbfile)



q = 'SELECT * FROM view_episode WHERE ep_number = ? AND season_number = ? AND series_title = ?'
paramas = (13, 4, 'Weeds')
log.debug(db._get_row(q, paramas))

q = "SELECT * FROM view_episode WHERE ep_number = 13"
log.debug(db._get_row(q))

