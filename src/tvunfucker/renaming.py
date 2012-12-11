import os

from chainwrapper import get_database
from util import replace_bad_chars, zero_prefix_int

log = logging.getLogger('tvunfucker')

def make_series_dir(title, year, source_dir):
    """    
    Make a directory for season according to title, year and source_dir.
    """
    title = replace_bad_chars(title)    
    dirname = '%s (%s)' % title, year    
    fpath = os.path.join(
        source_dir, dirname
        )
    try:
        os.mkdir(fpath)
    except OSError as e:
        if e.errno == 17:
            log.info(
                'dir: "%s" already exists in source dir: "%s". Moving on.'
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

def do_renaming(directory):
    """
    Rename and move files according to the database.
    Accepts an EpisodeSource.
    """
    db = get_database(directory)    
    for episode in db.get_episodes():        
        dseries = make_series_dir(
            epsiode['series_title'],
            episode['series_start_date'].year,
            directory
            )
        dseason = make_season_dir(
            episode['season_number'],
            dseries
            )
        

        

        
