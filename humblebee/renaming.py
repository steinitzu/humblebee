import os, logging, shutil

from .util import zero_prefix_int as padnum
from .util import replace_bad_chars
from .util import normpath
from .util import ensure_utf8
from .util import safe_make_dirs
from .util import samefile
from .util import prune_dirs
from .util import make_symlink
from .dbguy import TVDatabase
from .texceptions import FileExistsError, InvalidDirectoryError
from .texceptions import NoSuchDatabaseError
from . import appconfig

log = logging.getLogger('humblebee')

class NamingScheme(object):

    def ep_filename(self, ep):
        """
        Get bottom level filename for episode.
        """
        raise NotImplementedError

    def season_filename(self, ep):
        """
        Filename of season directory.
        """
        raise NotImplementedError

    def series_filename(self, ep):
        """
        Filename of series directory.
        """
        raise NotImplementedError

    def full_path(self, ep, root=None):
        """
        Get full series/season/ep path.
        Result should be treated as relative to 
        whatver root dir is.
        If `root` is passed, the resulting path will be 
        an absolute path.
        """
        eu = ensure_utf8
        fp = os.path.join(
            eu(self.series_filename(ep)),
            eu(self.season_filename(ep)),
            eu(self.ep_filename(ep))
            )
        if root:
            fp = normpath(os.path.join(root, fp))            
        return fp

class Friendly(NamingScheme):
    """
    Series Name (year)/s01/Series Name s01e02 Episode Title.avi
    """
    ep_mask = u'%(series_title)s s%(season_number)se%(ep_number)s%(extra_ep_number)s %(title)s%(ext)s'
    series_mask = u'%(series_title)s (%(series_start_date)s)'
    season_mask = u'season %(season_number)s'
    
    def ep_filename(self, ep):
        epd = dict(ep.items())
        eep = epd['extra_ep_number']
        epd['season_number'] = padnum(epd['season_number'])
        epd['ep_number'] = padnum(epd['ep_number'])
        if eep:
            epd['extra_ep_number'] = 'e'+padnum(eep)
        else:
            epd['extra_ep_number'] = ''             
        p = ep.path()
        if os.path.isdir(p):
            epd['ext'] = ''
        else:
            epd['ext'] = os.path.splitext(p)[1]
        return replace_bad_chars(self.ep_mask % epd)

    def season_filename(self, ep):
        epd = dict(ep.items())
        epd['season_number'] = padnum(ep['season_number'])
        return replace_bad_chars(self.season_mask % epd)

    def series_filename(self, ep):
        """
        Get a series foldername from ep.
        """
        epd = dict(ep.items())
        firstair = ep['series_start_date']
        if firstair:
            epd['series_start_date'] = firstair.year
        else:
            epd['series_start_date'] = 'no-date'
        if ep['series_title'].endswith('(%s)' % epd['series_start_date']):
            epd['series_title'] = ep['series_title'][:-7]
        return replace_bad_chars(self.series_mask % epd)


class Structured(NamingScheme):
    """
    Series Name (year)/s01/Series Name s01e02 Episode Title.avi
    """
    ep_mask = u'%(series_title)s s%(season_number)se%(ep_number)s%(extra_ep_number)s %(title)s%(ext)s'
    series_mask = u'%(series_title)s'
    season_mask = u'season %(season_number)s'
    
    def ep_filename(self, ep):
        epd = dict(ep.items())
        eep = epd['extra_ep_number']
        epd['season_number'] = padnum(epd['season_number'])
        epd['ep_number'] = padnum(epd['ep_number'])
        if eep:
            epd['extra_ep_number'] = 'e'+padnum(eep)
        else:
            epd['extra_ep_number'] = ''             
        p = ep.path()
        if os.path.isdir(p):
            epd['ext'] = ''
        else:
            epd['ext'] = os.path.splitext(p)[1]
        return replace_bad_chars(self.ep_mask % epd)

    def season_filename(self, ep):
        epd = dict(ep.items())
        epd['season_number'] = padnum(ep['season_number'])
        return replace_bad_chars(self.season_mask % epd)

    def series_filename(self, ep):
        """
        Get a series foldername from ep.
        """
        epd = dict(ep.items())
        return replace_bad_chars(self.series_mask % epd)
    

naming_schemes = {
    'friendly' : Friendly,
    'structured' : Structured
    }


class Renamer(object):
    """
    Handles renaming/moving of episodes in both filesystem and database.
    """    
    def __init__(self, rootdir, destdir, naming_scheme='friendly'):
        self.db = TVDatabase(rootdir)
        self.destdir = normpath(destdir)
        self.naming_scheme = naming_schemes[naming_scheme]()
        safe_make_dirs(self.destdir)
        if not samefile(self.destdir, self.db.directory):
            self.destdb = TVDatabase(self.destdir)
            self.destdb.create_database(soft=True)
        else:
            self.destdb = self.db
        self.clutter = appconfig.get('scanner', 'clutter').split(',')

    def update_db_path(self, ep, newpath):
        """
        Update file_path in database for given episode.
        """
        ep['file_path'] = newpath
        return self.destdb.upsert_episode(ep)

    def spare_dest_file(self, fn):
        """
        Move file to _unknown dir.
        """
        pj = os.path.join
        unknown = normpath(
            pj(self.destdir, '_unknown')
            )
        safe_make_dirs(unknown)
        destfile = normpath(
            pj(unknown, os.path.split(fn)[1])
            )
        os.rename(fn, destfile)
        

    def move_episode(self, ep, force=False):
        """
        Path will be moved to `destdir` in a filename structure 
        decided by `naming_scheme`.
        If `destdir` is the same as `db.directory`, path will also be updated 
        in database.        

        Containing directory of ep is pruned afterwards.

        If the new path currently exists, it will be moved to '_unknown' before 
        ep is put in its place. Unless `force` is True, then it is overwritten.
        """        
        oldfile = ep.path()
        olddir = os.path.dirname(oldfile)
        newfile = self.naming_scheme.full_path(ep, root=self.destdir)
        if samefile(oldfile, newfile):
            return ep
        log.debug('Renaming "%s" -> "%s"', oldfile, newfile)
        pathindb = self.db.path_exists(ep.path('db'))        
        if os.path.exists(newfile) and not force:
            self.spare_dest_file(newfile)
        if os.path.isdir(newfile) and force:
            shutil.rmtree(newfile)
        safe_make_dirs(os.path.dirname(newfile))
        os.rename(oldfile, newfile)
        #if samefile(self.destdir, self.db.directory):
        self.update_db_path(ep, newfile)
        prune_dirs(olddir, root=self.db.directory, clutter=self.clutter)
        return ep

class SymlinkRenamer(Renamer):

    """
    Safer version of Renamer. Creates symlinks in destdir instead of actually moving 
    any files.
    `rootdir` may not be the same as `destdir`
    """    
    def __init__(self, rootdir, destdir, naming_scheme='friendly'):        
        super(SymlinkRenamer, self).__init__(rootdir,destdir,naming_scheme)
        if samefile(self.destdir, self.db.directory):
            raise InvalidDirectoryError(
                'rootdir and destdir can not be the same directory.'
                )

    def move_episode(self, ep, force=True):
        oldfile = ep.path()
        newfile = self.naming_scheme.full_path(ep, root=self.destdir)
        make_symlink(oldfile, newfile, overwrite=True)





def make_unknown_dir(db, destdir):
    """nn
    When symlinks, make a virtual dir based on 
    unparsed_episode table.
    """
    pj = os.path.join
    root = normpath(
        pj(destdir, '_unknown')
        )
    safe_make_dirs(root)        
    q = 'SELECT * FROM unparsed_episode'
    for row in db.execute_query(q):
        path = row['child_path']
        rpath = pj(db.directory, path)
        vpath = pj(root, path)
        if os.path.isdir(rpath):
            safe_make_dirs(vpath)
        else:
            make_symlink(rpath, vpath)

def make_symlinkfs(rootdir, destdir, naming_scheme='friendly'):
    """
    Make a symlinkfs in destdir based on existing database in rootdir.
    """
    db = TVDatabase(rootdir)
    if not db.db_file_exists():
        raise NoSuchDatabaseError(
            'No tv database in "%s", please import first.' % rootdir
            )
    if not os.path.exists(destdir):
        safe_make_dirs(destdir)
    renamer = SymlinkRenamer(rootdir, destdir, naming_scheme='friendly')
    for ep in db.get_episodes():
        renamer.move_episode(ep)    
    make_unknown_dir(db, destdir)


def renamer_all(rootdir, destdir, force=False, naming_scheme='friendly'):
    """
    Rename all episodes in database in `rootdir` to `destdir`.
    """
    db = TVDatabase(rootdir)
    if not db.db_file_exists():
        raise NoSuchDatabaseError(
            'No tv database in "%s", please import first.' % rootdir
            )
    if not os.path.exists(destdir):
        safe_make_dirs(destdir)
    renamer = Renamer(rootdir, destdir, naming_scheme='friendly')
    for ep in db.get_episodes():
        renamer.move_episode(ep, force=force)
    
