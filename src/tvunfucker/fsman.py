import os

from .texceptions import InvalidDirectoryError, NoSuchDatabaseError
from .dbguy import TVDatabase
from .util import replace_bad_chars, zero_prefix_int


def _setup_env(source_dir, dest_dir):
    """
    _setup_env(source_dir, dest_dir) -> TVDatabase
    setup the environment before creating the filesystem.
    Create destination directory, spawn a TVDatabase instance.
    """
    db = TVDatabase(source_dir)
    if not db.db_file_exists():
        raise NoSuchDatabaseError(
            'There is no database file in source_dir %s.'\
            +'Please scrape this directory first.' % (source_dir)
            )        
    if os.path.exists(dest_dir):
        if not os.path.isdir(dest_dir):
            raise InvalidDirectoryError('"%s" is not a valid directory.' % dest_dir)
        if os.path.samefile(source_dir, dest_dir):
            raise InvalidDirectoryError(
                'source_dir and dest_dir can not be the same directory (%s)' % (dest_dir)
                )
        if os.listdir(dest_dir):
            raise InvalidDirectoryError(
                'destination directory is not empty (%s)' % (dest_dir)
                )
    else:
        #will raise OSError if not possible to make dir
        os.makedirs(dest_dir)
    return db

def _safe_make_dirs(path):
    """
    _safe_make_dirs(path)
    os.makedir but suppresses errors when dir already exists.
    All other errors are raised as normal.
    """
    try:
        os.makedirs(path)
    except OSError as e:
        if e.errno == 17: #file exists
            pass
        else:
            raise

filename_mask_ep = (
    ' %(series_title)s s%(season_number)se%(ep_number)s%(extra_ep_number)s %(title)s%(ext)s'
    ) 

def _make_ep_filename(ep):
    nums = ('season_number', 'ep_number')
    ep = dict(ep.items())
    for num in nums:
        ep[num] = zero_prefix_int(ep[num])
    ep['ext'] = os.path.splitext(ep['file_path'])[1]
    if not ep['extra_ep_number']:
        ep['extra_ep_number'] = ''
    else:
        ep['extra_ep_number'] = zero_prefix_int(ep['extra_ep_number'])
    return replace_bad_chars(filename_mask_ep % ep)
    

def create_filesystem(source_dir, dest_dir):
    db = _setup_env(source_dir, dest_dir)
    for ep in db.get_episodes():
        firstair = ep['series_start_date']
        if firstair:
            firstair = firstair.year
        else: 
            firstair = 'no-date'
        dirp = os.path.join(
            dest_dir, 
            '%s (%s)' % (replace_bad_chars(ep['series_title']), firstair),
            's%s' % zero_prefix_int(ep['season_number'])
            )
        _safe_make_dirs(dirp)
        epp = os.path.join(
            dirp,
            _make_ep_filename(ep)
            )
        fp = os.path.abspath(
            os.path.join(source_dir, ep['file_path'])
            )
        os.symlink(fp, epp)
    
    unpd = os.path.join(dest_dir, '_unknown')
    os.mkdir(unpd)
    q = 'SELECT * FROM unparsed_episode'
    for row in db.execute_query(q):
        cp = row['child_path']        
        if os.path.isdir(os.path.join(source_dir, cp)):
            _safe_make_dirs(os.path.join(unpd, cp))
        elif os.path.isfile(os.path.join(source_dir, cp)):
            _safe_make_dirs(
                os.path.split(os.path.join(unpd, cp))[0]
                )
            os.symlink(
                os.path.abspath(os.path.join(source_dir, cp)),
                os.path.join(unpd, cp)
                )
        else:
            raise Warning('%s is not a file or dir' % cp)
            
