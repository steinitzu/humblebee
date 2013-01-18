import os

from .util import zero_prefix_int as padnum
from .util import replace_bad_chars
from .util import normpath
from .util import ensure_utf8
from .util import safe_make_dirs
from .util import samefile
from .dbguy import TVDatabase
from .texceptions import FileExistsError


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
        if eep:
            epd['extra_ep_number'] = 'e'+padnum(eep)
        else:
            epd['extra_ep_number'] = ''                
        epd['ext'] = os.path.splitext(ep.path())[1]
        return self.ep_mask % epd

    def season_filename(self, ep):
        epd = dict(ep.items())
        epd['season_number'] = padnum(ep['season_number'])
        return self.season_mask % epd

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
        if ep['series_title'].endswith('(%s)' % ep['series_start_date']):
            epd['series_title'] = ep['series_title'][:5]
        return replace_bad_chars(self.series_mask % epd)

naming_schemes = {
    'friendly' : Friendly
    }


class Renamer(object):
    """
    Handles renaming/moving of episodes in both filesystem and database.
    """    
    def __init__(self, rootdir, destdir, naming_scheme='friendly'):
        self.db = TVDatabase(rootdir)
        self.destdir = normpath(destdir)
        self.naming_scheme = naming_scheme()
        
        #list of directories to try pruning when renaming is done
        self._pruneable = []

    def update_db_path(self, ep, newpath):
        """
        Update file_path in database for given episode.
        """
        ep['file_path'] = newpath
        return self.db.upsert_episode(ep)

    def move_episode(self, ep, force=False):
        """
        Path will be moved to `destdir` in a filename structure 
        decided by `naming_scheme`.
        If `destdir` is the same as `db.directory`, path will also be updated 
        in database.        

        If the new potential path exists already in filesystem, 
        an FileExistsError is raised.
        If  `force` is True, no error is raised and existing file is overwritten.
        """
        oldfile = ep.path()
        pathindb = self.db.path_exists(ep.path('db'))        
        newfile = self.naming_scheme.full_path(ep, root=self.destdir)
        if os.path.exists(newfile) and not force:
            raise FileExistsError(
                'Can not overwrite file at "%s"', newfile
                )
        safe_make_dirs(os.path.dirname(newfile))
        os.rename(oldfile, newfile)
        if samefile(self.destdir, self.db.directory):
            self.update_db_path(ep, newfile)
