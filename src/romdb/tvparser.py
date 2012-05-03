import os, re

from regexes import tv_regexes, junk

from romexception import *

#dirs that are not searched for shows
ignored_dirs = ['sample', 'Sample']
ignored_files = []

#file names that will be completely ignored (* for wildcard)
ignored_files = ('thumbs.db',) #todo: this belongs in a config file
video_files = ('.avi', '.mkv', '.mpg', '.mpeg', '.mp4', '.wmv') #todo: add more types

class Episode(dict):

    def __init__(self, path):
        self.path = path
        super(Episode, self).__init__(
            season_num=None,
            series_name=None,
            ep_num=None,
            extra_ep_num=None,
            extra_info=None,
            release_group=None            
            )

    def __repr__(self):
        return 'series: %s, s%s, e%s\npath=%s' % (self['series_name'],self['season_num'],self['ep_num'],self.path)

    def safe_update(self, otherep):
        """
        safe_update(dict) -> None\n
        otherep can be an Episode object or any dict like
        object with the same keys.\n
        Unlike dict.update(), this will only update
        'None' values in the destination dict.        
        """
        for key in otherep.keys():
            if self[key] is not None: continue
            self[key] = otherep[key]


class TVParser(object):

    def __init__(self, sourcedir):
        self.source_dir = sourcedir
        self.unparseable_eps = []
        self.parsed_eps = []
        self.single_ep_dirs = []

    def _scan_source(self, dir_):
        """
        Recursively scans the given directory.
        """
        if not os.path.isdir(dir_):
            raise RomError('\'%s\' is not a valid directory.' % dir_)

        for subdir in get_sub_directories(dir_):
            ep = parse_filename(subdir)
            if ep['series_name'] and ep['season_num'] and ep['ep_num']:
                #we handle single ep dirs specially cause the special mkay
                self.single_ep_dirs.append(ep) 
                continue
            for file_ in get_video_files(subdir):
                ep = parse_filename(file_)
                if ep['series_name'] and ep['season_num'] and ep['ep_num']:
                    #TODO: add to database
                    self.parsed_eps.append(ep)
                else:
                    ep = hardcore_parse_filename(ep)
                    if ep['series_name'] and ep['season_num'] and ep['ep_num']:
                        self.parsed_eps.append(ep)
                    else:
                        self.unparseable_eps.append(ep)                    
            self._scan_source(subdir)

    def scan_source(self):
        self._scan_source(self.source_dir)

def get_sub_directories(dir_):
    """
    A generator functions which yields first level sub
    directories in the given dir_.
    Ignores dirs in ignored_dirs.
    """
    for name in os.listdir(dir_):
        abspath = os.path.join(dir_,name)
        if os.path.isfile(abspath):
            continue
        if name in ignored_dirs:            
            rom_log.info('ignored dir in ignore list \'%s\'' % abspath)
            continue
        yield abspath

def get_video_files(dir_):
    """
    Generator function. Yields video files in given dir_
    """
    for name in os.listdir(dir_):
        abspath = os.path.join(dir_,name)
        if not os.path.isfile(abspath):
            continue
        if name in ignored_files:
            rom_log.info('ignored file in ignore list \'%s\'' % abspath)
            continue
        ext = os.path.splitext(name)[1]
        if not ext in video_files:
            #TODO: do something about rar files
            continue
        yield abspath


def clean_name(name):
    """
    Strips all kinds of junk from a name.
    """
    name = re.sub(junk, ' ', name)
    name = name.strip()
    name = name.title()
    return name

def clean_ep(ep):
    """
    Strips junk from series name,
    converts season and ep numbers to ints.\n
    Shit like that.
    """
    ep['series_name'] = clean_name(ep['series_name'])
    try:
        ep['season_num'] = int(ep['season_num'])
    except ValueError as e:
        raise RomError(
            'Original message %s\n%s' % (e.message, ep)
            )        
    try:
        ep['ep_num'] = int(ep['ep_num'])
    except ValueError as e:
        raise RomError(
            'Original message %s\n%s' % (e.message, ep)
            )
    
    return ep

def parse_filename(path):
    """
    parse_filename(path) -> Episode\n
    path should be absolute.    
    """
    ep = Episode(path)
    directory,filename = os.path.split(path)
    match = None
    matchedregex = None
    for regex in tv_regexes:
        match = re.match(regex.pattern,filename)
        if match:
            break
    if not match:
        #we are unmatched
        return ep
    ep.update(match.groupdict())
    if ep['series_name'] and ep['season_num'] and ep['ep_num']:
        #wow, that was easy
        return clean_ep(ep)
    return ep

def hardcore_parse_filename(ep):
    """
    hardcore_parse_filename(Episode) -> Episode\n
    For the filenames that couldn't be parsed by parse_filename\n
    Will parse parent and grandparent directory names for info as well,
    trying to get a full (series_name,season_num,ep_num) Episode object going.    
    """
    directory,filename = os.path.split(ep.path)
    oneup = parse_filename(directory)
    #update ep with oneup info
    ep.safe_update(oneup)
    
    if ep['series_name'] and ep['season_num'] and ep['ep_num']:
        #ep is full
        return clean_ep(ep)

    directory,filename = os.path.split(directory)
    twoup = parse_filename(directory)
    ep.safe_update(twoup)

    if ep['season_num'] and not ep['series_name']:
        #We are going to assume that ../../ is the series name
        ep['series_name'] = os.path.split(directory)[1]
        
    if ep['series_name'] and ep['season_num'] and ep['ep_num']:
        #ep is full
        return clean_ep(ep)
    return ep
