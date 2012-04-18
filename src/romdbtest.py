import os, re

from romdb import scraper


def test_tv_db():
    import tvdb_api
    tvdb_key = '29E8EC8DF23A5918'
    t = tvdb_api.Tvdb(apikey=tvdb_key)
    series = t['My name is earl']
    print '\n'.join([unicode(val) for val in series[1].keys()])



def parse_file_name(name):
    single = {}

    name = name.lower()
    if re.match(r'.+\.s\d+e\d+\..+', s, re.UNICODE):
        #it is a valid scene release, either a season or one ep
        words = s.split('.')
        series = ''
        for word in words:
            pass


def parse_scene_release(name):
    """Parses info from file name of properly named scene release."""
    """
    Fuck can't write code right now.

    Do a regex and split the name into 'series', 'season' and 'ep' (if applicable)
    detect wether it is a single ep or a season folder (depends if it's S00E00 or just S00)
    """
    
    


        
    

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
