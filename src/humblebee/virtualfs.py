#!/usr/bin/env/python
#encoding:utf-8

import os, logging

from .dbguy import TVDatabase
from .texceptions import NoSuchDatabaseError
from .util import replace_bad_chars, scene_style, zero_prefix_int, normpath, ensure_utf8
from .util import safe_make_dirs

log = logging.getLogger('humblebee')

FNMASKEP = u'%(series_title)s.s%(season_number)se%(ep_number)s%(extra_ep_number)s.%(title)s%(ext)s'
FNMASKSERIES = u'%(series_title)s (%(series_start_date)s)'
FNMASKSEASON = u'season %(season_number)s'

def _make_env(rootdir, destdir):
    """
    _make_env(rootdir, destdir) -> TVDatabase
    Setup the environment for the virtual fs.
    Open a `TVDatabase` instance in `rootdir` and make 
    `destdir` directories if needed.
    TVDatabase instance is returned.
    """
    db = TVDatabase(rootdir)
    if not db.db_file_exists():
        raise NoSuchDatabaseError(
            'There is no tv database in given rootdir: %s' % 
            (rootdir)
            )
    if not os.path.exists(destdir):
        os.makedirs(destdir)
    return db


def ep_filename(ep):
    nums = ('season_number', 'ep_number')
    strings = ('series_title', 'title')
    oep = ep
    ep = dict(ep.items())
    for s in strings:
        ep[s] = scene_style(ep[s])
    for num in nums:
        ep[num] = zero_prefix_int(ep[num])
    ep['ext'] = os.path.splitext(oep.path())[1]
    if not ep['extra_ep_number']:
        ep['extra_ep_number'] = ''
    else:
        ep['extra_ep_number'] = 'e'+zero_prefix_int(ep['extra_ep_number'])
    return replace_bad_chars(FNMASKEP % ep)



def series_filename(ep):
    """
    Get a series foldername from ep.
    """
    ep = dict(ep.items())
    firstair = ep['series_start_date']
    if firstair:
        ep['series_start_date'] = firstair.year
    else:
        ep['series_start_date'] = 'no-date'
    if ep['series_title'].endswith('(%s)' % ep['series_start_date']):
        ep['series_title'] = ep['series_title'][:5]
    return replace_bad_chars(FNMASKSERIES % ep)

def season_filename(ep):
    """
    Get a season foldername.
    """
    ep = dict(ep.items())
    ep['season_number'] = zero_prefix_int(ep['season_number'])
    return replace_bad_chars(FNMASKSEASON % ep)

def _full_path(root, path):
    return normpath(os.path.join(root, path))

def safe_symlink(target, linkn):
    try:
        os.symlink(target, linkn)
    except OSError as e:
        if e.errno == 17:
            pass
        else:
            raise

def make_filesystem(rootdir, destdir):
    db = _make_env(rootdir, destdir)
    for ep in db.get_episodes():
        sername = series_filename(ep)
        seasname = season_filename(ep)
        epname = ep_filename(ep)
        seriesdir = normpath(
            os.path.join(ensure_utf8(destdir), sername)
            )
        seasondir = normpath(
            os.path.join(ensure_utf8(seriesdir), seasname)
            )
        epfile = normpath(
            os.path.join(ensure_utf8(seasondir), epname)
            )
        safe_make_dirs(seasondir)        
        safe_symlink(ep.path(), epfile)
    unknowndir = normpath(os.path.join(destdir, '_unknown'))
    safe_make_dirs(unknowndir)
    q = 'SELECT * FROM unparsed_episode'
    for row in db.execute_query(q):
        path = row['child_path']
        fullspath = _full_path(rootdir, path)
        fullvpath = _full_path(unknowndir, path)
        if os.path.isdir(fullspath):
            safe_make_dirs(fullvpath)
        elif os.path.isfile(fullspath):
            safe_make_dirs(os.path.split(fullvpath)[0])
            safe_symlink(fullspath, fullvpath)
        
        
            
