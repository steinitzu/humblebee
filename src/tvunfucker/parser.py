#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os, re
from collections import OrderedDict

from . import  tvregexes, util, dbguy
import tvunfucker

log = tvunfucker.log

def ez_parse_episode(path):
    """
    parse_episode(absolute path) -> dict\n
    Parses only the episode's filename.    
    """
    log.info('Parsing path: %s', path)
    result = dbguy.Episode(path)
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
    Accepts a sequence of Episode objects.\n    
    Merges their data into one Episode object
    and returns it.\n
    Also takes path_to_ep, which should be a path to the actual episode file
    in question.\n
    Also takes a backup_series_title which can be a string,
    in case no series name data is available in any of the eps.
    """
    log.debug(eps)
    log.debug(path_to_ep)
    resultep = dbguy.Episode(path_to_ep)
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
        then the result will be a Episode with the following:\n
        {'series_title' : 'breaking bad', 'season_num':2, 'ep_num':4}\n

    If the episode file is in the root of source and can't be parsed by any
    regex it will< remain unparsed.
    """

    #get ONE fully parsed episode (series_title, ep_num, season_num)

    #step 1
    #parse directory one up from path, get a Episode object

    #step 2
    #parse directory two up from path, get a Episode object

    #step3
    #merge all 3 Episode objects into one ep and return it

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
    
    

