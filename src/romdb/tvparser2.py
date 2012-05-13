import os, re
import regexes
junk = regexes.junk
tv_regexes = regexes.tv_regexes
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
        super(Episode,self).__init__(
            season_num=None,
            series_name=None,
            ep_num=None,
            extra_ep_num=None,
            extra_info=None,
            release_group=None,
            which_regex=None
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
        s = ''
        for key,value in self.items():
            s+='%s = %s\n' % (key,value)
        s+='path = \'%s\'' % self.path
        return s
            
    

class TVParser(object):

    """
    This represents a single source directory for the most part.\n

    attributes - \n
    \t source_dir - absolute path to the given source directory
    \t unparsed_eps - a list of Episode objects that were not successfully parsed
                      might be partially or completely unparsed\n
    \t parsed_eps - successfully parsed eps (this means simply that
                    the episode's series_name, ep_num and season_num keys are there
                    but says nothing about the accuracy of the information.\n
    \t single_ep_dirs - directories which are believed to contain a single episode\n
    \t found_at_tvdb - episodes which have been found at the tvdb
                       these usually have accurate information\n
    """
    def __init__(self, sourcedir):
        self.source_dir = sourcedir
        self.unparsed_eps = []
        self.parsed_eps = []
        self.single_ep_dirs = []
        self.found_at_tvdb = []
        
    def scan_source(self):
        self._scan_source(self.source_dir)        

    def _scan_source(self, dir_):
        """
        Does a deep search in dir_, looking for media files.\n
        All dir names are parsed as eps, if matching they are added to
        self.single_ep_dirs .\n
        media files are added to parsed_eps and unparsed_eps respectively
        as Episode objects.
        """
        if not os.path.isdir(dir_):
            raise RomError('\'%s\' is not a valid directory.' % dir_)

        for subdir in get_sub_directories(dir_):
            direp = Episode(subdir)
            direp = self.parse_episode(direp)
            if direp.is_fully_parsed():
                self.add_ep_to_bin(direp)
                continue
            for file_ in get_video_files(subdir):
                ep = Episode(file_)
                ep = self.parse_episode(ep)
                if ep.is_fully_parsed():
                    self.add_ep_to_bin(ep)
                    continue
                ep = self.parse_episode_upwards(ep)
                self.add_ep_to_bin(ep)
            self._scan_source(subdir)                

    def parse_episode(self, ep):
        """
        Episode -> Episode
        """
        directory,filename = os.path.split(ep.path)
        if os.path.isfile(ep.path):
            filename = os.path.splitext(filename)[0]
        match = None
        for regex in tv_regexes:
            match = re.match(regex.pattern,filename)
            if match:
                ep['which_regex'] = regex.alias
                break
        if not match:
            return ep
        ep.safe_update(match.groupdict())
        return ep

    def parse_episode_upwards(self,ep):
        """
        parse_episode_upwards(Episode) -> Episode\n
        For the filenames that couldn't be parsed by parse_filename\n
        Will parse parent and grandparent directory names for info as well,
        trying to get a full (series_name,season_num,ep_num) Episode object going.\n
        It goes up from the file, starting with .. , then goes up to ../..
        
        """        
        directory,filename = os.path.split(ep.path)
        if os.path.isfile(ep.path):
            filename = os.path.splitext(filename)[0]

        #initiate stage one
        direponeup = Episode(directory)
        direponeup = self.parse_episode(direponeup)
        ep.safe_update(direponeup)
        if ep.is_fully_parsed(): return ep

        #initiate stage two
        directory,filename = os.path.split(directory)
        direptwoup = Episode(directory)
        direptwoup = self.parse_episode(direptwoup)
        ep.safe_update(direptwoup)

        if ep.is_fully_parsed(): return ep

        #initiate stage three (we are a failure)
        if ep['season_num'] and not ep['series_name']:
            ep['series_name'] = os.path.split(directory)[1]
        return ep

    def add_ep_to_bin(self, ep):
        """
        add_ep_to_bin(self,ep) -> None
        adds the given ep to the respective bin.\n
        unparsed_eps, parsed_eps, single_ep_dirs
        """        
        if os.path.isfile(ep.path) and ep.is_fully_parsed():
            ep.clean_ep()
            self.parsed_eps.append(ep)
        elif os.path.isdir(ep.path) and ep.is_fully_parsed():
            ep.clean_ep()
            self.single_ep_dirs.append(ep)
        elif os.path.isfile(ep.path):
            self.unparsed_eps.append(ep)

    #def fill_from_tv_db(self, ep):
        
            
                
def get_sub_directories(dir_):
    """
    A generator functions which yields first level sub
    directories in the given dir_.\n
    Ignores dirs in ignored_dirs.\n
    yields absolute paths.
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
    Generator function. Yields video files in given dir_\n
    yields absolute paths
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
        
