import os

import tvregexes

def ez_parse_episode(path):
    """
    parse_episode(absolute path) -> dict\n
    Parses only the episode's filename.    
    """
    result = LocalEpisode(path)
    directory,filename = os.path.split(path)
    if os.path.isfile(path):
        filename = os.path.splitext(filename)[0]
    match = None
    for regex in tvregexes:
        match  = re.match(regex.pattern,filename)
        if match:
            result['which_regex'] = regex.alias
            break
    if not match:
        return result #I'm out
    result.safe_update(match.groupdict())
    return result

def reverse_parse_episode(path, source):
    """
    Takes a path to an episode and a tv source directory.\n
    Starts by parsing the name one dir up from path.\n
    If that directory contains a season_num but not a series_name,
    it will be assumed that two dirs up from path is the series name (as long as that
    doesn't match any regex).\n
    For example,\n
        if path is: '/media/tv/breaking bad/season 2/episode 4.avi'\n
        and source is: '/media/tv'\n
        then the result will be a LocalEpisode with the following:\n
        {'series_name' : 'breaking bad', 'season_num':2, 'ep_num':4}\n

    If the episode file is in the root of source and can't be parsed by any
    regex it will remain unparsed.
    """
    raise NotImplementedError('Shit is not implemented')
    directory, filename = os.path.split(path)
    if os.path.isfile(ep.path):
        filename = os.path.splitext(filename)[0]
    if os.path.samefile(directory, source):
        #episode is in the root of source, nothing can be done for it
        return False

    #the initial episode
    ep = ez_parse_episode(path)
    if ep.is_fully_parsed(): return ep #we're done

    in_ep = []
    if ep['series_name']: in_ep.append('series_name')
    if ep['season_num']: in_ep.append('season_num')
    if ep['ep_num']: in_ep.append('ep_num')

    #up one level in the tree from path
    oneup = ez_parse_episode(directory)
    if oneup.is_fully_parsed(): return oneup

    if ep['ep_num'] and (ep['season_num'] or oneup['season_num']):
        if oneup['series_name']:

            
            
    
    
    

class LocalEpisode(dict):
    """
    keys\n
    --------\n
    season_num: the season number (int)\n
    series_name: the series name (string(unicode))\n
    ep_num: episode number (int)\n
    extra_ep_num: for 2 parter episodes\n
    extra_info: some extra gunk from the filename\n
    release_group: the media (scene) release group\n
    which_regex: which regex parsed this filename\n
    path: absolute path to the episode object\n
    tvdb_ep: Episode object from the tvdb_api\n    
    """
    
    def __init__(self, path):
        super(Episode,self).__init__(
            season_num=None,
            series_name=None,
            ep_num=None,
            extra_ep_num=None,
            extra_info=None,
            release_group=None,
            which_regex=None,
            tvdb_ep = None,
            path = path
            )    

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
            
    def is_fully_parsed(self):
        """
        Ep is fully parsed, true or false.\n
        Will throw key exceptions if it's not a good ep dict.    
        """
        return self['series_name'] and self['season_num'] is not None and self['ep_num'] is not None

    def clean_name(self, name):
        #TODO: find junk
        """
        Strips all kinds of junk from a name.
        """
        if name is None: return None
        name = re.sub(junk, ' ', name)
        name = name.strip()
        name = name.title()
        return name

    def __setitem__(key, value):
        """
        Introducing some type safety and stuff to this dict.\n
        Will implicitly convert any value put in a key in numerics to int.\n
        """
        valid_keys = (
            'season_num',
            'series_name',
            'ep_num',
            'extra_ep_num',
            'extra_info',
            'release_group',
            'which_regex',
            'tvdb_ep',
            'path'
            )
        numerics = ('season_num', 'ep_num', 'extra_ep_num')
        if key not in valid_keys:
            raise KeyError(
                '\'%s\' is not a valid key for a LocalEpisode.\nValid keys are: %s' %
                (key, valid_keys)
                )
        if key in numerics and value is not None:
            #will raise an error if value is not a valid number
            return super(LocalEpisode, self).__setitem__(key,int(value))
        elif key is series_name and value is not None:
            #Will just assume that values is utf8 cause character encodings are hard
            #(so we most likely won't get unicode erros and shit)
            if isinstance(value, unicode):
                return super(LocalEpisode, self).__setitem__(key,value)
            elif isinstance(value, basestring):
                return super(LocalEpisode, self).__setitem__(key,unicode(value,'utf8'))
            else:
                raise ValueError(
                    'Value for key \'%s\' must be a string type, got \'%s\' (value: \s)' %
                    (key, type(value), value)
                    )
        #no more, please
        return super(LocalEpisode,self).__setitem__(key,value)


    def __repr__(self):
        s = u''
        for key,value in self.items():
            try:
                value = unicode(value)
            except UnicodeDecodeError:
                value = unicode(value.decode('utf8'))
            s+=u'%s = %s\n' % (key,value)
        path = self.path
        try:
            path = unicode(path)
        except UnicodeDecodeError:
            path = unicode(path.decode('utf8'))
        s+=u'path = \'%s\'\n' % path
        if self.bin:
            s+=u'current bin = %s' % self.bin.name
        return s
