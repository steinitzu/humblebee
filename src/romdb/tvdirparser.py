import os, re
from collections import namedtuple

from romlog import *
from regexes import tv_regexes

raise DeprecationWarning('This module has been deprecated')

#TODO: Use the ep objects instead of passing paths around

#dirs that are not searched for shows
ignored_dirs = ['sample', 'Sample']
ignored_files = []


def compile_regex(pattern):
    return re.compile(pattern, re.IGNORECASE | re.UNICODE)

#regular expressions for parsing series, season and ep info from filenames
filename_regexes = [
    #Series name S01E01 i dont care
    #series.name.s01e01.i.dont.care
    #other similarly formed (i.e. everything before s01e01 is treated as series name)
    compile_regex(r'(?P<series>[\w\.\s]+)[\\\/\.\-_\s]*[Ss](?P<season>\d+)[eE](?P<episode>\d+)'),
    #series name 01x01 i don't care
    compile_regex(r'(?P<series>[\w\.\s]+)[\\\/\.\-_\s]*(?P<season>\d+)[xX](?P<episode>\d+)'),
    ]
partial_filename_regexes = [
    #s01e01 i don't care    
    compile_regex(r'[sS](?P<season>\d+)[eE](?P<episode>\d+)'),
    #episode 1.avi
    compile_regex(r'episode[\\\/\.\-_\s]*(?P<episode>\d+)'),
    ]

season_string_regexes = [
    compile_regex(r'[sS](?P<season>\d+)'),
    compile_regex(r'season[\\\/\.\-_\s]*(?P<season>\d+)'),    
    ]

#file names that will be completely ignored (* for wildcard)
ignored_files = ('thumbs.db',) #todo: this belongs in a config file
video_files = ('.avi', '.mkv', '.mpg', '.mpeg', '.mp4', '.wmv') #todo: add more types

"""
A simple namedtuple class holding a single episode.\n
info should be a {series:str, episode:int, season:int} dict and filename
and absolute path to the media file.
"""
Episode = namedtuple('Episode', 'info, path')


def parse_filename(path):
    """
    Takes absolute path as input -> returns an Episode object
    """
    ep = Episode({'season':None,'series':None,'episode':None}, path)
    directory,filename = os.path.split(path)
    match = None
    for pattern in tv_regexes:
        match = re.match(pattern,filename)
        if match:
            break
    if not match:
        #ep is unparseable
        return ep
    groups = match.groupdict()
    #when score is 0, info is complete
    #each key in (season,series,episode) adds 1 to the score
    score = -3
    if groups.haskey('series'):
        ep.info['series'] = groups['series']
        score+=1
    if groups.haskey('season'):
        ep.info['season'] = int(groups['season'])
        score+=1
    if groups.haskey('episode'):
        ep.info['episode'] = int(groups['episode'])
        score+=1
    if score == 0:
        #parsing is complete
        return ep
    if ep.info['season'] is None and ep.info['episode'] is not None:
        seasoninfo = parse_filename(directory)
        if seasoninfo.info['season'] is not None and seasoninfo.info['series'] it not None:
            ep.info['series'] = seasoninfo.info['series']
            ep.info['season'] = seasoninfo.info['season']
    return ep
    
class TVSourceScanner(object):
    """
    TVSourceScanner class: \n
    Takes a path as a first parameter and 'scan_tv_source' will scan that
    directory for tv shows.\n

    attrs: \n
        string source: the media directory to scan\n
        list single_ep_dirs: holds paths to dirs which were found to contain a single episode\n
        list unparseable_eps: holds paths to files and dirs which the parsing
        algorithms were unable to parse tv show information from.
        Items in this list will be run through a more advanced algorithm
        which tries to get info from the parenting directory structure.
        list proper_episodes: properly parsed media files go here
    """
    
    def __init__(self, source):
        self.source = source
        self.single_ep_dirs = []
        self.unparseable_eps = []
        self.proper_episodes = []
        self.half_parsed_episodes = []

    def recursive_parse_dir(self, dir_):
        """
        The whole shebang.
        """
        if not os.path.isdir(dir_):
            raise RomError('\'%s\' is not a valid directory.' % dir_)

        for subdir in get_sub_directories(dir_):
            ep = get_info_from_filename(subdir)
            if ep.info:
                #we handle single ep dirs specially cause the special mkay
                self.single_ep_dirs.append(ep) 
                continue
            for file_ in get_video_files(subdir):
                ep = get_info_from_filename(file_)
                if ep.info:
                    #TODO: add to database
                    self.proper_episodes.append(ep)
                else:
                    self.unparseable_eps.append(ep)                    
            self.recursive_parse_dir(subdir)


    def parse_unparseable(path):
        filename = os.path.split(path)
        match = None
        for expr in partial_filename_regexes:
            match = re.match(expr, filename)
            if match:
                break
        info = {'series':None,'season':None,'episode':None}
        missing_fields = []
        try: info['series'] = match.group('series')
        except IndexError: missing_fields.append('series')
        try: info['season'] = match.group('season')
        except IndexError: missing_fields.append('season')
        try: info['episode'] = match.group('episode')
        except IndexError: missing_fields.append('episode')

        if missing_fields:
            self.parse_dir_tree_upwards(path)

    def parse_dir_tree_upwards(self, path, missing_fields=[]):
        """
        Keeps climbing up the directory tree until it
        either hits the source dir or matches all the missing fields.
        """
        dirpath = os.path.dirname(path)
        if os.path.samefile(dirpath, self.source):
            return
        #TODO: do what the doc says
        

    def scan_tv_source(self):
        """
        Scan a tv show folder for shiz.
        """
        #reset the stuff
        del self.single_ep_dirs[:]
        self.recursive_parse_dir(self.source)


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

def get_info_from_filename(path):
    filename = os.path.split(path)[1]
    if not filename:
        raise RomError('No filename in path \'%s\'.' % path)

    info = parse_episode_filename(filename)
    return Episode(info, path)     

def parse_episode_filename(filename):
    """
    Attempts to parse filename for series, season and
    episode info.
    Will return a dictionary with those values if
    successful, otherwise 'False'.
    """
    if not filename:
        raise RomError('Empty values for filename are not allowed.')

    info = {}
    match = None
    for expr in filename_regexes:
        match = re.match(expr, filename.lower())
        if match:
            info['series'] = match.group('series')
            info['season'] = match.group('season')
            info['episode'] = match.group('episode')
            break
    #if not info:
    #    info = magic_parse_filename(filename)
    if not info: #check again after the magic
        return False
    info['series'] = info['series'].replace('.', ' ') #todo: strip more crap
    info['season'] = int(info['season'])
    info['episode'] = int(info['episode'])
    return info

    
    


        

#####################3
### DEPRECATED
#####################

def find_episodes(source):
    """
    Find episodes in give directory.    
    """
    raise DeprecationWarning()
    if not os.path.isdir(source):
        raise RomError(
            'Target source [%s] is not a directory.' % source
            )

    failedfiles = [] #files that failed to parse
    
    for name in os.listdir(source):
        lname = name.lower()
        abspath = os.path.join(source, name)
        info = None
        if lname in ignored_files:
            continue
        elif os.path.isfile(abspath):
            info = parse_episode_filename(lname)
            yield info  if info else failedfiles.append(abspath)            






