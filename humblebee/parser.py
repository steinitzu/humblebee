#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os, re, logging
from collections import OrderedDict

from . import  tvregexes, util, dbguy
from .util import components
from . import __pkgname__

log = logging.getLogger(__pkgname__)

def base_parse_episode(path, root_dir=''):
    """
    parse_episode(absolute path, root_dir='') -> dict\n
    Parses only the episode's filename.    
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
    return result

def _merge_episodes(eps, path_to_ep, root_dir, backup_series_title=None):
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
    resultep = dbguy.Episode(path_to_ep, root_dir)
    for ep in eps:
        resultep.safe_update(ep)
    if resultep.is_fully_parsed:
        return resultep
    if not resultep['series_title']:
        resultep['series_title'] = backup_series_title
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
    return _merge_episodes([ep, sep, eep], path, sourcedir)

    
