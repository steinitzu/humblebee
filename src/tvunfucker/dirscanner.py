#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from glob import glob

from . import parser
from .parser import ez_parse_episode
from . import appconfig as cfg
from logger import log
from .texceptions import InvalidArgumentError

FILE_EXTENSIONS = cfg.get('scanner', 'match-extensions').split(',')

#TODO: use os.walk, symlinks and whatnot

def _get_sub_directories(dir_):
    """
    A generator functions which yields first level sub
    directories in the given dir_.\n
    Ignores dirs in ignored_dirs.\n
    yields absolute paths.
    """
    for name in os.listdir(dir_):
        abspath = os.path.join(dir_,name)
        if not os.path.isdir(abspath):
            continue
        if name in cfg.get('scanner', 'ignored-dirs').split(','):            
            log.info('ignored dir in ignore list \'%s\'' % abspath)
            continue
        yield abspath

def _is_video_file(fn):
    topfn = os.path.split(fn)[1]
    if not os.path.isfile(fn):
        return False
    elif  topfn in cfg.get('scanner', 'ignored-files').split(','):    
        return False
    elif not os.path.splitext(fn)[1] in FILE_EXTENSIONS:
        return False    
    else:
        return True

def _get_video_files(dir_):
    """
    Generator function. Yields video files in given dir_\n
    yields absolute paths
    """
    for name in os.listdir(dir_):
        abspath = os.path.join(dir_,name)
        if not _is_video_file(abspath):
            continue
        yield abspath


def dir_is_single_ep(dir_):
    """
    str path -> bool
    """
    ep = parser.ez_parse_episode(dir_)
    return ep.is_fully_parsed()


def get_file_from_single_ep_dir(dir_):
    """
    Finds the media file in a given single episode directory.
    Returns a path.
    If no media file is found it returns the directory it self.    
    """    
    log.debug('Checking single ep dir: %s', dir_)
    vfiles = [f for f in _get_video_files(dir_)]
    if len(vfiles) == 1:
        log.debug('One media file found: %s', vfiles[0])
        return vfiles[0]
    elif len(vfiles) == 0:
        log.debug('No media file found in dir: %s. Returning dirname', dir_)
        return dir_
    #do something when more than 1 file in the dir
    log.debug('There was more than one media file in dir: %s', dir_)
    for f in vfiles:
        fname = os.path.split(f)[1]
        #TODO: What if 'sample' is in the ep title or something?
        if 'sample' in fname.lower():
            continue
        else:
            return f


def is_rar(path):
    """
    is_rar(path) -> bool
    Checks whether given path contains a scene style 
    rarred episode (e.g. *.r01, *.r02,...)
    """  
    rnumfiles = glob(
        os.path.join(path, '*.r[0-9][0-9]')
        )
    if rnumfiles: return True
    else: return False
        

def get_episodes(dir_):
    if not os.path.isdir(dir_):
        raise InvalidArgumentError(
            '\'%s\' is not a valid directory.' % dir_
            )
    for dirpath, dirnames, filenames in os.walk(dir_):
        for subdir in dirnames:
            subdir = os.path.join(dirpath, subdir)
            if dir_is_single_ep(subdir):
                ret = get_file_from_single_ep_dir(subdir)
                log.info('Found episode: %s', ret)                
                yield ez_parse_episode(ret)
        for fn in filenames:
            fn = os.path.join(dirpath, fn)
            if _is_video_file(fn):
                yield ez_parse_episode(fn)            
            else:
                continue
