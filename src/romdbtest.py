import os, re

from romdb import scraper, tvcaching, romexception

#file names that will be completely ignored (* for wildcard)
ignored_files = ('thumbs.db', 'Thumbs.db')

def test_tv_db():
    import tvdb_api
    tvdb_key = '29E8EC8DF23A5918'
    t = tvdb_api.Tvdb(apikey=tvdb_key)
    series = t['My name is earl']
    print '\n'.join([unicode(val) for val in series[1].keys()])

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
    """
    Tells us if the supplied dir contains a single episode.
    Returns true or false.\n
    Needs 3 points to qualify.
    """
    issingle = 0 #points
    if len(os.listdir(path)) == 1:
        issingle+=1
        
    
            

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
    #scraper.test()
    #test_tv_db()
    test_strip_crap()


if __name__ == '__main__':
    main()
