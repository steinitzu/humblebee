import os
import logging

from chainwrapper import get_database
from util import replace_bad_chars, zero_prefix_int, fndotify
from texceptions import FileExistsError

log = logging.getLogger('tvunfucker')

def make_series_dir(title, sdate, source_dir):
    """    
    Make a directory for season according to title, sdate and source_dir.
    """
    if not sdate: year = 'unknown'
    else: year = sdate.year
    title = replace_bad_chars(title)    
    dirname = '%s (%s)' % (title, year)
    fpath = os.path.join(
        source_dir, dirname
        )
    try:
        os.mkdir(fpath)
    except OSError as e:
        if e.errno == 17:
            log.info(
                'dir: "%s" already exists in source dir: "%s". Moving on.',
                dirname,
                source_dir
                )
        else: raise
    return fpath

def make_season_dir(season_num, series_dir):
    """
    Make a subdirectory for season_num in given series_dir.
    """
    fpath = os.path.join(
        series_dir,
        's%s' % zero_prefix_int(season_num)
        )
    try:
        os.mkdir(fpath)
    except OSError as e:
        if e.errno == 17:
            log.info(
                'dir: %s already exists. Moving on.', fpath
                )
        else: raise
    return fpath

def make_filename(epdict, source_dir):
    mask = '%s.s%se%s.%s'
    if os.path.isfile(os.path.join(source_dir, epdict['file_path'])):
        ext = os.path.splitext(epdict['file_path'])[1]
    else: ext = ''

    fname = mask % (
        fndotify(epdict['series_title']),
        zero_prefix_int(epdict['season_number']),
        zero_prefix_int(epdict['ep_number']),
        fndotify(epdict['title'])
        )        
    return fname if not ext else fname+'.'+ext

def move_episode(episode, to_dir, source_dir):
    """
    Rename and move given episode to to_dir.
    """
    newfn = make_filename(dict(episode), source_dir)
    oldpath = os.path.join(source_dir, episode['file_path'])
    newpath = os.path.join(
        to_dir, newfn
        )
    if os.path.exists(newpath):
        #don't want to overwrite anything
        raise FileExistsError(
            'File "%s" already exists.' % newpath
            )
    os.rename(oldpath, newpath)
    return newpath

        
    
def do_renaming(directory):
    """
    Rename and move files according to the database.
    Accepts an EpisodeSource.
    """
    db = get_database(directory)    
    for episode in db.get_episodes():        
        dseries = make_series_dir(
            episode['series_title'],
            episode['series_start_date'],
            directory
            )
        dseason = make_season_dir(
            episode['season_number'],
            dseries
            )
        neweppath = move_episode(
            episode,
            dseason,
            directory
            )
        #todo: update the episode path in the database here
        #todo: clean up empty directories
