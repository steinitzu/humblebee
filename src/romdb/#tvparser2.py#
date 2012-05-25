#!/usr/bin/env python
#encoding:utf-8

import os, re, time

import tvdb_api

import romdb
import regexes
import romlog
import romconfig
junk = regexes.junk
tv_regexes = regexes.tv_regexes
from romexception import *


log = romlog.rom_log

#dirs that are not searched for shows
ignored_dirs = ['sample', 'Sample']
ignored_files = []

#file names that will be completely ignored (* for wildcard)
ignored_files = ('thumbs.db',) #todo: this belongs in a config file
video_files = ('.avi', '.mkv', '.mpg', '.mpeg', '.mp4', '.wmv') #todo: add more types

def str_to_unicode(instr):
    if isinstance(instr, unicode):
        return instr
    ret = instr
    try:
        ret = unicode(instr)
    except UnicodeDecodeError:
        ret = unicode(instr.decode('utf8'))
    return ret

class EpisodeBin(dict):
    """
    Dict class to hold Episode objects.\n
    When an Episode is added it is removed from it's current bin and
    added to self.\n
    Episode holds a reference to a bin at all times. (except when it doesn't)    
    """
    #TODO: wtf rewrite this docstring

    def __init__(self,name):
        """
        name is the name of the bin, son
        """
        self.name = name        

    def __setitem__(self, key,value):
        """
        ___setitem___(self,strpath,Episode)
        """
        if isinstance(value,Episode):
            if value.bin:
                #remove it from the current bin
                log.debug(
                    'Removing ep "%s" from bin %s' %
                    (value.path, str(value.bin.name))
                    )
                value.bin.pop(key)                
            value.bin = self
        super(EpisodeBin, self).__setitem__(key,value)
        

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
            
    

class TVParser(object):

    """
    This represents a single source directory for the most part.\n

    attributes - \n

    the bins:\n\n
    {Episode.path : Episode}\n\n
    \t source_dir - absolute path to the given source directory
    \t unparsed_eps - Episode objects that were not successfully parsed
                      might be partially or completely unparsed\n
    \t parsed_eps - successfully parsed eps (this means simply that
                    the episode's series_name, ep_num and season_num keys are there
                    but says nothing about the accuracy of the information.\n
    \t single_ep_dirs - directories which are believed to contain a single episode\n
    \t found_at_tvdb - episodes which have been found at the tvdb
                       these usually have accurate information\n
    \t tvdb - tvdb_api.Tvdb instance with api key\n    
    """
    def __init__(self, sourcedir):
        self.source_dir = sourcedir
        self.unparsed_eps = EpisodeBin('unparsed_eps')
        self.parsed_eps = EpisodeBin('parsed_eps')
        self.single_ep_dirs = EpisodeBin('single_ep_dirs')
        self.found_at_tvdb = EpisodeBin('found_at_tvdb')
        self.tvdb = tvdb_api.Tvdb(actors=True, apikey=romdb.tvdb_key)
        
    def scan_source(self):
        self._scan_source(self.source_dir)
        #for ep in self.parsed_eps.values():
        #    self.update_ep_from_tvdb(ep)

    def get_eps_from_tvdb(self):
        for ep in self.parsed_eps.values():
            self.update_ep_from_tvdb(ep)
            #if ep.bin == self.found_at_tvdb:
            #    yield ep                

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
            log.debug('Working with subdir \'%s\'' % subdir)
            direp = Episode(str_to_unicode(subdir))
            direp = self.parse_episode(direp)
            if direp.is_fully_parsed():
                self.add_ep_to_bin(direp)
                continue
            for file_ in get_video_files(subdir):
                ep = Episode(str_to_unicode(file_))
                ep = self.parse_episode(ep)
                if ep.is_fully_parsed():
                    self.add_ep_to_bin(ep)  #nessssted
                    continue
                ep = self.parse_episode_upwards(ep)
                self.add_ep_to_bin(ep)
            self._scan_source(subdir)

    def _get_series_from_tvdb(self,series_name):
        """
        _get_series_from_tvdb(str) -> tvdb_api.Show\n
        Looks up the given series_name at tvdb. Will
        make use of the tvdb_api cache if available.\n
        If the series is not found -> returns None\n
        If connection to the tvdb fails it will retry
        [romconfig.tvdb_retry_count] times at an interval of
        [romconfig.tvdb_retry_interval].\n
        Raises a tvdb_api.tvdb_error when retries are exhausted.
        """
        retrycount = 0
        series = None
        while True:
            try:
                series = self.tvdb[str_to_unicode(series_name)]
                #series = self.tvdb[unicode(series_name.decode('utf8'))]
                break
            except tvdb_api.tvdb_shownotfound as e:
                break
            except tvdb_api.tvdb_error as e:
                #probably connection failure
                log.info('Failed to connect to the tvdb. \nmsg (%s)' % e.message)
                if retrycount >= romconfig.tvdb_retry_count:
                    raise #I tried
                log.info(
                    'Retry number (%d) in (%d) seconds' %
                    (retrycount,romconfig.tvdb_retry_interval)
                    )
                time.sleep(romconfig.tvdb_retry_interval)
                continue
        return series

    def update_ep_from_tvdb(self, ep):
        series = None
        log.debug('looking up "%s" at the tvdb' % ep['series_name'])
        series = self._get_series_from_tvdb(ep['series_name'])
        if not series:
            log.info('Couldn\'t find it, sorry')
            return ep
        log.info('Found it!')

        ep['series_name'] = series.data['seriesname']
        tvdb_ep = None
        try:
            tvdb_ep = series[ep['season_num']][ep['ep_num']]
        except (tvdb_api.tvdb_episodenotfound,tvdb_api.tvdb_seasonnotfound) as e:
            #swallow it, bitch
            pass
        if tvdb_ep:
            #fully parsed episode coming up
            ep.tvdb_ep = tvdb_ep
            self.found_at_tvdb[ep.path] = ep
        return ep
        
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
        direponeup = Episode(unicode(directory))
        direponeup = self.parse_episode(direponeup)
        ep.safe_update(direponeup)
        if ep.is_fully_parsed(): return ep

        #initiate stage two
        directory,filename = os.path.split(directory)
        direptwoup = Episode(unicode(directory))
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
        ep = ep.clean_ep()
        if os.path.isfile(ep.path) and ep.is_fully_parsed():
            self.parsed_eps[ep.path] = ep
        elif os.path.isdir(ep.path) and ep.is_fully_parsed():
            self.single_ep_dirs[ep.path] = ep
        elif os.path.isfile(ep.path):
            self.unparsed_eps[ep.path] = ep

    #def fill_from_tv_db(self, ep):
        


#these functions belong to the world

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
        
