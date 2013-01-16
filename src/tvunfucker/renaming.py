import os

from util import zero_prefix_int as padnum
from util import replace_bad_chars
from util import normpath
from util import ensure_utf8


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

    def full_path(self, ep):
        """
        Get full series/season/ep path.
        Result should be treated as relative to 
        whatver root dir is.
        """
        eu = ensure_utf8
        fp = os.path.join(
            eu(self.series_filename(ep)),
            eu(self.season_filename(ep)),
            eu(self.ep_filename(ep))
            )
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

def rename_episode(ep, naming_scheme):    
    pass
