import os

import tvregexes

def ez_parse_episode(path):
    """
    parse_episode(absolute path) -> dict\n
    Parses only the episode's filename.    
    """
    result = {}
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
        return result






class Episode(dict):
    
    def __init__(self, path):
        self.path = path
        self.bin = None
        super(Episode,self).__init__(
            season_num=None,
            series_name=None,
            ep_num=None,
            extra_ep_num=None,
            extra_info=None,
            release_group=None,
            which_regex=None
            )
        #the tvdb episode object (linked to season and show)
        self.tvdb_ep = None

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

    def _clean_name(self, name):
        """
        Strips all kinds of junk from a name.
        """
        if name is None: return None
        name = re.sub(junk, ' ', name)
        name = name.strip()
        name = name.title()
        return name

    def clean_ep(self):
        """
        Strips junk from series name,
        converts season and ep numbers to ints.\n
        Shit like that.\n
        This should be safe to call, even on unfilled eps.
        """        
        self['series_name'] = self._clean_name(self['series_name'])

        nums = ('season_num', 'ep_num', 'extra_ep_num')
        #exceptions are swallowed
        for num in nums:
            try:
                self[num] = int(self[num])
            except (ValueError, TypeError):
                self[num] = None
        return self

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




class LocalEpisode(dict):
    def __init__(self, path):
        

    
    


