import os, re

from romdb import scraper, tvcaching, romexception

#dirs that are not searched for shows
excluded_dirs = ('sample', )

#regular expressions for parsing series, season and ep info from filenames
filename_regexes = [
    r'(?P<series>.+)\.s(?P<season>\d+)e(?P<episode>\d+)', #series.name.s01e01.extra.shit
    r'(?P<series>(.?)*)\s(?P<season>\d+)x(?P<episode>\d+)', #series name 01x01 extra shit    
    ]

#file names that will be completely ignored (* for wildcard)
ignored_files = ('thumbs.db',) #todo: this belongs in a config file
video_files = ('avi', 'mkv', 'mpg', 'mpeg', 'mp4', 'wmv') #todo: add more types

def test_tv_db():
    import tvdb_api
    tvdb_key = '29E8EC8DF23A5918'
    t = tvdb_api.Tvdb(apikey=tvdb_key)
    series = t['My name is earl']
    print '\n'.join([unicode(val) for val in series[1].keys()])


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
    




    
    
def crack_my_scull(source):
    """
    Go through a tv source.
    """
    cache = tvcaching.CacheStore()
    if not os.path.isdir(source):
        raise RomError('Target source [%s] is not a directory.' % source)


    subdirs = []
    files = []    
    
    for name in os.listdir(source):
        if name in ignored_files:
            continue
        elif os.path.isfile(name):
            files.append(os.path.join(source, name))            
        elif os.path.isdir(name):
            subdirs.append(os.path.join(source, name))

def contains_single_episode(path):
    #BLEH
    """
    Tells us if the supplied dir contains a single episode.
    Returns true or false.\n
    Needs 3 points to qualify.
    """
    

def parse_file_name(name):
    single = {}    

    name = name.lower()
    if re.match(r'.+\.s\d+e\d+\..+-.+', s, re.UNICODE):
        #it is a valid scene release, a single ep
        single = parse_proper_scene_single(name)
        return single
    elif re.match(r'.+\.s\d+\..+-.+', s, re.UNICODE):
        #it is a valid scene release, but a directory with a season
        #TODO: write it
        return single
        


def parse_proper_scene(name):
    """Parses info from file name of properly named scene release."""
    """
    Fuck can't write code right now.

    Do a regex and split the name into 'series', 'season' and 'ep' (if applicable)
    detect wether it is a single ep or a season folder (depends if it's S00E00 or just S00)
    """
    single = {}
    #get the season and ep as a '.s00e00.' string
    seasonandep = re.search(ur'\.s\d+e\d+\.', name, re.UNICODE).group()
    eindex = seasonandep.index('e')

    single['season'] = seasonandep[2:eindex]
    single['episode'] = seasonandep[eindex+1:-1]

    series = name[:name.index(seasonandep)]
    single['series'] = series.replace('.', ' ')

    return single
    
def test_strip_crap():
    test_strings = os.listdir('/media/boneraper/+incoming')
    res_dict = {}
    for name in test_strings:
        single = {}
        title = re.sub(r'\{.+\}', '', name)
        title = re.sub(r'\[.+\]', '', title) #dno if need        
        title = re.split(r'\.S\d+', title)[0]
        title = title.strip()

        
        


        title = title.replace('.', ' ')
        title = title.strip('-')    

    
        

        print 'Original: [%s]. Result: [%s]' % (name, title)        
    

def main():
    for name in find_episodes('/media/boneraper/+incoming'):
        print name
        
    #scraper.test()
    #test_tv_db()
    #test_strip_crap()


if __name__ == '__main__':
    main()
