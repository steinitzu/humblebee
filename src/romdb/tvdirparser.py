import os, re

from romlog import *

#dirs that are not searched for shows
ignored_dirs = ['sample', 'Sample']
ignored_files = []

#regular expressions for parsing series, season and ep info from filenames
filename_regexes = [
    #r'(?P<series>.+)\.s(?P<season>\d+)e(?P<episode>\d+)', #series.name.s01e01.i.dont.care
    #r'(?P<series>(.?)*)\s(?P<season>\d+)x(?P<episode>\d+)', #series name 01x01 i dont care
    #Series name S01E01 i dont care
    #series.name.s01e01.i.dont.care
    #other similarly formed (i.e. everything before s01e01 is treated as series name)
    r'(?P<series>[\w\.\s]*)[\\\/\.\-_\s]*[Ss](?P<season>\d+)[eE](?P<episode>\d+)'
    ]


#file names that will be completely ignored (* for wildcard)
ignored_files = ('thumbs.db',) #todo: this belongs in a config file
video_files = ('.avi', '.mkv', '.mpg', '.mpeg', '.mp4', '.wmv') #todo: add more types


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
            print '\n\nWHATCK\n'            
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
        

def scan_tv_source(source):
    """
    Scan a tv show folder for shiz.
    """
    #TODO: go recursively through source and do magic
    for i in get_sub_directories(source):
        rom_log.info(i)
    for i in get_video_files(source):
        rom_log.info(i)



def find_episodes(source):
    """
    Find episodes in give directory.
    """
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
        if match:
            info['series'] = match.group('series')
            info['season'] = match.group('season')
            info['episode'] = match.group('episode')
            break
        match = re.match(expr, filename, re.UNICODE | re.IGNORECASE)
    if not info:
        info = magic_parse_filename(filename)
    if not info: #check again after the magic
        return False
    info['series'] = info['series'].replace('.', ' ') #todo: strip more crap
    info['season'] = int(info['season'])
    info['episode'] = int(info['episode'])
    return info

    
    

def magic_parse_filename(filename):
    #TODO: write a function that uses magic to parse weirdly named files
    #which don't match any of the regular expressions
    pass
