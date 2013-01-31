#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os, re, logging

from . import  tvregexes, dbguy
from .texceptions import InvalidArgumentError
from .util import components, split_root_dir
from . import __pkgname__

log = logging.getLogger(__pkgname__)

def is_dvdrip(ep=None, path=None, root_dir=''):
    if ep:
        p = ep.path('rel').lower()
    elif path:
        p = split_root_dir(path, root_dir)[1].lower()
    else:
        raise InvalidArgumentError(
            'Either `ep` or `path` argument must be provided.'
            )
    return 'dvdrip' in p or 'dvd rip' in p

def base_parse_episode(path, root_dir=''):
    """
    parse_episode(absolute path, root_dir='') -> Episode
    Run top most filename of given path through a series of 
    regular expressions attempting to match 
    a series_title and episode and season numbers.
    
    Will also check the full `path`, excluding `root_dir` for 
    instances of 'dvdrip' to determine whether the episode is a dvdrip or not.
    If true, the resulting Episode's `dvdrip` attribute is set to True.
    """
    log.info('Parsing path: %s', path)
    result = dbguy.Episode(path, root_dir)
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
    result.dvdrip = is_dvdrip(result)
    return result

def _merge_episodes(eps, path_to_ep, root_dir, fallback_series_title=None):
    """
    Accepts a sequence of Episode objects.\n    
    Merges their data into one Episode object
    and returns it.\n
    Also takes path_to_ep, which should be a path to the actual episode file
    in question.\n
    Also takes a fallback_series_title which can be a string,
    in case no series name data is available in any of the eps.
    """
    log.debug(eps)
    log.debug(path_to_ep)
    resultep = dbguy.Episode(path_to_ep, root_dir)
    for ep in eps:
        resultep.safe_update(ep)
    if resultep.is_fully_parsed:
        return resultep
    if not resultep['series_title']:
        resultep['series_title'] = fallback_series_title
    return resultep

def reverse_parse_episode(path, sourcedir):
    """
    assume bottom level filename has wrong info, start from the top.
    emergencies only
    """
    #get the path below sourcedir
    ep = base_parse_episode(path, sourcedir)
    abs = ep.path()
    relp = ep.path('rel')
    #relp = os.path.relpath(path, sourcedir)
    log.debug('abspath: %s', abs)
    log.debug('relpath: %s', relp)
    splitted = components(relp)
    if len(splitted) >= 3:
        ep['series_title'] = splitted[-3]
    if len(splitted) >=2:
        sep = base_parse_episode(splitted[-2], sourcedir)
    else:
        return base_parse_episode(splitted[-1], sourcedir)
    eep = base_parse_episode(splitted[-1], sourcedir)
    ep =  _merge_episodes([ep, sep, eep], path, sourcedir)
    ep.dvdrip = is_dvdrip(ep)
    return ep
