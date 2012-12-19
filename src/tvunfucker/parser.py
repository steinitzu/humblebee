#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, re
from collections import OrderedDict

from . import  tvregexes, util
import tvunfucker

log = tvunfucker.log

def ez_parse_episode(path):
    """
    parse_episode(absolute path) -> dict\n
    Parses only the episode's filename.    
    """
    log.info('Parsing path: %s', path)
    result = LocalEpisode(path)
    directory,filename = os.path.split(path)
    if os.path.isfile(path):
        filename = os.path.splitext(filename)[0]
    match = None
    for regex in tvregexes.tv_regexes:
        match  = re.match(regex.pattern,filename)
        if match:
            result['which_regex'] = regex.alias
            break
    if not match:
        return result #I'm out
    result.safe_update(match.groupdict())
    return result

def _merge_episodes(eps, path_to_ep, backup_series_title=None):
    """
    Accepts a sequence of LocalEpisode objects.\n    
    Merges their data into one LocalEpisode object
    and returns it.\n
    Also takes path_to_ep, which should be a path to the actual episode file
    in question.\n
    Also takes a backup_series_title which can be a string,
    in case no series name data is available in any of the eps.
    """
    log.debug(eps)
    log.debug(path_to_ep)
    resultep = LocalEpisode(path_to_ep)
    for ep in eps:
        resultep.safe_update(ep)
    if resultep.is_fully_parsed:
        return resultep
    if not resultep['series_title']:
        resultep['series_title'] = backup_series_title
    return resultep

def reverse_parse_episode(path, source):
    #TODO: update this docstring
    """
    Takes a path to an episode and a tv source directory.\n
    Starts by parsing the name one dir up from path.\n
    If that directory contains a season_num but not a series_title,
    it will be assumed that two dirs up from path is the series name (as long as that
    doesn't match any regex).\n
    For example,\n
        if path is: '/media/tv/breaking bad/season 2/episode 4.avi'\n
        and source is: '/media/tv'\n
        then the result will be a LocalEpisode with the following:\n
        {'series_title' : 'breaking bad', 'season_num':2, 'ep_num':4}\n

    If the episode file is in the root of source and can't be parsed by any
    regex it will< remain unparsed.
    """

    #get ONE fully parsed episode (series_title, ep_num, season_num)

    #step 1
    #parse directory one up from path, get a LocalEpisode object

    #step 2
    #parse directory two up from path, get a LocalEpisode object

    #step3
    #merge all 3 LocalEpisode objects into one ep and return it

    ep = ez_parse_episode(path)

    one_up_dir = os.path.dirname(path)
    if os.path.samefile(one_up_dir, source):
        #we reached the source, nothing to see here
        return ep
    one_up_ep = ez_parse_episode(one_up_dir)

    two_up_dir = os.path.dirname(one_up_dir)
    if os.path.samefile(two_up_dir, source):
        return _merge_episodes((ep, one_up_ep), path)
    two_up_ep = ez_parse_episode(two_up_dir)

    return _merge_episodes(
        (ep,one_up_ep,two_up_ep),
        path,
        backup_series_title=os.path.split(two_up_dir)[1]
        )
    
    

class LocalEpisode(OrderedDict):
    """
    keys\n
    --------\n
    season_num: the season number (int)\n
    series_title: the series name (string(unicode))\n
    ep_num: episode number (int)\n
    extra_ep_num: for 2 parter episodes\n
    extra_info: some extra gunk from the filename\n
    release_group: the media (scene) release group\n
    which_regex: which regex parsed this filename\n
    path: absolute path to the episode object\n
    tvdb_ep: Episode object from the tvdb_api\n    
    """
    preset_keys = (
        'id',
        'created_at',
        'modified_at',
        'title',
        'ep_number',
        'extra_ep_number',
        'ep_summary',
        'air_date',
        'file_path',
        'season_id',
        'season_number',
        'series_id',
        'series_title',
        'series_summary',
        'series_start_date',
        'run_time_minutes',
        'network',
        #parser keys
        'release_group',
        'which_regex',
        'extra_info',
        )
    numeric_keys = (
        'id',
        'ep_number',
        'extra_ep_number',
        'season_id',
        'season_number',
        'series_id',
        'run_time_minutes'
        )
    
    def __init__(self, path):
        path = util.ensure_utf8(path)
        super(LocalEpisode, self).__init__()
        for key in self.preset_keys:
            super(LocalEpisode, self).__setitem__(
                key, None
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
        Will throw key exceptions if self is not a good ep dict.    
        """
        return self['series_title'] and self['season_num'] is not None and self['ep_num'] is not None

    def clean_name(self, name):
        #TODO: find junk
        """
        Strips all kinds of junk from a name.
        """
        junk = tvregexes.junk
        if name is None: return None
        name = re.sub(junk, ' ', name)
        name = name.strip()
        name = name.title()
        return name

    def __setitem__(self, key, value):
        """
        Introducing some type safety and stuff to this dict.\n
        Will implicitly convert any value put in 
        a key in numerics to int.\n
        """
        if key not in self.preset_keys:
            raise KeyError(
                '''\'%s\' is not a valid key for a LocalEpisode.
                \nValid keys are: %s''' % (key, self.preset_keys))
        def set_val(val):
            #really set the value to key
            super(LocalEpisode, self).__setitem__(key, val)

        if key in self.numeric_keys and value is not None:
            #will raise an error if value is not a valid number
            return set_val(int(value))
        #strings
        if isinstance(value, basestring):
            if value == '' or value is None:
                return set_val(None)
            return set_val(util.ensure_utf8(value))
        return set_val(value)
